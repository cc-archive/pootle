#!/usr/bin/env python

"""manages projects and files and translations"""

from translate.storage import po
from translate.misc import quote
from translate.filters import checks
from translate.filters import pofilter
from translate.convert import po2csv
from translate.tools import pogrep
import os

def getmodtime(filename, default=None):
  """gets the modificationtime of the given file"""
  if os.path.exists(filename):
    return os.stat(filename)[os.path.stat.ST_MTIME]
  else:
    return default

class TranslationSession:
  """A translation session represents a users work on a particular translation project"""
  def __init__(self, project, session):
    self.session = session
    self.project = project

  def receivetranslation(self, pofilename, item, trans, issuggestion):
    """submits a new/changed translation from the user"""
    if issuggestion:
      self.project.suggesttranslation(pofilename, item, trans)
    else:
      self.project.updatetranslation(pofilename, item, trans)

  def skiptranslation(self, pofilename, item):
    """skips a declined translation from the user"""
    pass

class pootlefile(po.pofile):
  """this represents a pootle-managed .po file and its associated files"""
  def __init__(self, project, pofilename):
    po.pofile.__init__(self)
    self.project = project
    self.checker = self.project.checker
    self.pofilename = pofilename
    self.filename = os.path.join(self.project.podir, self.pofilename)
    self.statsfilename = self.filename + os.extsep + "stats"
    self.pendingfilename = self.filename + os.extsep + "pending"
    self.assignsfilename = self.filename + os.extsep + "assigns"
    self.pendingfile = None
    # we delay parsing until it is required
    self.parsed = False
    self.getstats()
    self.getassigns()

  def readpofile(self):
    """reads and parses the main po file"""
    self.parse(open(self.filename, 'r'))
    # we ignore all the headers by using this filtered set
    self.transelements = [poel for poel in self.poelements if not (poel.isheader() or poel.isblank())]
    self.classifyelements()
    self.parsed = True

  def savepofile(self):
    """saves changes to the main file to disk..."""
    lines = self.tolines()
    open(self.filename, "w").writelines(lines)

  def getsource(self):
    """returns pofile source"""
    if not self.parsed:
      self.readpofile()
    lines = self.tolines()
    return "".join(lines)

  def getcsv(self):
    """returns pofile as csv"""
    if not self.parsed:
      self.readpofile()
    convertor = po2csv.po2csv()
    csvfile = convertor.convertfile(self)
    lines = csvfile.tolines()
    return "".join(lines)

  def readpendingfile(self):
    """reads and parses the pending file corresponding to this po file"""
    if os.path.exists(self.pendingfilename):
      pendingmtime = getmodtime(self.pendingfilename)
      if pendingmtime == getattr(self, "pendingmtime", None):
        return
      inputfile = open(self.pendingfilename, "r")
      self.pendingmtime, self.pendingfile = pendingmtime, po.pofile(inputfile)
      if self.parsed:
        self.reclassifysuggestions()
    else:
      self.pendingfile = po.pofile()
      self.savependingfile()

  def savependingfile(self):
    """saves changes to disk..."""
    lines = self.pendingfile.tolines()
    open(self.pendingfilename, "w").writelines(lines)
    self.pendingmtime = getmodtime(self.pendingfilename)

  def getstats(self):
    """reads the stats if neccessary or returns them from the cache"""
    if os.path.exists(self.statsfilename):
      self.readstats()
    pomtime = getmodtime(self.filename)
    pendingmtime = getmodtime(self.pendingfilename, None)
    if hasattr(self, "pendingmtime"):
      self.readpendingfile()
    if pomtime != getattr(self, "statspomtime", None) or pendingmtime != getattr(self, "statspendingmtime", None):
      self.calcstats()
      self.savestats()
    return self.stats

  def readstats(self):
    """reads the stats from the associated stats file, setting the required variables"""
    statsmtime = getmodtime(self.statsfilename)
    if statsmtime == getattr(self, "statsmtime", None):
      return
    stats = open(self.statsfilename, "r").read()
    mtimes, postatsstring = stats.split("\n", 1)
    mtimes = mtimes.strip().split()
    if len(mtimes) == 1:
      frompomtime = int(mtimes[0])
      frompendingmtime = None
    elif len(mtimes) == 2:
      frompomtime = int(mtimes[0])
      frompendingmtime = int(mtimes[1])
    postats = {}
    for line in postatsstring.split("\n"):
      if not line.strip():
        continue
      if not ":" in line:
        print "invalid stats line in", self.statsfilename,line
        continue
      name, count = line.split(":", 1)
      count = int(count.strip())
      postats[name.strip()] = count
    # save all the read times, data simultaneously
    self.statspomtime, self.statspendingmtime, self.statsmtime, self.stats = frompomtime, frompendingmtime, statsmtime, postats

  def savestats(self):
    """saves the current statistics to file"""
    # assumes self.stats is up to date
    try:
      postatsstring = "\n".join(["%s:%d" % (name, count) for name, count in self.stats.iteritems()])
      statsfile = open(self.statsfilename, "w")
      if os.path.exists(self.pendingfilename):
        statsfile.write("%d %d\n" % (getmodtime(self.filename), getmodtime(self.pendingfilename)))
      else:
        statsfile.write("%d\n" % getmodtime(self.filename))
      statsfile.write(postatsstring)
      statsfile.close()
    except IOError:
      # TODO: log a warning somewhere. we don't want an error as this is an optimization
      pass

  def calcstats(self):
    """calculates translation statistics for the given po file"""
    if not self.parsed:
      self.readpofile()
    postats = dict([(name, len(items)) for name, items in self.classify.iteritems()])
    self.stats = postats

  def getassigns(self):
    """reads the assigns if neccessary or returns them from the cache"""
    if os.path.exists(self.assignsfilename):
      self.assigns = self.readassigns()
    else:
      self.assigns = {}
    return self.assigns

  def readassigns(self):
    """reads the assigns from the associated assigns file, returning the assigns
    the format is a number of lines consisting of
    username: action: itemranges
    where itemranges is a comma-separated list of item numbers or itemranges like 3-5
    e.g.  pootlewizz: review: 2-99,101"""
    assignsmtime = getmodtime(self.assignsfilename)
    if assignsmtime == getattr(self, "assignsmtime", None):
      return
    assignsstring = open(self.assignsfilename, "r").read()
    poassigns = {}
    for line in assignsstring.split("\n"):
      if not line.strip():
        continue
      if not line.count(":") == 2:
        print "invalid assigns line in", self.assignsfilename, line
        continue
      username, action, itemranges = line.split(":", 2)
      username, action = username.strip(), action.strip()
      if not username in poassigns:
        poassigns[username] = {}
      userassigns = poassigns[username]
      if not action in userassigns:
        userassigns[action] = []
      items = userassigns[action]
      for itemrange in itemranges.split(","):
        if "-" in itemrange:
          if not line.count("-") == 1:
            print "invalid assigns range in", self.assignsfilename, line, itemrange
            continue
          itemstart, itemstop = [int(item.strip()) for item in itemrange.split("-", 1)]
          items.extend(range(itemstart, itemstop+1))
        else:
          item = int(itemrange.strip())
          items.append(item)
      userassigns[action] = items
    return poassigns

  def saveassigns(self):
    """saves the current assigns to file"""
    # assumes self.assigns is up to date
    assignstrings = []
    usernames = self.assigns.keys()
    usernames.sort()
    for username in usernames:
      actions = self.assigns[username].keys()
      actions.sort()
      for action in actions:
        items = self.assigns[username][action]
        items.sort()
        if items:
          lastitem = None
          rangestart = None
          assignstring = "%s: %s: " % (username, action)
          for item in items:
            if item - 1 == lastitem:
              if rangestart is None:
                rangestart = lastitem
            else:
              if rangestart is not None:
                assignstring += "-%d" % lastitem
                rangestart = None
              if lastitem is None:
                assignstring += "%d" % item
              else:
                assignstring += ",%d" % item
            lastitem = item
        if rangestart is not None:
          assignstring += "-%d" % lastitem
        assignstrings.append(assignstring + "\n")
    assignsfile = open(self.assignsfilename, "w")
    assignsfile.writelines(assignstrings)
    assignsfile.close()

  def setmsgstr(self, item, newmsgstr):
    """updates a translation with a new msgstr value"""
    if not self.parsed:
      self.readpofile()
    thepo = self.transelements[item]
    thepo.msgstr = newmsgstr
    thepo.markfuzzy(False)
    self.savepofile()
    self.reclassifyelement(item)

  def classifyelements(self):
    """makes a dictionary of which elements fall into which classifications"""
    self.classify = {}
    self.classify["fuzzy"] = []
    self.classify["blank"] = []
    self.classify["translated"] = []
    self.classify["has-suggestion"] = []
    self.classify["total"] = []
    for checkname in self.checker.getfilters().keys():
      self.classify["check-" + checkname] = []
    for item, poel in enumerate(self.transelements):
      classes = self.classifyelement(poel)
      if self.getsuggestions(item):
        classes.append("has-suggestion")
      for classname in classes:
        self.classify[classname].append(item)

  def classifyelement(self, poel):
    """returns all classify keys that this element should match"""
    classes = ["total"]
    if poel.isfuzzy():
      classes.append("fuzzy")
    if poel.isblankmsgstr():
      classes.append("blank")
    if not ("fuzzy" in classes or "blank" in classes):
      classes.append("translated")
    unquotedid = po.getunquotedstr(poel.msgid, joinwithlinebreak=False)
    unquotedstr = po.getunquotedstr(poel.msgstr, joinwithlinebreak=False)
    failures = self.checker.run_filters(poel, unquotedid, unquotedstr)
    for failure in failures:
      functionname = failure.split(":",2)[0]
      classes.append("check-" + functionname)
    return classes

  def reclassifyelement(self, item):
    """updates the classification of poel in self.classify"""
    poel = self.transelements[item]
    classes = self.classifyelement(poel)
    if self.getsuggestions(item):
      classes.append("has-suggestion")
    for classname, matchingitems in self.classify.items():
      if (classname in classes) != (item in matchingitems):
        if classname in classes:
          self.classify[classname].append(item)
        else:
          self.classify[classname].remove(item)
        self.classify[classname].sort()
    self.calcstats()
    self.savestats()

  def reclassifysuggestions(self):
    """shortcut to only update classification of has-suggestion for all items"""
    suggitems = []
    suggsources = {}
    for thesugg in self.pendingfile.poelements:
      sources = tuple(thesugg.getsources())
      suggsources[sources] = thesugg
    suggitems = [item for item in self.transelements if tuple(item.getsources()) in suggsources]
    havesuggestions = self.classify["has-suggestion"]
    for item, poel in enumerate(self.transelements):
      if (poel in suggitems) != (item in havesuggestions):
        if poel in suggitems:
          havesuggestions.append(item)
        else:
          havesuggestions.remove(item)
        havesuggestions.sort()
    self.calcstats()
    self.savestats()

  def getsuggestions(self, item):
    """find all the suggestion items submitted for the given (pofile or pofilename) and item"""
    self.readpendingfile()
    thepo = self.transelements[item]
    sources = thepo.getsources()
    # TODO: review the matching method
    suggestpos = [suggestpo for suggestpo in self.pendingfile.poelements if suggestpo.getsources() == sources]
    return suggestpos

  def addsuggestion(self, item, suggmsgstr):
    """adds a new suggestion for the given item to the pendingfile"""
    self.readpendingfile()
    thepo = self.transelements[item]
    newpo = thepo.copy()
    newpo.msgstr = suggmsgstr
    newpo.markfuzzy(False)
    self.pendingfile.poelements.append(newpo)
    self.savependingfile()
    self.reclassifyelement(item)

  def deletesuggestion(self, item, suggitem):
    """removes the suggestion from the pending file"""
    self.readpendingfile()
    # TODO: remove the suggestion in a less brutal manner
    del self.pendingfile.poelements[suggitem]
    self.savependingfile()
    self.reclassifyelement(item)

  def iteritems(self, search, lastitem=None):
    """iterates through the items in this pofile starting after the given lastitem
    if matchnames is given only returns items matching one of the given classifications
    if assigncondition is given, as (username, action), only returns items assigned to username for action"""
    # update stats if required
    self.getstats()
    if lastitem is None:
      minitem = 0
    else:
      minitem = lastitem + 1
    maxitem = len(self.transelements)
    validitems = range(minitem, maxitem)
    if search.assigncondition is not None: 
      self.getassigns()
      username, action = search.assigncondition
      assignitems = self.assigns.get(username, {}).get(action, {})
      validitems = [item for item in validitems if item in assignitems]
    for item in validitems:
      if not search.matchnames:
        yield item
      for name in search.matchnames:
        if item in self.classify[name]:
          yield item

