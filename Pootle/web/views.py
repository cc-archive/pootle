from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext, loader
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import render_to_response
from django import forms
from django.core.mail import send_mail

from Pootle.compat.authforms import RegistrationManipulator
from Pootle import indexpage, adminpages, users, translatepage
from Pootle.conf import instance, potree
from Pootle.conf import users as pootleusers
from Pootle.storage_client import generaterobotsfile
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
import random

from Pootle.storage_client import getprojects, getlanguageselector

from Pootle import __version__ as pootleversion
from translate import __version__ as toolkitversion

### backwards compatiblity 
import kid
import os
from jToolkit.xml import DOMOverlay
OLD_TEMPLATEDIR = settings.TEMPLATE_DIRS[0]

class AttrDict(dict):
  """Dictionary that also allows access to keys using attributes"""
  def __getattr__(self, attr, default=None):
    if attr in self:
      return self[attr]
    else:
      return default

# needed for 'buildpage'
def attribify(context):
  """takes a set of nested dictionaries and converts them into AttrDict. Also searches through lists"""
  if isinstance(context, dict) and not isinstance(context, AttrDict):
    newcontext = AttrDict(context)
    for key, value in newcontext.items():
      if isinstance(value, (dict, list)):
        newcontext[key] = attribify(value)
    return newcontext
  elif isinstance(context, list):
    for n, item in enumerate(context):
      if isinstance(item, (dict, list)):
        context[n] = attribify(item)
    return context
  else:
    return context

def loadurl(filename, context):
    "opens a template file and returns contents as string"
    filename = os.path.join(OLD_TEMPLATEDIR, filename+os.extsep+"html")
    if os.path.exists(filename):
        return open(filename, "r").read()
    return None
    
def buildpage(source, context, loadurl=loadurl, localize=None, innerid=None):
    #(self, source, context, loadurl=None, localize=None, innerid=None):
    if DOMOverlay is not None:
      innerid = context.pop("@innerid", None)
      if loadurl is None:
        loadurl = DOMOverlay.loadurl
      domoverlay = DOMOverlay.DOMOverlay(source, loadurl, context)
      source = domoverlay.serialise(innerid)
    context = attribify(context)
    t = kid.Template(source=source,**context)
    return t.serialize(output='xhtml')

# the most "important" method for rendering backwards compatible templates
def render_to_pootleresponse(pootlepage):
    templatename = pootlepage.templatename
    template = open(os.path.join(OLD_TEMPLATEDIR, templatename+os.extsep+"html"), "r").read()
    page = buildpage(template, pootlepage.templatevars or {})
    return HttpResponse(page)

def pootlesession(req):
    """Make a wrapper around Django session object to make it work
    with Pootle's page classes seamlessly."""
    def localize(s, *args):
        if args:
            return _(s) % args
        return s 
    def nlocalize(s, s2, numarg, *args):
        if args: 
            return s % args
        return s
    session = req.session
    session.localize = localize
    session.nlocalize = nlocalize
    session.username = req.user
    session.instance = instance()
    if not req.user.is_authenticated():
        session.status = 'not logged in'
    else:
        session.status = 'logged in as <b>%s</b>' % req.user
    session.isopen = req.user.is_authenticated()
    session.prefs = req.user
    
    # user's projects
    class getprojects:
        def __call__(self):
            userlanguages = getattr(session.prefs, "languages", "")
            return [languagecode.strip() for languagecode in userlanguages.split(',') if languagecode.strip()]
    session.getprojects = getprojects()
    
    def is_admin(req):
        def _inner():
            if not req.user.is_anonymous:
                if req.user.is_authenticated and req.user.is_superuser:
                    return True
            return False
        return _inner
    session.issiteadmin = is_admin(req)

    def getlanguages():
        return []
    session.getlanguages = getlanguages
    
    session.language = 'sl'
    return session

def css(req):
    css = open('/home/hruske/Desktop/pootle/trunk/Pootle/html/pootle.css','r').read()
    return HttpResponse(content=css, mimetype='text/css')

def errorlist_from_errors(errors):
    # FIXME a rather ugly hack just to keep things jtoolkit-friendly
    error_list = []
    for e in errors:
        error_list.extend([ str(a) for a in errors[e]])
    return " ".join(error_list)

    

### end backwards compatibility

def robots(req):
    return HttpResponse(content=generaterobotsfile(["login.html", "register.html", "activate.html"]), mimetype="text/plain")

# indexpage.py
def index(req, what=None):
    if req.GET:
        if 'islogout' in req.GET:
            next_page = req.GET.get('next_page','/')
            from django.contrib.auth import logout as djangologout
            djangologout(req)
            req.session.isopen = False
            return HttpResponseRedirect(next_page)

    if what == 'languages':
        context = {
            'languages': [{"code": code, "name": name } for code, name in potree().getlanguages()],
            }
    elif what == 'projects':
        context = {
            'projects': getprojects(),
            }
    else:
        context = {
            'languages': [{"code": code, "name": name } for code, name in potree().getlanguages()],
            'projects': getprojects(),
            }
    return render_to_response("index.html", RequestContext(req, context))
    
