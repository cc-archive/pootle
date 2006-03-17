#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jToolkit.widgets import widgets
from jToolkit.widgets import table
from Pootle import pagelayout
from Pootle import projects
from translate.filters import checks

class AdminPage(pagelayout.PootlePage):
  """page for administering pootle..."""
  def __init__(self, potree, session, instance):
    self.potree = potree
    self.session = session
    self.instance = instance
    self.localize = session.localize
    pagelayout.PootlePage.__init__(self, self.localize("Pootle Admin Page"), [], session)
    self.templatename = "adminindex"
    sessionvars = {"status": self.session.status, "isopen": self.session.isopen, "issiteadmin": self.session.issiteadmin()}
    instancetitle = getattr(self.instance, "title", session.localize("Pootle Demo"))
    self.templatevars = {"options": self.getoptions(), "session": sessionvars, "instancetitle": instancetitle}

  def getoptions(self):
    optiontitles = {"title": self.localize("Title"), "description": self.localize("Description"), "baseurl": self.localize("Base URL"), "homepage": self.localize("Home Page")}
    options = []
    for optionname, optiontitle in optiontitles.items():
      optionvalue = getattr(self.instance, optionname, "")
      option = {"name": "option-%s" % optionname, "title": optiontitle, "value": optionvalue}
      options.append(option)
    return options

class LanguagesAdminPage(pagelayout.PootlePage):
  """page for administering pootle..."""
  def __init__(self, potree, session, instance):
    self.potree = potree
    self.session = session
    self.instance = instance
    self.localize = session.localize
    pagelayout.PootlePage.__init__(self, self.localize("Pootle Languages Admin Page"), [], session)
    self.templatename = "adminlanguages"
    sessionvars = {"status": self.session.status, "isopen": self.session.isopen, "issiteadmin": self.session.issiteadmin()}
    instancetitle = getattr(self.instance, "title", session.localize("Pootle Demo"))
    self.templatevars = {"languages": self.getlanguagesoptions(), "options": self.getoptions(), "session": sessionvars, "instancetitle": instancetitle}

  def getoptions(self):
    options = [{"name": "code", "title": self.localize("ISO Code"), "size": 6, "newvalue": ""},
               {"name": "name", "title": self.localize("Full Name"), "newvalue": self.localize("(add language here)")},
               {"name": "specialchars", "title": self.localize("Special Chars"), "newvalue": self.localize("(special characters)")},
               {"name": "nplurals", "title": self.localize("Number of Plurals"), "newvalue": self.localize("(number of plurals)")},
               {"name": "pluralequation", "title": self.localize("Plural Equation"), "newvalue": self.localize("(plural equation)")},
               {"name": "remove", "title": self.localize("Remove Language")}]
    for option in options:
      if "newvalue" in option:
        option["newname"] = "newlanguage" + option["name"]
    return options

  def getlanguagesoptions(self):
    languages = []
    for languagecode, languagename in self.potree.getlanguages():
      languagespecialchars = self.potree.getlanguagespecialchars(languagecode)
      languagenplurals = self.potree.getlanguagenplurals(languagecode)
      languagepluralequation = self.potree.getlanguagepluralequation(languagecode)
      languageremove = None
      # TODO: make label work like this
      removelabel = self.localize("Remove %s") % languagecode
      languageoptions = [{"name": "languagename-%s" % languagecode, "value": languagename, "type": "text"},
                         {"name": "languagespecialchars-%s" % languagecode, "value": languagespecialchars, "type": "text"},
                         {"name": "languagenplurals-%s" % languagecode, "value": languagenplurals, "type": "text"},
                         {"name": "languagepluralequation-%s" % languagecode, "value": languagepluralequation, "type": "text"},
                         {"name": "languageremove-%s" % languagecode, "value": languageremove, "type": "checkbox", "label": removelabel}]
      languages.append({"code": languagecode, "options": languageoptions})
    return languages

