from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context, RequestContext, loader
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.core.mail import send_mail
from django.views import i18n

from Pootle.web import webforms
from Pootle.web.models import Project, Language, TranslationProject, Store
from Pootle.utils.convert import convert_translation_store
from Pootle.compat import forms as pootleforms 
from Pootle.compat import pootleauth
from Pootle.compat.authforms import RegistrationManipulator, ActivationManipulator
from Pootle.conf import instance, potree
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
import random
from cStringIO import StringIO

from Pootle.web.models import Language, Project

from Pootle import __version__ as pootleversion
from translate import __version__ as toolkitversion

def set_language(req):
    """Sets proper language code for internationalization and returns True if 
    language code was changed."""
    if req.LANGUAGE_CODE == req.POST.get('language', None):
        return False
    req.GET._mutable = True
    req.GET['language'] = req.POST.get('language', None)
    i18n.set_language(req)
    return True

def robots(req):
    return HttpResponse(content=generaterobotsfile(["login.html", "register.html", "activate.html"]), mimetype="text/plain")

def index(req, what=None):
    if req.GET:
        if 'islogout' in req.GET:
            next_page = req.GET.get('next_page','/')
            from django.contrib.auth import logout as djangologout
            djangologout(req)
            return HttpResponseRedirect(next_page)

    if what == 'languages':
        context = {
            'languages': Language.objects.all(),
            }
    elif what == 'projects':
        context = {
            'projects': Project.objects.all(),
            }
    else:
        context = {
            'languages': Language.objects.all(),
            'projects': Project.objects.all(),
            }
    return render_to_response("index.html", RequestContext(req, context))
    
def about(req):
    context = { 'pootleversion':pootleversion.ver, 'toolkitversion':toolkitversion.ver }
    return render_to_response("about.html", RequestContext(req, context ))

def project(req, project):
    p = get_object_or_404(Project, code=project)
    languages = TranslationProject.objects.filter(project=p)
    if req.user.is_authenticated():
        start_translating = [ i for i in req.user.get_profile().languages.all() if i not in 
            [ lang.language for lang in languages ]]
    else:
        start_translating = []
    
    if len(languages):
        average_translated = sum([x.stats[2] for x in languages])/len(languages)
    else:
        average_translated = 0
    context = {
        'project': p,
        'stats': ngettext(  "%(count)d language, average %(average)d%% translated",
                            "%(count)d languages, average %(average)d%% translated", 
                            len(languages)) % { 
                                'count': len(languages),
                                'average': average_translated,
                                },
        'languages': languages,
        'starttranslating': start_translating,
        }
    return render_to_response("project.html", RequestContext(req, context))

def project_start(req, project, language):
    if settings.REQUIRE_NEW_PROJECT_APPROVAL:
        context = { 'message': _("This site requires administrator approval when creating new translation projects. When your translation project is approved, you will be notified by email.") }
    else:
        try:
            p = Project.objects.get(code=project)
            lang = Language.objects.get(code=language)
        except Project.DoesNotExist:
            pass
        except Language.DoesNotExist:
            pass
        else:
            newproject = TranslationProject(project=p, language=lang)
            newproject.save()
            # FIXME join req.user to group as admin
            return HttpResponseRedirect("/%s/%s/" % (language, project) )
        context = { 'message': _("Creating new project has failed.") }
    return render_to_response("project_start.html", RequestContext(req, context))

def language(req, language):
    lang = get_object_or_404(Language, code=language)
    projects = TranslationProject.objects.filter(language=lang)

    if len(projects):
        average_translated = sum([x.stats[2] for x in projects])/len(projects)
    else:
        average_translated = 0
    context = {
        "language": lang,
        "stats": ngettext(  "%(count)d project, average %(average)d%% translated",
                            "%(count)d projects, average %(average)d%% translated", 
                            len(projects)) % { 
                                'count': len(projects),
                                'average': average_translated,
                                },
        "projects": projects,
        }
    return render_to_response("language.html", RequestContext(req, context))
    
def translationproject(req, language, project, subdir=None):
    p = get_object_or_404(TranslationProject, language__code=language, project__code=project)
    
    files = p.list_dir(subdir)
    numfiles = len(files)
    try:
        average_translated = int(sum([f.translatedstrings for f in files])/float(numfiles))
    except ZeroDivisionError:
        average_translated = 0

    context = {
        'project': p,
        'stats': ngettext(  "%(count)d file, average %(average)d%% translated",
                            "%(count)d files, average %(average)d%% translated",
                            numfiles) % {
                                'count': numfiles,
                                'average': average_translated,
                                },
        'items': files,
       }
    return render_to_response("translationproject.html", RequestContext(req, context))

