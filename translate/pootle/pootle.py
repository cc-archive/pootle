#!/usr/bin/env python

from jToolkit.web import server
from jToolkit.web import session
from jToolkit import prefs
from jToolkit.widgets import widgets
from jToolkit import mailer
from translate.pootle import indexpage
from translate.pootle import translatepage
from translate.pootle import pagelayout
from translate.pootle import projects
from translate.pootle import users
import sys
import os
import random

class PootleServer(users.OptionalLoginAppServer):
  """the Server that serves the Pootle Pages"""
  def __init__(self, instance, sessioncache=None, errorhandler=None, loginpageclass=users.LoginPage):
    if sessioncache is None:
      sessioncache = session.SessionCache(sessionclass=users.ActivateSession)
    super(PootleServer, self).__init__(instance, sessioncache, errorhandler, loginpageclass)
    self.potree = projects.POTree(self.instance)
    # these are for pootle UI localization
    if not self.languagenames:
      self.languagenames = None

  def saveuserprefs(self, users):
    """saves changed preferences back to disk"""
    # TODO: this is a hack, fix it up nicely :-)
    prefsfile = users.__root__.__dict__["_setvalue"].im_self
    prefsfile.savefile()

  def refreshstats(self):
    """refreshes all the available statistics..."""
    self.potree.refreshstats()

  def generateactivationcode(self):
    """generates a unique activation code"""
    return "".join(["%02x" % int(random.random()*0x100) for i in range(16)])

  def getpage(self, pathwords, session, argdict):
    """return a page that will be sent to the user"""
    # TODO: strip off the initial path properly
    while pathwords and pathwords[0] == "pootle":
      pathwords = pathwords[1:]
    if pathwords:
      top = pathwords[0]
    else:
      top = ""
    if not top or top == "index.html":
      return indexpage.PootleIndex(self.potree, session)
    elif top == 'res.html':
      from jLogbook.python import configpage
      return configpage.ResourcePage(self, session)
    elif top == "login.html":
      if session.isopen:
        redirecttext = pagelayout.IntroText("Redirecting to index...")
        redirectpage = pagelayout.PootlePage("Redirecting to index...", redirecttext, session)
        return server.Redirect("index.html", withpage=redirectpage)
      if 'username' in argdict:
        session.username = argdict["username"]
      return users.LoginPage(session, languagenames=self.languagenames)
    elif top == "register.html":
      return self.registerpage(session, argdict)
    elif top == "activate.html":
      return self.activatepage(session, argdict)
    elif top == "projects":
      pathwords = pathwords[1:]
      if pathwords:
        top = pathwords[0]
      else:
        top = ""
      if not top or top == "index.html":
        return indexpage.ProjectsIndex(self.potree, session)
      else:
        projectcode = top
        pathwords = pathwords[1:]
        if pathwords:
          top = pathwords[0]
        else:
          top = ""
        if not top or top == "index.html":
          return indexpage.ProjectLanguageIndex(self.potree, projectcode, session)
    elif self.potree.haslanguage(top):
      languagecode = top
      pathwords = pathwords[1:]
      if pathwords:
        top = pathwords[0]
	bottom = pathwords[-1]
      else:
        top = ""
	bottom = ""
      if not top or top == "index.html":
        return indexpage.LanguageIndex(self.potree, languagecode, session)
      if self.potree.hasproject(languagecode, top):
        projectcode = top
        project = self.potree.getproject(languagecode, projectcode)
        pathwords = pathwords[1:]
        if pathwords:
          top = pathwords[0]
        else:
          top = ""
        if not top or top == "index.html":
	  return indexpage.ProjectIndex(project, session, argdict)
	elif bottom == "translate.html":
	  if len(pathwords) > 1:
            dirfilter = os.path.join(*pathwords[:-1])
	  else:
	    dirfilter = ""
          try:
            return translatepage.TranslatePage(project, session, argdict, dirfilter)
          except (StopIteration, projects.RightsError), stoppedby:
            argdict["message"] = str(stoppedby)
            return indexpage.ProjectIndex(project, session, argdict, dirfilter)
	elif bottom.endswith(".po"):
	  pofilename = os.path.join(*pathwords)
	  if argdict.get("translate", 0):
            try:
              return translatepage.TranslatePage(project, session, argdict, dirfilter=pofilename)
            except (StopIteration, projects.RightsError), stoppedby:
              argdict["message"] = str(stoppedby)
              return indexpage.ProjectIndex(project, session, argdict, dirfilter=pofilename)
	  elif argdict.get("index", 0):
            return indexpage.ProjectIndex(project, session, argdict, dirfilter=pofilename)
	  else:
	    contents = project.getsource(pofilename)
	    page = widgets.PlainContents(contents)
	    page.content_type = "text/plain"
	    return page
	elif bottom.endswith(".csv"):
	  csvfilename = os.path.join(*pathwords)
	  contents = project.getcsv(csvfilename)
	  page = widgets.PlainContents(contents)
	  page.content_type = "text/plain"
	  return page
	elif bottom == "index.html":
          if len(pathwords) > 1:
            dirfilter = os.path.join(*pathwords[:-1])
          else:
            dirfilter = None
	  return indexpage.ProjectIndex(project, session, argdict, dirfilter)
	else:
	  return indexpage.ProjectIndex(project, session, argdict, os.path.join(*pathwords))
    return None

  def handleregistration(self, session, argdict):
    """handles the actual registration"""
    supportaddress = getattr(self.instance.registration, 'supportaddress', "")
    username = argdict.get("username", "")
    if not username or not username.isalnum() or not username[0].isalpha():
      raise users.RegistrationError("Username must be alphanumeric, and must start with an alphabetic character")
    email = argdict.get("email", "")
    password = argdict.get("password", "")
    if not (email and "@" in email and "." in email):
      raise users.RegistrationError("You must supply a valid email address")
    userexists = session.loginchecker.userexists(username)
    if userexists:
      usernode = getattr(session.loginchecker.users, username)
      # use the email address on file
      email = getattr(usernode, "email", email)
      password = ""
      # TODO: we can't figure out the password as we only store the md5sum. have a password reset mechanism
      message = "You (or someone else) attempted to register an account with your username.\n"
      message += "We don't store your actual password but only a hash of it\n"
      if supportaddress:
        message += "If you have a problem with registration, please contact %s\n" % supportaddress
      else:
        message += "If you have a problem with registration, please contact the site administrator\n"
      displaymessage = "That username already exists. An email will be sent to the registered email address...\n"
      redirecturl = "login.html?username=%s" % username
      displaymessage += "Proceeding to <a href='%s'>login</a>\n" % redirecturl
    else:
      minpasswordlen = 6
      if not password or len(password) < minpasswordlen:
        raise users.RegistrationError("You must supply a valid password of at least %d characters" % minpasswordlen)
      setattr(session.loginchecker.users, username + ".email", email)
      setattr(session.loginchecker.users, username + ".passwdhash", session.md5hexdigest(password))
      setattr(session.loginchecker.users, username + ".activated", 0)
      activationcode = self.generateactivationcode()
      setattr(session.loginchecker.users, username + ".activationcode", activationcode)
      activationlink = ""
      message = "A Pootle account has been created for you using this email address\n"
      if session.instance.baseurl.startswith("http://"):
        message += "To activate your account, follow this link:\n"
        activationlink = session.instance.baseurl
        if not activationlink.endswith("/"):
          activationlink += "/"
        activationlink += "activate.html?username=%s&activationcode=%s" % (username, activationcode)
        message += "  %s  \n" % activationlink
      message += "Your activation code is:\n%s\n" % activationcode
      if activationlink:
        message += "If you are unable to follow the link, please enter the above code at the activation page\n"
      message += "This message is sent to verify that the email address is in fact correct. If you did not want to register an account, you may simply ignore the message.\n"
      redirecturl = "activate.html?username=%s" % username
      displaymessage = "Account created. You will be emailed login details and an activation code. Please enter your activation code on the <a href='%s'>activation page</a>. " % redirecturl
      if activationlink:
        displaymessage += "(Or simply click on the activation link in the email)"
    self.saveuserprefs(session.loginchecker.users)
    message += "Your user name is: %s\n" % username
    if password.strip():
      message += "Your password is: %s\n" % password
    message += "Your registered email address is: %s\n" % email
    smtpserver = self.instance.registration.smtpserver
    fromaddress = self.instance.registration.fromaddress
    messagedict = {"from": fromaddress, "to": [email], "subject": "Pootle Registration", "body": message}
    if supportaddress:
      messagedict["reply-to"] = supportaddress
    fullmessage = mailer.makemessage(messagedict)
    errmsg = mailer.dosendmessage(fromemail=self.instance.registration.fromaddress, recipientemails=[email], message=fullmessage, smtpserver=smtpserver)
    if errmsg:
      raise users.RegistrationError("Error sending mail: %s" % errmsg)
    return displaymessage, redirecturl

  def registerpage(self, session, argdict):
    """handle registration or return the Register page"""
    if "username" in argdict:
      try:
        displaymessage, redirecturl = self.handleregistration(session, argdict)
      except users.RegistrationError, message:
        session.status = str(message)
        return users.RegisterPage(session, argdict)
      message = pagelayout.IntroText(displaymessage)
      redirectpage = pagelayout.PootlePage("Redirecting...", [message], session)
      redirectpage.attribs["refresh"] = 10
      redirectpage.attribs["refreshurl"] = redirecturl
      return redirectpage
    else:
      return users.RegisterPage(session, argdict)

  def activatepage(self, session, argdict):
    """handle activation or return the Register page"""
    if "username" in argdict and "activationcode" in argdict:
      username = argdict["username"]
      activationcode = argdict["activationcode"]
      usernode = getattr(session.loginchecker.users, username, None)
      if usernode is not None:
        correctcode = getattr(usernode, "activationcode", "")
        if correctcode and correctcode.strip().lower() == activationcode.strip().lower():
          setattr(usernode, "activated", 1)
          self.saveuserprefs(session.loginchecker.users)
          redirecttext = pagelayout.IntroText("Your account has been activated! Redirecting to login...")
          redirectpage = pagelayout.PootlePage("Redirecting to login...", redirecttext, session)
          redirectpage.attribs["refresh"] = 10
          redirectpage.attribs["refreshurl"] = "login.html?username=%s" % username
          return redirectpage
      failedtext = pagelayout.IntroText("The activation link you have entered was not valid")
      failedpage = pagelayout.PootlePage("Activation Failed", failedtext, session)
      return failedpage
    else:
      return users.ActivatePage(session, argdict)

def main_is_frozen():
  import imp
  return (hasattr(sys, "frozen") or # new py2exe
          hasattr(sys, "importers") # old py2exe
          or imp.is_frozen("__main__")) # tools/freeze

def main():
  # run the web server
  from jToolkit.web import simplewebserver
  parser = simplewebserver.WebOptionParser()
  if main_is_frozen():
    pootledir = os.path.dirname(sys.executable)
  else:
    pootledir = os.path.abspath(os.path.dirname(__file__))
  prefsfile = os.path.join(pootledir, "pootle.prefs")
  parser.set_default('prefsfile', prefsfile)
  parser.set_default('instance', 'Pootle')
  htmldir = os.path.join(pootledir, "html")
  parser.set_default('htmldir', htmldir)
  parser.add_option('', "--refreshstats", dest="action", action="store_const", const="refreshstats", default="runwebserver", help="refresh the stats files instead of running the webserver")
  options, args = parser.parse_args()
  server = parser.getserver(options)
  if options.action == "runwebserver":
    simplewebserver.run(server, options)
  elif options.action == "refreshstats":
    server.refreshstats()

if __name__ == '__main__':
  main()