class ProjectsAdminPage(pagelayout.PootlePage):
  """page for administering pootle..."""
  def __init__(self, potree, session, instance):
    self.potree = potree
    self.session = session
    self.instance = instance
    self.localize = session.localize
    pagelayout.PootlePage.__init__(self, self.localize("Pootle Projects Admin Page"), [], session)
    self.templatename = "adminprojects"
    self.allchecks = [{"value": check, "description": check} for check in checks.projectcheckers.keys()]
    self.allchecks.insert(0, {"value": "", "description": self.localize("Standard")})
    sessionvars = {"status": self.session.status, "isopen": self.session.isopen, "issiteadmin": self.session.issiteadmin()}
    instancetitle = getattr(self.instance, "title", session.localize("Pootle Demo"))
    self.templatevars = {"projects": self.getprojectsoptions(), "options": self.getoptions(), "session": sessionvars, "instancetitle": instancetitle}

  def getoptions(self):
    options = [{"name": "code", "title": self.localize("Project Code"), "size": 6, "newvalue": ""},
               {"name": "name", "title": self.localize("Full Name"), "newvalue": self.localize("(add project here)")},
               {"name": "description", "title": self.localize("Project Description"), "newvalue": self.localize("(project description)")},
               {"name": "checkerstyle", "title": self.localize("Checker Style"), "selectoptions": self.allchecks, "newvalue": ""},
               {"name": "createmofiles", "title": self.localize("Create MO Files"), "type": "checkbox", "newvalue": ""},
               {"name": "remove", "title": self.localize("Remove Project")}]
    for option in options:
      if "newvalue" in option:
        option["newname"] = "newproject" + option["name"]
      if "type" not in option and "selectoptions" not in option:
        type="text"
    return options

  def getprojectsoptions(self):
    projects = []
    for projectcode in self.potree.getprojectcodes():
      projectadminlink = "../projects/%s/admin.html" % projectcode
      projectname = self.potree.getprojectname(projectcode)
      projectdescription = self.potree.getprojectdescription(projectcode)
      projectname = self.potree.getprojectname(projectcode)
      projectcheckerstyle = self.potree.getprojectcheckerstyle(projectcode)
      if self.potree.getprojectcreatemofiles(projectcode):
        projectcreatemofiles = "checked"
      else:
        projectcreatemofiles = ""
      projectremove = None
      removelabel = self.localize("Remove %s") % projectcode
      projectoptions = [{"name": "projectname-%s" % projectcode, "value": projectname, "type": "text"},
                        {"name": "projectdescription-%s" % projectcode, "value": projectdescription, "type": "text"},
                        {"name": "projectcheckerstyle-%s" % projectcode, "value": projectcheckerstyle, "selectoptions": self.allchecks},
                        {"name": "projectcreatemofiles-%s" % projectcode, "value": projectcreatemofiles, "type": "checkbox", projectcreatemofiles: ""},
                        {"name": "projectremove-%s" % projectcode, "value": projectremove, "type": "checkbox", "label": removelabel}]
      projects.append({"code": projectcode, "adminlink": projectadminlink, "options": projectoptions})
    return projects

class UsersAdminPage(pagelayout.PootlePage):
  """page for administering pootle..."""
  def __init__(self, server, users, session, instance):
    self.server = server
    self.users = users
    self.session = session
    self.instance = instance
    self.localize = session.localize
    pagelayout.PootlePage.__init__(self, self.localize("Pootle User Admin Page"), [], session)
    self.templatename = "adminusers"
    sessionvars = {"status": self.session.status, "isopen": self.session.isopen, "issiteadmin": self.session.issiteadmin()}
    instancetitle = getattr(self.instance, "title", session.localize("Pootle Demo"))
    self.templatevars = {"users": self.getusersoptions(), "options": self.getoptions(), "session": sessionvars, "instancetitle": instancetitle}

  def getoptions(self):
    options = [{"name": "name", "title": self.localize("Login"), "newvalue": "", "size": 6},
               {"name": "fullname", "title": self.localize("Full Name"), "newvalue": self.localize("(add full name here)")},
               {"name": "email", "title": self.localize("Email Address"), "newvalue": self.localize("(add email here)")},
               {"name": "password", "title": self.localize("Password"), "newvalue": self.localize("(add password here)")},
               {"name": "activated", "title": self.localize("Activated"), "type": "checkbox", "checked": "true", "newvalue": "", "label": self.localize("Activate New User")},
               {"name": "remove", "title": self.localize("Remove User"), "type": "checkbox"}]
    for option in options:
      if "newvalue" in option:
        # TODO: rationalize this in the form processing
        if option["name"] == "activated":
          option["newname"] = "newuseractivate"
        else:
          option["newname"] = "newuser" + option["name"]
    return options

  def getusersoptions(self):
    users = []
    for usercode, usernode in self.users.iteritems(sorted=True):
      fullname = getattr(usernode, "name", "")
      email = getattr(usernode, "email", "")
      activated = getattr(usernode, "activated", 0) == 1
      if activated:
        activatedattr = "checked"
      else:
        activatedattr = ""
      userremove = None
      removelabel = self.localize("Remove %s") % usercode
      useroptions = [{"name": "username-%s" % usercode, "value": fullname, "type": "text"},
                     {"name": "useremail-%s" % usercode, "value": email, "type": "text"},
                     {"name": "userpassword-%s" % usercode, "value": None, "type": "text"},
                     {"name": "useractivated-%s" % usercode, "value": activated, "type": "checkbox", activatedattr: ""},
                     {"name": "userremove-%s" % usercode, "value": None, "type": "checkbox", "label": removelabel}]
      users.append({"code": usercode, "options": useroptions})
    return users

