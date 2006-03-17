#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jToolkit.web import server
from jToolkit.web import session
from jToolkit.widgets import widgets
from jToolkit.widgets import form
from jToolkit.widgets import table
from jToolkit import mailer
from jToolkit import prefs
from Pootle import pagelayout

class RegistrationError(ValueError):
  pass

class LoginPage(pagelayout.PootlePage):
  """wraps the normal login page in a PootlePage layout"""
  def __init__(self, session, languagenames=None):
    self.languagenames = languagenames
    pagetitle = session.localize("Login to Pootle")
    pagelayout.PootlePage.__init__(self, pagetitle, [], session)
    self.templatename = "login"
    instancetitle = getattr(session.instance, "title", session.localize("Pootle Demo"))
    sessionvars = {"status": session.status, "isopen": session.isopen, "issiteadmin": session.issiteadmin()}
    self.templatevars = {"pagetitle": pagetitle,
        "username_title": self.localize("Username:"),
        "username": getattr(session, 'username', ''),
        "password_title": self.localize("Password:"),
        "language_title": self.localize('Language:'),
        "languages": self.getlanguageoptions(session),
        "login_text": self.localize('Login'),
        "session": sessionvars, "instancetitle": pagetitle}

  def getlanguageoptions(self, session):
    """returns the language selector..."""
    # TODO: work out how we handle localization of language names...
    languageoptions = [('', session.localize("Default"))]
    if isinstance(self.languagenames, dict):
      languageoptions += self.languagenames.items()
    else:
      languageoptions += self.languagenames
    return [{"code": key, "name": value, "selected": key==session.language or None} for key, value in languageoptions]

class RegisterPage(pagelayout.PootlePage):
  """page for new registrations"""
  def __init__(self, session, argdict):
    self.localize = session.localize
    introtext = self.localize("Please enter your registration details")
    pagetitle = self.localize("Pootle Registration")
    self.argdict = argdict
    pagelayout.PootlePage.__init__(self, pagetitle, [], session)
    self.templatename = "register"
    instancetitle = getattr(session.instance, "title", session.localize("Pootle Demo"))
    sessionvars = {"status": session.status, "isopen": session.isopen, "issiteadmin": session.issiteadmin()}
    self.templatevars = {"pagetitle": pagetitle, "introtext": introtext,
        "username_title": self.localize("Username"),
        "username_tooltip": self.localize("Your requested username"),
        "username": self.argdict.get("username", ""),
        "email_title": self.localize("Email Address"),
        "email_tooltip": self.localize("Must be a valid email address"),
        "email": self.argdict.get("email", ""),
        "fullname_title": self.localize("Full Name"),
        "fullname_tooltip": self.localize("Your full name"),
        "fullname": self.argdict.get("name", ""),
        "password_title": self.localize("Password"),
        "password_tooltip": self.localize("Your desired password"),
        "password": self.argdict.get("password", ""),
        "register_text": self.localize('Register Account'),
        "session": sessionvars, "instancetitle": pagetitle}

class ActivatePage(pagelayout.PootlePage):
  """page for new registrations"""
  def __init__(self, session, argdict):
    self.localize = session.localize
    introtext = self.localize("Please enter your activation details")
    self.argdict = argdict
    pagetitle = self.localize("Pootle Account Activation")
    pagelayout.PootlePage.__init__(self, pagetitle, [], session)
    self.templatename = "activate"
    instancetitle = getattr(session.instance, "title", session.localize("Pootle Demo"))
    sessionvars = {"status": session.status, "isopen": session.isopen, "issiteadmin": session.issiteadmin()}
    self.templatevars = {"pagetitle": pagetitle, "introtext": introtext,
        "username_title": self.localize("Username"),
        "username_tooltip": self.localize("Your requested username"),
        "username": self.argdict.get("username", ""),
        "code_title": self.localize("Activation Code"),
        "code_tooltip": self.localize("The activation code you received"),
        "code": self.argdict.get("activationcode", ""),
        "activate_text": self.localize('Activate Account'),
        "session": sessionvars, "instancetitle": pagetitle}