def about(req):
    context = { 'pootleversion':pootleversion.ver, 'toolkitversion':toolkitversion.ver }
    return render_to_response("about.html", RequestContext(req, context ))

def home(req):
    return render_to_pootleresponse(indexpage.UserIndex(potree(), pootlesession(req)))
home = login_required(home)

def projectlanguageindex(req, project):
    return render_to_pootleresponse(indexpage.ProjectLanguageIndex(potree(), project, pootlesession(req)))

def languageindex(req, language):
    return render_to_pootleresponse(indexpage.LanguageIndex(potree(), language, pootlesession(req)))
    
def projectindex(req, language, project):
    # important, handles 4 urls
    argdict = {}

    proj = potree().getproject(language, project)
    return render_to_pootleresponse(indexpage.ProjectIndex(proj, pootlesession(req), argdict, dirfilter=None))

# users.py

def options(req):
    # use manipulator here
    message = None
    if req.POST:
        try:
            if "changeoptions" in req.POST:
                pass
            elif "changepersonal" in req.POST:
                pass
            elif "changeinterface" in req.POST:
                pass
        except users.RegistrationError, errormessage:
            message = errormessage
    return render_to_pootleresponse(users.UserOptions(potree(), pootlesession(req), message))

def login(req):
    message = None
    redirect_to = req.REQUEST.get(REDIRECT_FIELD_NAME, '')
    manipulator = AuthenticationForm(req)
    new_data = {}
    if not redirect_to or '://' in redirect_to or ' ' in redirect_to:
        redirect_to = '/home/'

    if req.user.is_authenticated():
        return HttpResponseRedirect(redirect_to)
    else:
        if req.POST:
            # do login here
            errors = manipulator.get_validation_errors(req.POST)
            if not errors:
                from django.contrib.auth import login
                login(req, manipulator.get_user())
                req.session.delete_test_cookie()
                req.session.isopen = True
                return HttpResponseRedirect(redirect_to) 
            new_data = req.POST.copy()
            del(new_data['password'])
        else:
            errors = {}
        req.session.set_test_cookie()
        
        # we don't want password
        
        form = forms.FormWrapper(manipulator, new_data, errors)
        context = { 
            'languages': getlanguageselector(potree().getlanguages(), pootlesession(req)), # FIXME
            'form': form,
            }
        return render_to_response("login.html", RequestContext(req, context))

# users.py: registration, activation

def register(req):
    message = _("Please enter your registration details")
    manipulator = RegistrationManipulator() 
    if req.POST:
        new_data = req.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if errors:
            message = errorlist_from_errors(errors)
        else:
            manipulator.do_html2python(new_data)
            activation_code = "".join(["%02x" % int(random.random()*0x100) for i in range(16)])
            new_data['activationcode'] = activation_code
            new_user = manipulator.save(new_data)
            
            # and email the activation details
            email_contents = loader.get_template("email_register.txt")
            context = Context({
                'activationlink': '',
                'activationcode': activation_code,
                'username': new_data['username'],
                'password': new_data['password'],
                'email': new_data['email'],
                })
            send_mail("Pootle registration", email_contents.render(context), settings.DEFAULT_FROM_EMAIL, [new_data['email']],
                fail_silently=False)

            return render_to_response("register_sent.html", RequestContext(req))
    else:
        new_data = {}
        errors = {}
    
    form = forms.FormWrapper(manipulator, new_data, errors)
    context = {
        'register_message' : message, 
        'form' : form,
        }
    return render_to_response("register.html", RequestContext(req, context)) 

def activate(req):
    argdict = req.POST.copy()
    return render_to_pootleresponse(users.ActivatePage(pootlesession(req), argdict, title=None, message=None))

# adminpages.py

def projectadmin(req, project):
    argdict = {}
    return render_to_pootleresponse(adminpages.ProjectAdminPage(potree(), project, pootlesession(req), argdict))
    
def admin(req):
    return render_to_pootleresponse(adminpages.AdminPage(potree(), pootlesession(req), instance))

def adminusers(req):
    return render_to_pootleresponse(adminpages.UsersAdminPage(None, pootleusers(), pootlesession(req), instance))

def adminlanguages(req):
    return render_to_pootleresponse(adminpages.LanguagesAdminPage(potree(), pootlesession(req), instance))

def adminprojects(req):
    return render_to_pootleresponse(adminpages.ProjectsAdminPage(potree(), pootlesession(req), instance))

def admintranslationproject(req):
    return render_to_pootleresponse(adminpages.TranslationProjectAdminPage(potree(), project, pootlesession(req), argdict))

# translatepage.py

def translatepage(req):
    # handles 2 urls
    return render_to_pootleresponse(translatepage.TranslatePage(project, pootlesession(req), argdict={}, dirfilter=None))

# spellui.py

def spellcheck(req):
    return render_to_pootleresponse(spellui.SpellingReview(pootlesession(req), argdict={}, js_url="/js/spellui.js"))

def spellingstandby(req):
    return render_to_pootleresponse(spellui.SpellingStandby())