def options(req):
    manipulator = webforms.UserProfileManipulator(req.user)
    if req.POST:
        new_data = req.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)
            manipulator.save(new_data)
            return HttpResponseRedirect(req.path)
    else:
        errors = {}
        new_data = manipulator.old_data()
    form = forms.FormWrapper(manipulator, new_data, errors)
    context = { 'form' : form, 'errors': errors }
    return render_to_response("options.html", RequestContext(req, context))

def login(req):
    message = None
    redirect_to = req.REQUEST.get(REDIRECT_FIELD_NAME, '')
    manipulator = AuthenticationForm(req)
    new_data = {}
    if not redirect_to or '://' in redirect_to or ' ' in redirect_to:
        redirect_to = '/'

    if req.user.is_authenticated():
        return HttpResponseRedirect(redirect_to)
    else:
        if req.POST:
            # do login here
            errors = manipulator.get_validation_errors(req.POST)
            locale_changed = set_language(req)
            if not errors:
                from django.contrib.auth import login
                login(req, manipulator.get_user())
                req.session.delete_test_cookie()
                return HttpResponseRedirect(redirect_to) 
            if locale_changed:
                # redirect back to login, but in new language
                return HttpResponseRedirect(req.path)
            new_data = req.POST.copy()
            del(new_data['password'])
        else:
            errors = {}
        req.session.set_test_cookie()
        
        form = forms.FormWrapper(manipulator, new_data, errors)
        context = { 
            'languages': settings.LANGUAGES,
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
    manipulator = ActivationManipulator()
    context = {}
    if 'activationcode' in req.REQUEST and 'username' in req.REQUEST:
        # FIXME: validation
        errors = manipulator.get_validation_errors(req.REQUEST)
        if not errors:
            if manipulator.save(req.REQUEST):
                context = { 'activationmessage': _("Your account has been activated!"), }

    if 'username' in req.REQUEST:
        new_data = {'username': req.REQUEST['username']} 
    else:
        new_data = {}
    errors = {}
    
    form = forms.FormWrapper(manipulator, new_data, errors)
    context['form'] = form
    return render_to_response("activate.html", RequestContext(req, context))

# adminpages.py

def projectadmin(req, project): # FIXME
    argdict = {}
    return render_to_pootleresponse(adminpages.ProjectAdminPage(potree(), project, pootlesession(req), argdict))
    
def admin(req):
    manipulator = pootleforms.SiteOptionsManipulator()
    if req.POST and req.user.is_superuser():
        new_data = req.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)
            manipulator.save(new_data)
            return HttpResponseRedirect(req.path)
    else:
        errors = {}
        new_data = manipulator.old_data()
    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response("adminindex.html", RequestContext(req, { 'form': form, 'errors': errors } ))

def admin_useredit(req, user):
    manipulator = webforms.UserAdminManipulator(user)
    if req.POST and req.user.is_superuser:
        new_data = req.POST.copy()
        new_data['username'] = user
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)
            manipulator.save(new_data)
            return HttpResponseRedirect('/'.join(req.path.split("/")[:-2]) + '/')
    else:
        errors = {}
        new_data = manipulator.old_data()
    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response("admin_useredit.html", RequestContext(req, { 'form': form, 'u': user, 'errors':errors} ))

def admin_users(req):
    if req.POST and req.user.is_superuser:
        selected = [ u for u in User.objects.all() if "select-%s" % u.username in req.POST]
        if 'delete-selected' in req.POST:
            for u in selected:
                u.delete()
    
    return render_to_response("admin_users.html", RequestContext(req, { 'users': User.objects.all() } ))

def admin_languages(req):
    error = None
    if req.POST:
        if req.user.is_superuser:
            for lang in Language.unfiltered.all():
                lang.enabled = lang.code in req.POST
                lang.save()
        else:   
            error = _("You do not have sufficient rights.")
    context = { 
        'languages': Language.unfiltered.all(), 
        'error':error, 
        'selected': [ lang.code for lang in Language.unfiltered.all()] }
    return render_to_response("admin_languages.html", RequestContext(req, context))

def admin_projects(req):
    error = None
    if req.POST: 
        if req.user.is_superuser:
            for project in Project.objects.all():
                if project.code in req.POST:
                    # FIXME do something 
                    pass
        else:
            error = _("You do not have sufficient rights.")
    context = { 
        'error': error,
        'projects' : Project.objects.all() }
    return render_to_response("admin_projects.html", RequestContext(req, context))