class ProjectAdminPage(pagelayout.PootlePage):
  """list of languages belonging to a project"""
  def __init__(self, potree, projectcode, session, argdict):
    self.potree = potree
    self.projectcode = projectcode
    self.session = session
    self.localize = session.localize
    projectname = self.potree.getprojectname(self.projectcode)
    if self.session.issiteadmin():
      if "doaddlanguage" in argdict:
        newlanguage = argdict.get("newlanguage", None)
        if not newlanguage:
          raise ValueError("You must select a new language")
        self.potree.addtranslationproject(newlanguage, self.projectcode)
      if "doupdatelanguage" in argdict:
        languagecodes = argdict.get("updatelanguage", None)
        if not languagecodes:
          raise ValueError("No languagecode given in doupdatelanguage")
        if isinstance(languagecodes, (str, unicode)):
          languagecodes = [languagecodes]
        for languagecode in languagecodes:
          translationproject = self.potree.getproject(languagecode, self.projectcode)
          translationproject.converttemplates(self.session)
    main_link = self.localize("Back to main page")
    existing_title = self.localize("Existing languages")
    existing_languages = self.getexistinglanguages()
    new_languages = self.getnewlanguages()
    update_button = self.localize("Update Languages")
    pagetitle = "Pootle Admin: "+projectname,
    norights_text = self.localize("You do not have the rights to administer this project.")
    update_link = self.localize("Update from templates")
    pagelayout.PootlePage.__init__(self, pagetitle, [], session, bannerheight=81, returnurl="projects/%s/admin.html" % projectcode)
    self.templatename = "projectadmin"
    sessionvars = {"status": self.session.status, "isopen": self.session.isopen, "issiteadmin": self.session.issiteadmin()}
    instancetitle = getattr(self.session.instance, "title", session.localize("Pootle Demo"))
    self.templatevars = {"pagetitle": pagetitle, "norights_text": norights_text,
        "project": {"code": projectcode, "name": projectname},
        "existing_title": existing_title, "existing_languages": existing_languages,
        "new_languages": new_languages,
        "update_button": update_button, "add_button": self.localize("Add Language"),
        "main_link": main_link, "update_link": update_link,
        "session": sessionvars, "instancetitle": instancetitle}

  def getexistinglanguages(self):
    """gets the info on existing languages"""
    languages = self.potree.getlanguages(self.projectcode)
    languageitems = [{"code": languagecode, "name": languagename} for languagecode, languagename in languages]
    for n, item in enumerate(languageitems):
      item["parity"] = ["even", "odd"][n % 2]
    return languageitems

  def getnewlanguages(self):
    """returns a box that lets the user add new languages"""
    existingcodes = self.potree.getlanguagecodes(self.projectcode)
    allcodes = self.potree.getlanguagecodes()
    newcodes = [code for code in allcodes if not (code in existingcodes or code == "templates")]
    newoptions = [(self.potree.getlanguagename(code), code) for code in newcodes]
    newoptions.sort()
    newoptions = [{"code": code, "name": languagename} for (languagename, code) in newoptions]
    return newoptions