class Search:
  """an object containint all the searching information"""
  def __init__(self, dirfilter=None, matchnames=None, assigncondition=None, searchtext=None):
    self.dirfilter = dirfilter
    self.matchnames = matchnames
    self.assigncondition = assigncondition
    self.searchtext = searchtext

class TranslationProject:
  """Manages iterating through the translations in a particular project"""
  def __init__(self, languagecode, projectcode, potree):
    self.languagecode = languagecode
    self.projectcode = projectcode
    self.potree = potree
    self.languagename = self.potree.getlanguagename(self.languagecode)
    self.projectname = self.potree.getprojectname(self.projectcode)
    self.podir = potree.getpodir(languagecode, projectcode)
    self.pofilenames = potree.getpofiles(languagecode, projectcode)
    checkerclasses = [checks.projectcheckers.get(projectcode, checks.StandardChecker), pofilter.StandardPOChecker]
    self.checker = pofilter.POTeeChecker(checkerclasses=checkerclasses)
    self.pofiles = {}
    self.initpootlefiles()

  def browsefiles(self, dirfilter=None, depth=None, maxdepth=None, includedirs=False, includefiles=True):
    """gets a list of pofilenames, optionally filtering with the parent directory"""
    if dirfilter is None:
      pofilenames = self.pofilenames
    else:
      if not dirfilter.endswith(os.path.sep) and not dirfilter.endswith(os.path.extsep + "po"):
        dirfilter += os.path.sep
      pofilenames = [pofilename for pofilename in self.pofilenames if pofilename.startswith(dirfilter)]
    if includedirs:
      podirs = {}
      for pofilename in pofilenames:
        dirname = os.path.dirname(pofilename)
	if not dirname:
	  continue
        podirs[dirname] = True
	while dirname:
	  dirname = os.path.dirname(dirname)
	  if dirname:
	    podirs[dirname] = True
      podirs = podirs.keys()
    else:
      podirs = []
    if not includefiles:
      pofilenames = []
    if maxdepth is not None:
      pofilenames = [pofilename for pofilename in pofilenames if pofilename.count(os.path.sep) <= maxdepth]
      podirs = [podir for podir in podirs if podir.count(os.path.sep) <= maxdepth]
    if depth is not None:
      pofilenames = [pofilename for pofilename in pofilenames if pofilename.count(os.path.sep) == depth]
      podirs = [podir for podir in podirs if podir.count(os.path.sep) == depth]
    return pofilenames + podirs

  def iterpofilenames(self, lastpofilename=None, includelast=False):
    """iterates through the pofilenames starting after the given pofilename"""
    if lastpofilename is None:
      index = 0
    else:
      index = self.pofilenames.index(lastpofilename)
      if not includelast:
        index += 1
    while index < len(self.pofilenames):
      yield self.pofilenames[index]
      index += 1

  def searchpofilenames(self, lastpofilename, search, includelast=False):
    """find the next pofilename that has items matching one of the given classification names"""
    for pofilename in self.iterpofilenames(lastpofilename, includelast):
      # TODO: handle assigncondition
      if search.dirfilter is not None and not pofilename.startswith(search.dirfilter):
        continue
      if not search.matchnames:
        yield pofilename
      postats = self.getpostats(pofilename)
      for name in search.matchnames:
        if postats[name]:
          yield pofilename

  def searchpoitems(self, pofilename, item, search):
    """finds the next item matching one of the given classification names"""
    if search.searchtext:
      pogrepfilter = pogrep.pogrepfilter(search.searchtext, None, ignorecase=True)
    for pofilename in self.searchpofilenames(pofilename, search, includelast=True):
      pofile = self.getpofile(pofilename)
      for item in pofile.iteritems(search, item):
        # TODO: move this to iteritems
        if search.searchtext:
          thepo = pofile.transelements[item]
          if pogrepfilter.filterelement(thepo):
            yield pofilename, item
        else:
          yield pofilename, item

  def gettranslationsession(self, session):
    """gets the user's translationsession"""
    if not hasattr(session, "translationsessions"):
      session.translationsessions = {}
    if not (self.languagecode, self.projectcode) in session.translationsessions:
      session.translationsessions[self.languagecode, self.projectcode] = TranslationSession(self, session)
    return session.translationsessions[self.languagecode, self.projectcode]

  def initpootlefiles(self):
    """sets up pootle files (without neccessarily parsing them)"""
    for pofilename in self.pofilenames:
      self.pofiles[pofilename] = pootlefile(self, pofilename)

  def calculatestats(self, pofilenames=None):
    """calculates translation statistics for the given po files (or all if None given)"""
    totalstats = {}
    if pofilenames is None:
      pofilenames = self.pofilenames
    for pofilename in pofilenames:
      if not pofilename or os.path.isdir(pofilename):
        continue
      postats = self.getpostats(pofilename)
      for name, count in postats.iteritems():
        totalstats[name] = totalstats.get(name, 0) + count
    return totalstats

  def getpostats(self, pofilename):
    """calculates translation statistics for the given po file"""
    return self.pofiles[pofilename].getstats()

  def getpofile(self, pofilename):
    """parses the file into a pofile object and stores in self.pofiles"""
    pofile = self.pofiles[pofilename]
    if not pofile.parsed:
      pofile.readpofile()
    return pofile

  def getpofilelen(self, pofilename):
    """returns number of items in the given pofilename"""
    # TODO: needn't parse the file for this ...
    pofile = self.getpofile(pofilename)
    return len(pofile.transelements)

  def getitem(self, pofilename, item):
    """returns a particular item from a particular po file's orig, trans strings as a tuple"""
    pofile = self.getpofile(pofilename)
    thepo = pofile.transelements[item]
    orig, trans = po.getunquotedstr(thepo.msgid), po.getunquotedstr(thepo.msgstr)
    return orig, trans

  def getitemclasses(self, pofilename, item):
    """returns which classes this item belongs to"""
    # TODO: needn't parse the file for this ...
    pofile = self.getpofile(pofilename)
    return [classname for (classname, classitems) in pofile.classify.iteritems() if item in classitems]

  def getitems(self, pofilename, itemstart, itemstop):
    """returns a set of items from the pofile, converted to original and translation strings"""
    pofile = self.getpofile(pofilename)
    elements = pofile.transelements[max(itemstart,0):itemstop]
    return [(po.getunquotedstr(poel.msgid), po.getunquotedstr(poel.msgstr)) for poel in elements]

  def updatetranslation(self, pofilename, item, trans):
    """updates a translation with a new value..."""
    newmsgstr = [quote.quotestr(transpart) for transpart in trans.split("\n")]
    pofile = self.pofiles[pofilename]
    pofile.setmsgstr(item, newmsgstr)

  def suggesttranslation(self, pofilename, item, trans):
    """stores a new suggestion for a translation..."""
    suggmsgstr = [quote.quotestr(transpart) for transpart in trans.split("\n")]
    pofile = self.getpofile(pofilename)
    pofile.addsuggestion(item, suggmsgstr)

  def getsuggestions(self, pofile, item):
    """find all the suggestions submitted for the given (pofile or pofilename) and item"""
    if isinstance(pofile, (str, unicode)):
      pofilename = pofile
      pofile = self.getpofile(pofilename)
    suggestpos = pofile.getsuggestions(item)
    suggestions = [po.getunquotedstr(suggestpo.msgstr) for suggestpo in suggestpos]
    return suggestions

  def acceptsuggestion(self, pofile, item, suggitem, newtrans):
    """accepts the suggestion into the main pofile"""
    if isinstance(pofile, (str, unicode)):
      pofilename = pofile
      pofile = self.getpofile(pofilename)
    pofile.deletesuggestion(item, suggitem)
    self.updatetranslation(pofilename, item, newtrans)

  def rejectsuggestion(self, pofile, item, suggitem, newtrans):
    """rejects the suggestion and removes it from the pending file"""
    if isinstance(pofile, (str, unicode)):
      pofilename = pofile
      pofile = self.getpofile(pofilename)
    pofile.deletesuggestion(item, suggitem)

  def savepofile(self, pofilename):
    """saves changes to disk..."""
    pofile = self.getpofile(pofilename)
    pofile.savepofile()

  def getsource(self, pofilename):
    """returns pofile source"""
    pofile = self.getpofile(pofilename)
    return pofile.getsource()

  def getcsv(self, csvfilename):
    """returns pofile as csv"""
    pofilename = csvfilename.replace(".csv", ".po")
    pofile = self.getpofile(pofilename)
    return pofile.getcsv()