class UserOptions(pagelayout.PootlePage):
  """page for user to change their options"""
  def __init__(self, potree, session):
    self.potree = potree
    self.session = session
    self.localize = session.localize
    submitbutton = widgets.Input({"type":"submit", "name":"changeoptions", "value": self.localize("Save changes")})
    hiddenfields = widgets.HiddenFieldList([("allowmultikey","languages"), ("allowmultikey","projects")])
    formmembers = [self.getprojectoptions(), self.getlanguageoptions(), hiddenfields, submitbutton]
    useroptions = widgets.Form(formmembers, {"name": "useroptions", "action":""})
    homelink = pagelayout.IntroText(widgets.Link("index.html", self.localize("Home page")))
    contents = [self.getpersonaloptions(), useroptions, homelink]
    pagelayout.PootlePage.__init__(self, self.localize("Options for: %s") % session.username, contents, session)

  def getprojectoptions(self):
    """gets the options box to change the user's projects"""
    projectstitle = pagelayout.Title(self.localize("My Projects"))
    projectoptions = []
    userprojects = self.session.getprojects()
    for projectcode in self.potree.getprojectcodes():
      projectname = self.potree.getprojectname(projectcode)
      projectoptions.append((projectcode, projectname))
    projectselect = widgets.MultiSelect({"value": userprojects, "name": "projects"}, projectoptions)
    bodydescription = pagelayout.ItemDescription([projectselect, widgets.HiddenFieldList({"allowmultikey":"projects"})])
    return pagelayout.Contents([projectstitle, bodydescription])

  def getlanguageoptions(self):
    """gets the options box to change the user's languages"""
    languagestitle = pagelayout.Title(self.localize("My Languages"))
    languageoptions = []
    userlanguages = self.session.getlanguages()
    languageoptions = self.potree.getlanguages()
    languageselect = widgets.MultiSelect({"value": userlanguages, "name": "languages"}, languageoptions)
    bodydescription = pagelayout.ItemDescription(languageselect)
    return pagelayout.Contents([languagestitle, bodydescription])

  def getpersonaloptions(self):
    """get the options fields to change the user's personal details"""
    personaltitle = pagelayout.Title(self.localize("Personal Details"))
    personal = table.TableLayout()
    personal.setcell(0, 0, table.TableCell(pagelayout.Title(self.localize("Option"))))
    personal.setcell(0, 1, table.TableCell(pagelayout.Title(self.localize("Current value"))))
    options = {"name": self.localize("Name"), "email": self.localize("Email")}
    for option, optionname in options.items():
      optionvalue = getattr(self.session.prefs, option, "")
      valuetextbox = widgets.Input({"name": "option-%s" % option, "value": optionvalue})
      rownum = personal.maxrownum()+1
      personal.setcell(rownum, 0, table.TableCell(optionname))
      personal.setcell(rownum, 1, table.TableCell(valuetextbox))
    rownum = personal.maxrownum()+1
    submitbutton = widgets.Input({"type":"submit", "name":"changepersonal", "value":self.localize("Save changes")})
    personalform = widgets.Form([personal, submitbutton], {"name": "personal", "action":""})
    interfacetitle = pagelayout.Title(self.localize("Translation Interface Configuration"))
    interface = table.TableLayout()
    interface.setcell(0, 0, table.TableCell(pagelayout.Title(self.localize("Option"))))
    interface.setcell(0, 1, table.TableCell(pagelayout.Title(self.localize("Current value"))))
    uilanguage = getattr(self.session.prefs, "uilanguage", "")
    if not uilanguage:
      userlanguages = self.session.getlanguages()
      if userlanguages:
        uilanguage = userlanguages[0]
    languageoptions = [('', '')] + self.potree.getlanguages()
    selectlanguage = widgets.Select({"value": uilanguage, "name": "option-uilanguage"}, languageoptions)
    interface.setcell(1, 0, table.TableCell(self.localize("User Interface language")))
    interface.setcell(1, 1, table.TableCell(selectlanguage))
    options = {"inputheight": self.localize("Input Height"), "inputwidth": self.localize("Input Width"),
          "viewrows": self.localize("Number of rows in view mode"), 
          "translaterows": self.localize("Number of rows in translate mode")}
    for option, optionname in options.items():
      optionvalue = getattr(self.session.prefs, option, "")
      valuetextbox = widgets.Input({"name": "option-%s" % option, "value": optionvalue})
      rownum = interface.maxrownum()+1
      interface.setcell(rownum, 0, table.TableCell(optionname))
      interface.setcell(rownum, 1, table.TableCell(valuetextbox))
    rownum = interface.maxrownum()+1
    submitbutton = widgets.Input({"type":"submit", "name":"changeinterface", "value":self.localize("Save changes")})
    interfaceform = widgets.Form([interface, submitbutton], {"name": "interface", "action":""})
    return pagelayout.Contents([personaltitle, personalform, interfacetitle, interfaceform])