class TranslationProjectAdminPage(pagelayout.PootlePage):
  """admin page for a translation project (project+language)"""
  def __init__(self, potree, project, session, argdict):
    self.potree = potree
    self.project = project
    self.session = session
    self.localize = session.localize
    self.rightnames = self.project.getrightnames(session)
    title = self.localize("Pootle Admin: %s %s") % (self.project.languagename, self.project.projectname)
    mainlink = widgets.Link("index.html", self.localize("Project home page"))
    links = [pagelayout.Title(title), pagelayout.IntroText(mainlink)]
    if "admin" in self.project.getrights(self.session):
      if "doupdaterights" in argdict:
        for key, value in argdict.iteritems():
          if key.startswith("rights-"):
            username = key.replace("rights-", "", 1)
            self.project.setrights(username, value)
          if key.startswith("rightsremove-"):
            username = key.replace("rightsremove-", "", 1)
            self.project.delrights(username)
        username = argdict.get("rightsnew-username", None)
        if username:
          username = username.strip()
          if self.session.loginchecker.userexists(username):
            self.project.setrights(username, argdict.get("rightsnew", ""))
          else:
            raise IndexError(self.localize("Cannot set rights for username %s - user does not exist") % username)
      contents = [self.getoptions()]
    else:
      contents = pagelayout.IntroText(self.localize("You do not have the rights to administer this project."))
    pagelayout.PootlePage.__init__(self, title, [links, contents], session, bannerheight=81)

  def getoptions(self):
    """returns a box that describes the options"""
    self.project.readprefs()
    if self.project.filestyle == "gnu":
      filestyle = pagelayout.IntroText(self.localize("This is a GNU-style project (one directory, files named per language)."))
    else:
      filestyle = pagelayout.IntroText(self.localize("This is a standard style project (one directory per language)."))
    rightstitle = pagelayout.Title(self.localize("User Permissions"))
    rightstable = table.TableLayout()
    rightstable.setcell(0, 0, table.TableCell(pagelayout.Title(self.localize("Username"))))
    rightstable.setcell(0, 1, table.TableCell(pagelayout.Title(self.localize("Rights"))))
    rightstable.setcell(0, 2, table.TableCell(pagelayout.Title(self.localize("Remove"))))
    self.addrightsrow(rightstable, 1, "nobody", self.project.getrights(username=None), delete=False)
    defaultrights = self.project.getrights(username="default")
    self.addrightsrow(rightstable, 2, "default", defaultrights, delete=False)
    rownum = 3
    userlist = []
    for username, rights in getattr(self.project.prefs, "rights", {}).iteritems():
      if username in ("nobody", "default"): continue
      userlist.append(username)
    userlist.sort()
    for username in userlist:
      self.addrightsrow(rightstable, rownum, username, self.project.getrights(username=username))
      rownum += 1
    rightstable.setcell(rownum, 0, table.TableCell(widgets.Input({"name": "rightsnew-username"})))
    selectrights = widgets.MultiSelect({"name": "rightsnew", "value": defaultrights}, self.rightnames)
    rightstable.setcell(rownum, 1, table.TableCell(selectrights))
    submitbutton = widgets.Input({"type": "submit", "name": "doupdaterights", "value": self.localize("Update Rights")})
    rightsform = widgets.Form([rightstitle, rightstable, submitbutton], {"action": "", "name":"rightsform"})
    return [filestyle, rightsform]

  def addrightsrow(self, rightstable, rownum, username, rights, delete=True):
    """adds a row for the given user's rights"""
    if not isinstance(rights, list):
      rights = [right.strip() for right in rights.split(",")]
    rightstable.setcell(rownum, 0, table.TableCell(username))
    selectrights = widgets.MultiSelect({"name": "rights-%s" % username, "value": rights}, self.rightnames)
    rightstable.setcell(rownum, 1, table.TableCell(selectrights))
    removecheckbox = widgets.Input({"type":"checkbox", "name":"rightsremove-%s" % username})
    if delete: 
      rightstable.setcell(rownum, 2, table.TableCell([removecheckbox, self.localize("Remove %s") % username]))