class POTree:
  """Manages the tree of projects and languages"""
  def __init__(self, instance):
    self.languages = instance.languages
    self.projects = instance.projects
    self.directories = instance.directories
    self.projectcache = {}

  def haslanguage(self, languagecode):
    """checks if this language exists"""
    return hasattr(self.languages, languagecode)

  def getlanguageprefs(self, languagecode):
    """returns the language object"""
    return getattr(self.languages, languagecode)

  def getlanguagename(self, languagecode):
    """returns the language's full name"""
    return getattr(self.getlanguageprefs(languagecode), "fullname", languagecode)

  def getlanguagecodes(self, projectcode=None):
    """returns a list of valid languagecodes for a given project or all projects"""
    languagecodes = [languagecode for languagecode, language in self.languages.iteritems()]
    languagecodes.sort()
    if projectcode is None:
      return languagecodes
    else:
      return [languagecode for languagecode in languagecodes if self.hasproject(languagecode, projectcode)]

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
    if not self.haslanguage(languagecode):
      return False
    try:
      podir = self.getpodir(languagecode, projectcode)
      return True
    except IndexError:
      return False

  def getproject(self, languagecode, projectcode):
    """returns the project object for the languagecode and projectcode"""
    if (languagecode, projectcode) not in self.projectcache:
      self.projectcache[languagecode, projectcode] = TranslationProject(languagecode, projectcode, self)
    return self.projectcache[languagecode, projectcode]

  def getprojectname(self, projectcode):
    """returns the full name of the project"""
    projectprefs = getattr(self.projects, projectcode)
    return getattr(projectprefs, "fullname", projectcode)

  def getpodir(self, languagecode, projectcode):
    """returns the base directory containing po files for the project"""
    search = self.getdirpattern(languagecode, projectcode)
    if isinstance(search, (str, unicode)):
      return search
    elif search is not None:
      directoryname = search.directory.replace("$project", projectcode).replace("$language", languagecode)
      if os.path.exists(directoryname):
        return directoryname
    raise IndexError("directory not found for language %s, project %s" % (languagecode, projectcode))

  def getdirpattern(self, languagecode, projectcode):
    """returns either a directory name or a prefs node indicating how to construct the directory name"""
    for searchname, search in self.directories.iteritems():
      if isinstance(search, (str, unicode)):
        directoryname = search.replace("$project", projectcode).replace("$language", languagecode)
        if os.path.exists(directoryname):
          return directoryname
      else:
        directorypattern = search.directory
        if hasattr(search, "projectcode"):
          if search.projectcode != projectcode:
            continue
        if hasattr(search, "languagecode"):
          if search.languagecode != languagecode:
            continue
        directoryname = search.directory.replace("$project", projectcode).replace("$language", languagecode)
        if not os.path.exists(directoryname):
          continue
        return search
    return None

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
      languageponame = languagecode + os.extsep + "po"
      ponames = [fname for fname in fnames if fname == languageponame]
      pofilenames.extend([os.path.join(basedirname, poname) for poname in ponames])
    pofilenames = []
    podir = self.getpodir(languagecode, projectcode)
    search = self.getdirpattern(languagecode, projectcode)
    if isinstance(search, (str, unicode)):
      dirstyle = "standard"
    else:
      dirstyle = getattr(search, "dirstyle", "standard")
    if dirstyle == "standard":
      os.path.walk(podir, addfiles, podir)
    elif dirstyle == "gnu":
      os.path.walk(podir, addgnufiles, podir)
    return pofilenames

  def refreshstats(self):
    """manually refreshes all the stats files"""
    for projectcode in self.getprojectcodes():
      print "Project %s:" % (projectcode)
      for languagecode in self.getlanguagecodes(projectcode):
        print "Project %s, Language %s:" % (projectcode, languagecode)
        translationproject = self.getproject(languagecode, projectcode)
        translationproject.stats = {}
        for pofilename in translationproject.pofilenames:
          translationproject.getpostats(pofilename)
          print ".",
        print