class OptionalLoginAppServer(server.LoginAppServer):
  """a server that enables login but doesn't require it except for specified pages"""
  def handle(self, req, pathwords, argdict):
    """handles the request and returns a page object in response"""
    argdict = self.processargs(argdict)
    session = self.getsession(req, argdict)
    if session.isopen:
      session.pagecount += 1
      session.remote_ip = self.getremoteip(req)
    return self.getpage(pathwords, session, argdict)

  def hasuser(self, users, username):
    """returns whether the user exists in users"""
    return users.__hasattr__(username)

  def getusernode(self, users, username):
    """gets the node for the given user"""
    if not self.hasuser(users, username):
      usernode = prefs.PrefNode(users, username)
      users.__setattr__(username, usernode)
    else:
      usernode = users.__getattr__(username)
    return usernode

  def adduser(self, users, username, fullname, email, password):
    """adds the user with the given details"""
    usernode = self.getusernode(users, username)
    usernode.name = fullname
    usernode.email = email
    usernode.passwdhash = session.md5hexdigest(password)

  def makeactivationcode(self, users, username):
    """makes a new activation code for the user and returns it"""
    usernode = self.getusernode(users, username)
    usernode.activated = 0
    activationcode = self.generateactivationcode()
    usernode.activationcode = activationcode
    return activationcode

  def activate(self, users, username):
    """sets the user as activated"""
    self.getusernode(users, username).activated = 1

  def changeusers(self, session, argdict):
    """handles multiple changes from the site admin"""
    if not session.issiteadmin():
      raise ValueError(session.localize("You need to be siteadmin to change users"))
    users = session.loginchecker.users
    for key, value in argdict.iteritems():
      if key.startswith("userremove-"):
        usercode = key.replace("userremove-", "", 1)
        if self.hasuser(users, usercode):
          raise NotImplementedError("Can't remove users")
      elif key.startswith("username-"):
        username = key.replace("username-", "", 1)
        if self.hasuser(users, username):
          usernode = self.getusernode(users, username)
          fullname = getattr(usernode, "name", None)
          if fullname != value:
            usernode.name = value
      elif key.startswith("useremail-"):
        username = key.replace("useremail-", "", 1)
        if self.hasuser(users, username):
          usernode = self.getusernode(users, username)
          useremail = getattr(usernode, "email", None)
          if useremail != value:
            usernode.email = value
      elif key.startswith("userpassword-"):
        username = key.replace("userpassword-", "", 1)
        if self.hasuser(users, username):
          usernode = self.getusernode(users, username)
          if value and value.strip():
            usernode.passwdhash = session.md5hexdigest(value.strip())
      elif key.startswith("useractivated-"):
        username = key.replace("useractivated-", "", 1)
        self.activate(users, username)
      elif key == "newusername":
        username = value.lower()
        if not username:
          continue
        if not (username[:1].isalpha() and username.replace("_","").isalnum()):
          raise ValueError("Login must be alphanumeric and start with an alphabetic character (got %r)" % username)
        if self.hasuser(users, username):
          raise ValueError("Already have user with the login: %s" % username)
        userpassword = argdict.get("newuserpassword", None)
        if userpassword is None or userpassword == self.localize("(add password here)"):
          raise ValueError("You must specify a password")
        userfullname = argdict.get("newfullname", None)
        if userfullname == self.localize("(add full name here)"):
          raise ValueError("Please set the users full name or leave it blank")
        useremail = argdict.get("newuseremail", None)
        if useremail == self.localize("(add email here)"):
          raise ValueError("Please set the users email address or leave it blank")
        useractivate = "newuseractivate" in argdict
        self.adduser(users, username, userfullname, useremail, userpassword)
        if useractivate:
          self.activate(users, username)
        else:
          activationcode = self.makeactivationcode(users, username)
          print "user activation code for %s is %s" % (username, activationcode)
    session.saveprefs()

  def handleregistration(self, session, argdict):
    """handles the actual registration"""
    supportaddress = getattr(self.instance.registration, 'supportaddress', "")
    username = argdict.get("username", "")
    if not username or not username.isalnum() or not username[0].isalpha():
      raise RegistrationError("Username must be alphanumeric, and must start with an alphabetic character")
    fullname = argdict.get("name", "")
    email = argdict.get("email", "")
    password = argdict.get("password", "")
    if " " in email or not (email and "@" in email and "." in email):
      raise RegistrationError("You must supply a valid email address")
    userexists = session.loginchecker.userexists(username)
    users = session.loginchecker.users
    if userexists:
      usernode = self.getusernode(users, username)
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
        raise RegistrationError("You must supply a valid password of at least %d characters" % minpasswordlen)
      self.adduser(users, username, fullname, email, password)
      activationcode = self.makeactivationcode(users, username)
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
    session.saveprefs()
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
    if isinstance(fullmessage, unicode):
      fullmessage = fullmessage.encode("utf-8")
    errmsg = mailer.dosendmessage(fromemail=self.instance.registration.fromaddress, recipientemails=[email], message=fullmessage, smtpserver=smtpserver)
    if errmsg:
      raise RegistrationError("Error sending mail: %s" % errmsg)
    return displaymessage, redirecturl

  def registerpage(self, session, argdict):
    """handle registration or return the Register page"""
    if "username" in argdict:
      try:
        displaymessage, redirecturl = self.handleregistration(session, argdict)
      except RegistrationError, message:
        session.status = str(message)
        return RegisterPage(session, argdict)
      message = pagelayout.IntroText(displaymessage)
      redirectpage = pagelayout.PootlePage("Redirecting...", [message], session)
      redirectpage.attribs["refresh"] = 10
      redirectpage.attribs["refreshurl"] = redirecturl
      return redirectpage
    else:
      return RegisterPage(session, argdict)

  def activatepage(self, session, argdict):
    """handle activation or return the Register page"""
    if "username" in argdict and "activationcode" in argdict:
      username = argdict["username"]
      activationcode = argdict["activationcode"]
      if self.hasuser(session.loginchecker.users, username):
        usernode = self.getusernode(session.loginchecker.users, username)
        correctcode = getattr(usernode, "activationcode", "")
        if correctcode and correctcode.strip().lower() == activationcode.strip().lower():
          setattr(usernode, "activated", 1)
          session.saveprefs()
          redirecttext = pagelayout.IntroText("Your account has been activated! Redirecting to login...")
          redirectpage = pagelayout.PootlePage("Redirecting to login...", redirecttext, session)
          redirectpage.attribs["refresh"] = 10
          redirectpage.attribs["refreshurl"] = "login.html?username=%s" % username
          return redirectpage
      failedtext = pagelayout.IntroText("The activation link you have entered was not valid")
      failedpage = pagelayout.PootlePage("Activation Failed", failedtext, session)
      return failedpage
    else:
      return ActivatePage(session, argdict)

