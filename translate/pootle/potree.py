#!/usr/bin/env python

"""manages projects and files and translations"""

from translate.pootle import projects
from translate.pootle import pootlefile
import os
import sre

languagere = sre.compile("^[a-z]{2,3}([_-][A-Z]{2,3}|)$")
regionre = sre.compile("^[_-][A-Z]{2,3}$")

class POTree:
  """Manages the tree of projects and languages"""
  def __init__(self, instance):
    self.languages = instance.languages
    self.projects = instance.projects
    self.podirectory = instance.podirectory
    self.projectcache = {}

  def saveprefs(self):
    """saves any changes made to the preferences"""
    # TODO: this is a hack, fix it up nicely :-)
    prefsfile = self.languages.__root__.__dict__["_setvalue"].im_self
    prefsfile.savefile()

  def changelanguages(self, argdict):
    """changes language entries"""
    for key, value in argdict.iteritems():
      if key.startswith("languageremove-"):
        languagecode = key.replace("languageremove-", "", 1)
        if self.haslanguage(languagecode):
          delattr(self.languages, languagecode)
      elif key.startswith("languagename-"):
        languagecode = key.replace("languagename-", "", 1)
        if self.haslanguage(languagecode):
          languagename = self.getlanguagename(languagecode)
          if languagename != value:
            self.setlanguagename(languagecode, value)
      elif key == "newlanguagecode":
        languagecode = value.lower()
        if not languagecode.strip():
          continue
        if not languagecode.isalpha():
          raise ValueError("Language code must be alphabetic")
        if self.haslanguage(languagecode):
          raise ValueError("Already have language with the code %s" % languagecode)
        languagename = argdict.get("newlanguagename", languagecode)
        setattr(self.languages, languagecode + ".fullname", languagename)
    self.saveprefs()

  def changeprojects(self, argdict):
    """changes project entries"""
    for key, value in argdict.iteritems():
      if key.startswith("projectremove-"):
        projectcode = key.replace("projectremove-", "", 1)
        if hasattr(self.projects, projectcode):
          delattr(self.projects, projectcode)
      elif key.startswith("projectname-"):
        projectcode = key.replace("projectname-", "", 1)
        if hasattr(self.projects, projectcode):
          projectname = self.getprojectname(projectcode)
          if projectname != value:
            self.setprojectname(projectcode, value)
      elif key.startswith("projectdescription-"):
        projectcode = key.replace("projectdescription-", "", 1)
        if hasattr(self.projects, projectcode):
          projectdescription = self.getprojectdescription(projectcode)
          if projectdescription != value:
            self.setprojectdescription(projectcode, value)
      elif key.startswith("projectcheckerstyle-"):
        projectcode = key.replace("projectcheckerstyle-", "", 1)
        if hasattr(self.projects, projectcode):
          projectcheckerstyle = self.getprojectcheckerstyle(projectcode)
          if projectcheckerstyle != value:
            self.setprojectcheckerstyle(projectcode, value)
      elif key.startswith("projectcreatemofiles-"):
        projectcode = key.replace("projectcreatemofiles-", "", 1)
        if hasattr(self.projects, projectcode):
          self.setprojectcreatemofiles(projectcode, 1)
      elif key == "newprojectcode":
        projectcode = value.lower()
        if not projectcode:
          continue
        if not (projectcode[:1].isalpha() and projectcode.replace("_","").isalnum()):
          raise ValueError("Project code must be alphanumeric and start with an alphabetic character (got %r)" % projectcode)
        if hasattr(self.projects, projectcode):
          raise ValueError("Already have project with the code %s" % projectcode)
        projectname = argdict.get("newprojectname", projectcode)
        projectdescription = argdict.get("newprojectdescription", "")
        projectcheckerstyle = argdict.get("newprojectcheckerstyle", "")
        projectcreatemofiles = argdict.get("newprojectcreatemofiles", "")
        setattr(self.projects, projectcode + ".fullname", projectname)
        setattr(self.projects, projectcode + ".description", projectdescription)
        setattr(self.projects, projectcode + ".checkerstyle", projectcheckerstyle)
        setattr(self.projects, projectcode + ".createmofiles", projectcreatemofiles)
        projectdir = os.path.join(self.podirectory, projectcode)
        if not os.path.isdir(projectdir):
          os.mkdir(projectdir)
    self.saveprefs()

  def haslanguage(self, languagecode):
    """checks if this language exists"""
    return hasattr(self.languages, languagecode)

  def getlanguageprefs(self, languagecode):
    """returns the language object"""
    return getattr(self.languages, languagecode)

  def getlanguagename(self, languagecode):
    """returns the language's full name"""
    return getattr(self.getlanguageprefs(languagecode), "fullname", languagecode)

  def setlanguagename(self, languagecode, languagename):
    """returns the language's full name"""
    setattr(self.getlanguageprefs(languagecode), "fullname", languagename)

  def getlanguagecodes(self, projectcode=None):
    """returns a list of valid languagecodes for a given project or all projects"""
    alllanguagecodes = [languagecode for languagecode, language in self.languages.iteritems()]
    if projectcode is None:
      alllanguagecodes.sort()
      return alllanguagecodes
    else:
      projectdir = os.path.join(self.podirectory, projectcode)
      if not os.path.exists(projectdir):
        return []
      if self.isgnustyle(projectcode):
        return [languagecode for languagecode in alllanguagecodes if self.hasproject(languagecode, projectcode)]
      else:
        subdirs = [fn for fn in os.listdir(projectdir) if os.path.isdir(os.path.join(projectdir, fn))]
        languagecodes = []
        for potentialcode in subdirs:
          if not self.languagematch(None, potentialcode):
            continue
          if "-" in potentialcode:
            potentialcode = potentialcode[:potentialcode.find("-")]
          elif "_" in potentialcode:
            potentialcode = potentialcode[:potentialcode.find("_")]
          if potentialcode in alllanguagecodes:
            languagecodes.append(potentialcode)
        return languagecodes

  def getprojectcodes(self, languagecode=None):
    """returns a list of project codes that are valid for the given languagecode or all projects"""
    projectcodes = [projectcode for projectcode, projectprefs in self.projects.iteritems()]
    projectcodes.sort()
    if languagecode is None:
      return projectcodes
    else:
      return [projectcode for projectcode in projectcodes if self.hasproject(languagecode, projectcode)]

  def hasproject(self, languagecode, projectcode):
    """returns whether the project exists for the language"""
    if not hasattr(self.projects, projectcode):
      return False
    if languagecode is None:
      return True
    if not self.haslanguage(languagecode):
      return False
    try:
      podir = self.getpodir(languagecode, projectcode)
      return True
    except IndexError:
      return False

  def gettemplates(self, projectcode):
    """returns templates for the given project"""
    projectdir = os.path.join(self.podirectory, projectcode)
    templatesdir = os.path.join(projectdir, "templates")
    if not os.path.exists(templatesdir):
      templatesdir = projectdir
    potfilenames = []
    def addfiles(podir, dirname, fnames):
      """adds the files to the set of files for this project"""
      basedirname = dirname.replace(podir, "", 1)
      while basedirname.startswith(os.sep):
        basedirname = basedirname.replace(os.sep, "", 1)
      ponames = [fname for fname in fnames if fname.endswith(os.extsep+"pot")]
      potfilenames.extend([os.path.join(basedirname, poname) for poname in ponames])
    os.path.walk(templatesdir, addfiles, templatesdir)
    return potfilenames

  def getproject(self, languagecode, projectcode):
    """returns the project object for the languagecode and projectcode"""
    if (languagecode, projectcode) not in self.projectcache:
      self.projectcache[languagecode, projectcode] = projects.TranslationProject(languagecode, projectcode, self)
    return self.projectcache[languagecode, projectcode]

  def isgnustyle(self, projectcode):
    """checks whether the whole project is a GNU-style project"""
    projectdir = os.path.join(self.podirectory, projectcode)
    return self.hasgnufiles(projectdir)

  def addtranslationproject(self, languagecode, projectcode):
    """creates a new TranslationProject"""
    if self.hasproject(languagecode, projectcode):
      raise ValueError("projects.TranslationProject for project %s, language %s already exists" % (projectcode, languagecode))
    translationproject = projects.TranslationProject(languagecode, projectcode, self, create=True)

  def getprojectname(self, projectcode):
    """returns the full name of the project"""
    projectprefs = getattr(self.projects, projectcode)
    return getattr(projectprefs, "fullname", projectcode)

  def setprojectname(self, projectcode, projectname):
    """returns the full name of the project"""
    projectprefs = getattr(self.projects, projectcode)
    setattr(projectprefs, "fullname", projectname)

  def getprojectdescription(self, projectcode):
    """returns the project description"""
    projectprefs = getattr(self.projects, projectcode)
    return getattr(projectprefs, "description", projectcode)

  def setprojectdescription(self, projectcode, projectdescription):
    """returns the project description"""
    projectprefs = getattr(self.projects, projectcode)
    setattr(projectprefs, "description", projectdescription)

  def getprojectcheckerstyle(self, projectcode):
    """returns the project checker style"""
    projectprefs = getattr(self.projects, projectcode)
    return getattr(projectprefs, "checkerstyle", projectcode)

  def setprojectcheckerstyle(self, projectcode, projectcheckerstyle):
    """sets the project checker style"""
    projectprefs = getattr(self.projects, projectcode)
    setattr(projectprefs, "checkerstyle", projectcheckerstyle)

  def getprojectcreatemofiles(self, projectcode):
    """returns whether the project builds MO files"""
    projectprefs = getattr(self.projects, projectcode)
    return getattr(projectprefs, "createmofiles", False)

  def setprojectcreatemofiles(self, projectcode, projectcreatemofiles):
    """sets whether the project builds MO files"""
    projectprefs = getattr(self.projects, projectcode)
    setattr(projectprefs, "createmofiles", projectcreatemofiles)

  def hasgnufiles(self, podir, languagecode=None):
    """returns whether this directory contains gnu-style PO filenames for the given language"""
    fnames = os.listdir(podir)
    poext = os.extsep + "po"
    subdirs = []
    for fn in fnames:
      if fn.endswith(poext):
        if self.languagematch(languagecode, fn[:-len(poext)]):
          return True
      elif os.path.isdir(os.path.join(podir, fn)):
        # if we have a language subdirectory, we're probably not GNU-style
        if self.languagematch(languagecode, fn):
          return False
        subdirs.append(os.path.join(podir, fn))
    for subdir in subdirs:
      if self.hasgnufiles(subdir, languagecode):
        return True
    return False

  def getpodir(self, languagecode, projectcode):
    """returns the base directory containing po files for the project"""
    projectdir = os.path.join(self.podirectory, projectcode)
    if not os.path.exists(projectdir):
      raise IndexError("directory not found for project %s" % (projectcode))
      return None
    languagedir = os.path.join(projectdir, languagecode)
    if not os.path.exists(languagedir):
      languagedirs = [languagedir for languagedir in os.listdir(projectdir) if self.languagematch(languagecode, languagedir)]
      if not languagedirs:
        # if no matching directories can be found, check if it is a GNU-style project
        if self.hasgnufiles(projectdir, languagecode):
          return projectdir
        raise IndexError("directory not found for language %s, project %s" % (languagecode, projectcode))
      # TODO: handle multiple regions
      if len(languagedirs) > 1:
        raise IndexError("multiple regions defined for language %s, project %s" % (languagecode, projectcode))
      languagedir = os.path.join(projectdir, languagedirs[0])
    return languagedir

  def languagematch(self, languagecode, otherlanguagecode):
    """matches a languagecode to another, ignoring regions in the second"""
    if languagecode is None:
      return languagere.match(otherlanguagecode)
    return languagecode == otherlanguagecode or \
      (otherlanguagecode.startswith(languagecode) and regionre.match(otherlanguagecode[len(languagecode):]))

  def getpofiles(self, languagecode, projectcode):
    """returns a list of po files for the project and language"""
    def addfiles(podir, dirname, fnames):
      """adds the files to the set of files for this project"""
      basedirname = dirname.replace(podir, "", 1)
      while basedirname.startswith(os.sep):
        basedirname = basedirname.replace(os.sep, "", 1)
      ponames = [fname for fname in fnames if fname.endswith(os.extsep+"po")]
      pofilenames.extend([os.path.join(basedirname, poname) for poname in ponames])
    def addgnufiles(podir, dirname, fnames):
      """adds the files to the set of files for this project"""
      basedirname = dirname.replace(podir, "", 1)
      while basedirname.startswith(os.sep):
        basedirname = basedirname.replace(os.sep, "", 1)
      poext = os.extsep + "po"
      ponames = [fn for fn in fnames if fn.endswith(poext) and self.languagematch(languagecode, fn[:-len(poext)])]
      pofilenames.extend([os.path.join(basedirname, poname) for poname in ponames])
    pofilenames = []
    podir = self.getpodir(languagecode, projectcode)
    if self.hasgnufiles(podir, languagecode):
      os.path.walk(podir, addgnufiles, podir)
    else:
      os.path.walk(podir, addfiles, podir)
    return pofilenames

  def refreshstats(self):
    """manually refreshes (all or missing) the stats files"""
    for projectcode in self.getprojectcodes():
      print "Project %s:" % (projectcode)
      for languagecode in self.getlanguagecodes(projectcode):
        print "Project %s, Language %s:" % (projectcode, languagecode)
        translationproject = self.getproject(languagecode, projectcode)
        translationproject.stats = {}
        for pofilename in translationproject.pofilenames:
          translationproject.getpostats(pofilename)
          translationproject.pofiles[pofilename] = pootlefile.pootlefile(translationproject, pofilename)
          print ".",
        print
        self.projectcache = {}