def admin_projectedit(req, project):
    p = get_object_or_404(Project, code=project)
    manipulator = webforms.ProjectAdminManipulator(p)
    if req.POST:
        if req.user.is_superuser:
            new_data = req.POST.copy()
            errors = manipulator.get_validation_errors(new_data)
            if not errors:
                manipulator.do_html2python(new_data)
                manipulator.save(new_data)
                return HttpResponseRedirect('/'.join(req.path.split("/")[:-2]) + '/')
    else:
        errors = {}
        new_data = manipulator.old_data()
    form = forms.FormWrapper(manipulator, new_data, errors)
    context = { 'project' : Project.objects.get(code=project),
                'form': form,
                'errors': errors,}
    return render_to_response("admin_projectedit.html", RequestContext(req, context))

def admintranslationproject(req, language, project): # FIXME
    if req.POST and req.user.is_superuser():
        pass
    argdict = {}
    project_obj = potree().getproject(language, project)
    return render_to_pootleresponse(adminpages.TranslationProjectAdminPage(potree(), project_obj, pootlesession(req), argdict))

def translate(req, language, project, subdir, filename):
    translationproject = TranslationProject.objects.get(project__code=project, language__code=language)
    file = translationproject.podir / (subdir + filename)
    
    errors = {}
    if req.POST:
        if req.POST.has_key('id'):
            try:
                id = int(req.POST['id'])
            except ValueError:
                return HttpResponseRedirect(req.path)
            num, unit = file.filter([], id)
            manipulator = webforms.TranslationManipulator(unit)

            new_data = req.POST.copy()
            errors = manipulator.get_validation_errors(new_data)
            if not errors:
                manipulator.do_html2python(new_data)
                unit.target = new_data['translation']
                print unit.__repr__()
                return HttpResponseRedirect("%s?id=%d" % (req.path, int(req.POST['id'])+1))
    try:
        stringnumber = int(req['id'])
    except ValueError:
        stringnumber = 0
    except KeyError:
        stringnumber = 0

    stringnumber, unit = file.filter([], stringnumber)

    print "This", unit.__repr__()
    manipulator = webforms.TranslationManipulator()
    new_data = { 
        'translation': unit.target,
        'id': stringnumber
        } 
    form = forms.FormWrapper(manipulator, new_data, errors)

    context = {
        'form' : form,
        'originalstring': unit.source,
        'stringnumber': stringnumber,
        }
    return render_to_response("translate.html", RequestContext(req, context))

def downloadfile(req, project, language, subdir, filename):
    format = req.GET.get('format', 'po')
    translationproject = TranslationProject.objects.get(project__code=project, language__code=language)
    buffer = StringIO()
    f = Store.objects.get(name=filename)
    buffer.write(f.dump_to_postring().encode("utf-8"))
    buffer.seek(0)
    contents = convert_translation_store(buffer, format)
    buffer.close()    
    return HttpResponse(contents,mimetype="text/plain")

# spellui.py

def spellcheck(req):
    return render_to_pootleresponse(spellui.SpellingReview(pootlesession(req), argdict={}, js_url="/js/spellui.js"))

def spellingstandby(req):
    return render_to_pootleresponse(spellui.SpellingStandby())


def test(req):
    tests = []
    ta = tests.append
    # Pootle.compat.pootleauth
    ta(("<b>Pootle.compat.pootleauth</b>",))
    # user created
    testuser = pootleauth.create_user('testuser','test@example.com')
    ta(('user created', pootleauth.get_user('testuser') == testuser._user))
    # password set
    testuser.set_password('testpassword')
    try: t = testuser.check_password('testpassword')
    except: t = False
    ta(('password set', t))
    # user authenticated
    pa = pootleauth.PootleAuth()
    u = pa.authenticate('testuser', 'testpassword')
    ta(('user authenticated', u != None and type(u) == type(pootleauth.UserWrapper(testuser._user,'testuser'))))
    # is_authenticated is true
    ta(('is_authenticated is true', testuser.is_authenticated() == True))
    # is_anonymous is false
    ta(('is_anonymous is false', testuser.is_anonymous() == False))
    # is_active is false
    ta(('is_active is false', testuser.is_active() == False))
    # activate 
    testuser.activate()
    ta(('activate', testuser.is_active() == True))
    # is_superuser is false
    ta(('is_superuser is false', testuser.is_superuser() == False))
    # user deleted
    testuser.delete()
    pootleauth.save_users()
    ta( ('user deleted', pootleauth.get_user('testuser') == None))


    return render_to_response("test.html", RequestContext(req, {'tests': tests}))