class PootleSession(session.LoginSession):
  """a session object that knows about Pootle"""
  def __init__(self, sessioncache, server, sessionstring = None, loginchecker = None):
    """sets up the session and remembers the users prefs"""
    super(PootleSession, self).__init__(sessioncache, server, sessionstring, loginchecker)
    self.getprefs()

  def getprefs(self):
    """gets the users prefs into self.prefs"""
    if self.isopen:
      self.prefs = self.loginchecker.users.__getattr__(self.username)
      self.setlanguage(self.language_set)
    else:
      self.prefs = None

  def saveprefs(self):
    """saves changed preferences back to disk"""
    # TODO: this is a hack, fix it up nicely :-)
    prefsfile = self.loginchecker.users.__root__.__dict__["_setvalue"].im_self
    prefsfile.savefile()

  def open(self):
    """opens the session, along with the users prefs"""
    super(PootleSession, self).open()
    self.getprefs()
    return self.isopen

  def close(self, req):
    """opens the session, along with the users prefs"""
    super(PootleSession, self).close(req)
    self.getprefs()

  def setlanguage(self, language):
    """sets the language for the session"""
    self.language_set = language or ""
    if language:
      self.language = language
    else:
      if self.isopen:
        self.language = getattr(self.prefs, "uilanguage", "") or self.server.defaultlanguage
      else:
        self.language = self.server.defaultlanguage
    if self.isopen:
      if not getattr(self.prefs, "uilanguage", "") and self.language_set:
        self.setinterfaceoptions({"option-uilanguage": self.language_set})
    self.translation = self.server.gettranslation(self.language)

  def validate(self):
    """checks if this session is valid (which means the user must be activated)"""
    if not super(PootleSession, self).validate():
      return False
    if self.loginchecker.users.__hasattr__(self.username):
      usernode = self.loginchecker.users.__getattr__(self.username)
      if getattr(usernode, "activated", 0):
        return self.isvalid
    self.isvalid = False
    self.status = "username has not yet been activated"
    return self.isvalid

  def setoptions(self, argdict):
    """sets the user options"""
    userprojects = argdict.get("projects", [])
    if isinstance(userprojects, (str, unicode)):
      userprojects = [userprojects]
    setattr(self.prefs, "projects", ",".join(userprojects))
    userlanguages = argdict.get("languages", [])
    if isinstance(userlanguages, (str, unicode)):
      userlanguages = [userlanguages]
    setattr(self.prefs, "languages", ",".join(userlanguages))
    self.saveprefs()

  def setpersonaloptions(self, argdict):
    """sets the users personal details"""
    name = argdict.get("option-name", "")
    setattr(self.prefs, "name", name)
    email = argdict.get("option-email", "")
    setattr(self.prefs, "email", email)
    self.saveprefs()

  def setinterfaceoptions(self, argdict):
    """sets the users interface details"""
    value = argdict.get("option-uilanguage", "")
    if value:
      self.prefs.uilanguage = value
    def setinterfacevalue(name, errormessage):
      value = argdict.get("option-%s" % name, "")
      if value != "":
        if not value.isdigit():
          raise ValueError(errormessage)
        setattr(self.prefs, name, value)
    setinterfacevalue("inputheight", self.localize("Input height must be numeric"))
    setinterfacevalue("inputwidth", self.localize("Input width must be numeric"))
    setinterfacevalue("viewrows", self.localize("The number of rows displayed in view mode must be numeric"))
    setinterfacevalue("translaterows", self.localize("The number of rows displayed in translate mode must be numeric"))
    self.saveprefs()

  def getprojects(self):
    """gets the user's projects"""
    userprojects = getattr(self.prefs, "projects", "")
    return [projectcode.strip() for projectcode in userprojects.split(',') if projectcode.strip()]

  def getlanguages(self):
    """gets the user's languages"""
    userlanguages = getattr(self.prefs, "languages", "")
    return [languagecode.strip() for languagecode in userlanguages.split(',') if languagecode.strip()]

  def getrights(self):
    """gets the user's rights"""
    return getattr(self.prefs, "rights", None)

  def issiteadmin(self):
    """returns whether the user can administer the site"""
    return getattr(self.getrights(), "siteadmin", False)

