#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""manages po files and their associated files"""

from translate.storage import base
from translate.storage import po
from translate.misc import quote
from translate.misc.multistring import multistring
from translate.filters import checks
from Pootle import __version__
from jToolkit import timecache
from jToolkit import glock
import time
import os

def getmodtime(filename, default=None):
  """gets the modificationtime of the given file"""
  if os.path.exists(filename):
    return os.stat(filename)[os.path.stat.ST_MTIME]
  else:
    return default

def wordcount(unquotedstr):
  """returns the number of words in an unquoted str"""
  return len(unquotedstr.split())

class Wrapper(object):
  """An object which wraps an inner object, delegating to the encapsulated methods etc"""
  def __getattr__(self, attrname, *args):
    if attrname in self.__dict__:
      return self.__dict__[attrname]
    return getattr(self.__dict__["__innerobj__"], attrname, *args)

  def __setattr__(self, attrname, value):
    if attrname == "__innerobj__":
      self.__dict__[attrname] = value
    elif attrname in self.__dict__:
      if isinstance(self.__dict__[attrname], property):
        self.__dict__[attrname].fset(value)
      else:
        self.__dict__[attrname] = value
    elif attrname in self.__class__.__dict__:
      if isinstance(self.__class__.__dict__[attrname], property):
        self.__class__.__dict__[attrname].fset(self, value)
      else:
        self.__dict__[attrname] = value
    else:
      return setattr(self.__dict__["__innerobj__"], attrname, value)

class pootleunit(base.TranslationUnit, Wrapper):
  """a pounit with helpful methods for pootle"""
  WrapUnitClass = po.pounit
  def __init__(self, source=None, encoding="UTF-8", wrapunit=None):
    # self.__innerobj__ must be the first attribute set
    if wrapunit is None:
      self.__innerobj__ = self.WrapUnitClass()
    else:
      self.__innerobj__ = wrapunit
    self.encoding = po.encodingToUse(encoding)
    if source is not None:
      self.source = source

  def __getattr__(self, attrname, *args):
    if attrname in self.__dict__:
      return self.__dict__[attrname]
    return getattr(self.__dict__["__innerobj__"], attrname, *args)

  def __setattr__(self, attrname, value):
    if attrname == "__innerobj__":
      self.__dict__[attrname] = value
    elif attrname in self.__dict__:
      if isinstance(self.__dict__[attrname], property):
        self.__dict__[attrname].fset(value)
      else:
        self.__dict__[attrname] = value
    elif attrname in self.__class__.__dict__:
      if isinstance(self.__class__.__dict__[attrname], property):
        self.__class__.__dict__[attrname].fset(self, value)
      else:
        self.__dict__[attrname] = value
    else:
      return setattr(self.__dict__["__innerobj__"], attrname, value)

  def __str__(self):
    return self.__innerobj__.__str__()

  def parse(self, src):
    return self.__innerobj__.parse(src)

  def getsource(self):
    return self.__innerobj__.source

  def setsource(self, source):
    self.__innerobj__.source = source
  source = property(getsource, setsource)

  def gettarget(self):
    return self.__innerobj__.target

  def settarget(self, target):
    self.__innerobj__.target = target
  target = property(gettarget, settarget)

  def getlocations(self):
    return self.__innerobj__.getlocations()

  def hasplural(self):
    return self.__innerobj__.hasplural()

  def merge(self, otherunit, overwrite=False, comments=True):
    if isinstance(otherunit, pootleunit):
      return self.__innerobj__.merge(otherunit.__innerobj__, overwrite=overwrite, comments=comments)
    else:
      return self.__innerobj__.merge(otherunit, overwrite=overwrite, comments=comments)

  # TODO: try and replace with underlying baseunit properties as much as possible
  def getunquotedmsgid(self):
    """returns the msgid as a list of unquoted strings (one per plural form present)"""
    if self.hasplural():
      return self.source.strings
    else:
      return [self.source]
  unquotedmsgid = property(getunquotedmsgid)

  def getunquotedmsgstr(self):
    """returns the msgstr as a list of unquoted strings (one per plural form present)"""
    if self.hasplural() and isinstance(self.target, multistring):
      return self.target.strings
    else:
      return [self.target]

  def setunquotedmsgstr(self, text):
    """quotes text in po-style"""
    if isinstance(text, dict):
      self.target = dict([(key, value.replace("\r\n", "\n")) for key, value in text.items()])
    elif isinstance(text, list):
      if not self.hasplural() and len(text) != 1:
        raise ValueError("po unit has no plural but msgstr has %d elements (%s)" % (len(text), text))
      self.target = [value.replace("\r\n", "\n") for value in text]
    else:
      self.target = text.replace("\r\n", "\n")

  unquotedmsgstr = property(getunquotedmsgstr, setunquotedmsgstr)

  def classify(self, checker):
    """returns all classify keys that this unit should match, using the checker"""
    classes = ["total"]
    if self.isfuzzy():
      classes.append("fuzzy")
    if self.isblankmsgstr():
      classes.append("blank")
    if not ("fuzzy" in classes or "blank" in classes):
      classes.append("translated")
    # TODO: we don't handle checking plurals at all yet, as this is tricky...
    unquotedid = self.unquotedmsgid[0]
    unquotedstr = self.unquotedmsgstr[0]
    if isinstance(unquotedid, str) and isinstance(unquotedstr, unicode):
      unquotedid = unquotedid.decode(getattr(self, "encoding", "utf-8"))
    filterresult = checker.run_filters(self, unquotedid, unquotedstr)
    for filtername, filtermessage in filterresult:
      classes.append("check-" + filtername)
    return classes

class pootlestatistics:
  """this represents the statistics known about a file"""
  def __init__(self, basefile, generatestats=True):
    """constructs statistic object for the given file"""
    # TODO: try and remove circular references between basefile and this class
    self.basefile = basefile
    self.statsfilename = self.basefile.filename + os.extsep + "stats"
    self.classify = {}
    self.msgidwordcounts = []
    self.msgstrwordcounts = []
    if generatestats:
      self.getstats()

  def getstats(self):
    """reads the stats if neccessary or returns them from the cache"""
    if os.path.exists(self.statsfilename):
      try:
        self.readstats()
      except Exception, e:
        print "Error reading stats from %s, so recreating (Error was %s)" % (self.statsfilename, e)
        raise
        self.statspomtime = None
    pomtime = getmodtime(self.basefile.filename)
    lastpomtime = getattr(self, "statspomtime", None)
    if pomtime is None or pomtime != lastpomtime:
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
    elif len(mtimes) == 2:
      frompomtime = int(mtimes[0])
    postats = {}
    msgidwordcounts = []
    msgstrwordcounts = []
    for line in postatsstring.split("\n"):
      if not line.strip():
        continue
      if not ":" in line:
        print "invalid stats line in", self.statsfilename,line
        continue
      name, items = line.split(":", 1)
      if name == "msgidwordcounts":
        msgidwordcounts = [[int(subitem.strip()) for subitem in item.strip().split("/")] for item in items.strip().split(",") if item]
      elif name == "msgstrwordcounts":
        msgstrwordcounts = [[int(subitem.strip()) for subitem in item.strip().split("/")] for item in items.strip().split(",") if item]
      else:
        items = [int(item.strip()) for item in items.strip().split(",") if item]
        postats[name.strip()] = items
    # save all the read times, data simultaneously
    self.statspomtime, self.statsmtime, self.stats, self.msgidwordcounts, self.msgstrwordcounts = frompomtime, statsmtime, postats, msgidwordcounts, msgstrwordcounts
    # if in old-style format (counts instead of items), recalculate
    totalitems = postats.get("total", [])
    if len(totalitems) == 1 and totalitems[0] != 0:
      self.calcstats()
      self.savestats()
    if (len(msgidwordcounts) < len(totalitems)) or (len(msgstrwordcounts) < len(totalitems)):
      self.basefile.pofreshen()
      self.countwords()
      self.savestats()

  def savestats(self):
    """saves the current statistics to file"""
    if not os.path.exists(self.basefile.filename):
      if os.path.exists(self.statsfilename):
        os.remove(self.statsfilename)
      return
    # assumes self.stats is up to date
    try:
      postatsstring = "\n".join(["%s:%s" % (name, ",".join(map(str,items))) for name, items in self.stats.iteritems()])
      wordcountsstring = "msgidwordcounts:" + ",".join(["/".join(map(str,subitems)) for subitems in self.msgidwordcounts])
      wordcountsstring += "\nmsgstrwordcounts:" + ",".join(["/".join(map(str,subitems)) for subitems in self.msgstrwordcounts])
      statsfile = open(self.statsfilename, "w")
      statsfile.write("%d\n" % getmodtime(self.basefile.filename))
      statsfile.write(postatsstring + "\n" + wordcountsstring)
      statsfile.close()
    except IOError:
      # TODO: log a warning somewhere. we don't want an error as this is an optimization
      pass
    self.updatequickstats()

  def updatequickstats(self):
    """updates the project's quick stats on this file"""
    translated = self.stats.get("translated")
    translatedwords = sum([sum(self.msgidwordcounts[item]) for item in translated if 0 <= item < len(self.msgidwordcounts)])
    totalwords = sum([sum(partcounts) for partcounts in self.msgidwordcounts])
    self.basefile.project.updatequickstats(self.basefile.pofilename, translatedwords, len(translated), totalwords, len(self.msgidwordcounts))

  def calcstats(self):
    """calculates translation statistics for the given po file"""
    # handle this being called when self.basefile.statistics is being set and calcstats is called from self.__init__
    if not hasattr(self.basefile, "statistics"):
      self.basefile.statistics = self
    self.basefile.pofreshen()
    postats = dict([(name, items) for name, items in self.classify.iteritems()])
    self.stats = postats

  def classifyunits(self):
    """makes a dictionary of which units fall into which classifications"""
    self.classify = {}
    self.classify["fuzzy"] = []
    self.classify["blank"] = []
    self.classify["translated"] = []
    self.classify["has-suggestion"] = []
    self.classify["total"] = []
    for checkname in self.basefile.checker.getfilters().keys():
      self.classify["check-" + checkname] = []
    for item, poel in enumerate(self.basefile.transunits):
      classes = poel.classify(self.basefile.checker)
      for classname in classes:
        if classname in self.classify:
          self.classify[classname].append(item)
        else:
          self.classify[classname] = item
    self.countwords()

  def countwords(self):
    """counts the words in each of the units"""
    self.msgidwordcounts = []
    self.msgstrwordcounts = []
    for poel in self.basefile.transunits:
      self.msgidwordcounts.append([wordcount(text) for text in poel.unquotedmsgid])
      self.msgstrwordcounts.append([wordcount(text) for text in poel.unquotedmsgstr])

  def reclassifyunit(self, item):
    """updates the classification of poel in self.classify"""
    poel = self.basefile.transunits[item]
    self.msgidwordcounts[item] = [wordcount(text) for text in poel.unquotedmsgid]
    self.msgstrwordcounts[item] = [wordcount(text) for text in poel.unquotedmsgstr]
    classes = poel.classify(self.basefile.checker)
    for classname, matchingitems in self.classify.items():
      if (classname in classes) != (item in matchingitems):
        if classname in classes:
          self.classify[classname].append(item)
        else:
          self.classify[classname].remove(item)
        self.classify[classname].sort()
    self.calcstats()
    self.savestats()

  def getitemslen(self):
    """gets the number of items in the file"""
    # TODO: simplify this, and use wherever its needed
    if hasattr(self.basefile, "transunits"):
      return len(self.basefile.transunits)
    elif hasattr(self, "stats") and "total" in self.stats:
      return len(self.stats["total"])
    elif hasattr(self, "classify") and "total" in self.classify:
      return len(self.classify["total"])
    else:
      # we hadn't read stats...
      return len(self.getstats()["total"])

class LockedFile:
  """locked interaction with a filesystem file"""
  def __init__(self, filename):
    self.filename = filename
    self.lock = glock.GlobalLock(self.filename + os.extsep + "lock")

  def readmodtime(self):
    """returns the modification time of the file (locked operation)"""
    self.lock.acquire()
    try:
      return getmodtime(self.filename)
    finally:
      self.lock.forcerelease()

  def getcontents(self):
    """returns modtime, contents tuple (locked operation)"""
    self.lock.acquire()
    try:
      pomtime = getmodtime(self.filename)
      filecontents = open(self.filename, 'r').read()
      return pomtime, filecontents
    finally:
      self.lock.forcerelease()

  def writecontents(self, contents):
    """writes contents to file, returning modification time (locked operation)"""
    self.lock.acquire()
    try:
      f = open(self.filename, 'w')
      f.write(contents)
      f.close()
      pomtime = getmodtime(self.filename)
      return pomtime
    finally:
      self.lock.release()

class pootleassigns:
  """this represents the assignments for a file"""
  def __init__(self, basefile):
    """constructs assignments object for the given file"""
    # TODO: try and remove circular references between basefile and this class
    self.basefile = basefile
    self.assignsfilename = self.basefile.filename + os.extsep + "assigns"
    self.getassigns()

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
    itemcount = len(getattr(self, "classify", {}).get("total", []))
    for line in assignsstring.split("\n"):
      if not line.strip():
        continue
      if not line.count(":") == 2:
        print "invalid assigns line in %s: %r" % (self.assignsfilename, line)
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
          if not itemrange.count("-") == 1:
            print "invalid assigns range in %s: %r (from line %r)" % (self.assignsfilename, itemrange, line)
            continue
          itemstart, itemstop = [int(item.strip()) for item in itemrange.split("-", 1)]
          items.extend(range(itemstart, itemstop+1))
        else:
          item = int(itemrange.strip())
          items.append(item)
      if itemcount:
        items = [item for item in items if 0 <= item < itemcount]
      userassigns[action] = items
    return poassigns

  def assignto(self, item, username, action):
    """assigns the item to the given username for the given action"""
    userassigns = self.assigns.setdefault(username, {})
    items = userassigns.setdefault(action, [])
    if item not in items:
      items.append(item)
    self.saveassigns()

  def unassign(self, item, username=None, action=None):
    """removes assignments of the item to the given username (or all users) for the given action (or all actions)"""
    if username is None:
      usernames = self.assigns.keys()
    else:
      usernames = [username]
    for username in usernames:
      userassigns = self.assigns.setdefault(username, {})
      if action is None:
        itemlist = [userassigns.get(action, []) for action in userassigns]
      else:
        itemlist = [userassigns.get(action, [])]
      for items in itemlist:
        if item in items:
          items.remove(item)
    self.saveassigns()

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

  def getunassigned(self, action=None):
    """gets all strings that are unassigned (for the given action if given)"""
    unassigneditems = range(0, self.statistics.getitemslen())
    assigns = self.getassigns()
    for username in self.assigns:
      if action is not None:
        assigneditems = self.assigns[username].get(action, [])
      else:
        assigneditems = []
        for action, actionitems in self.assigns[username].iteritems():
          assigneditems += actionitems
      unassigneditems = [item for item in unassigneditems if item not in assigneditems]
    return unassigneditems

  def finditems(self, search):
    """returns items that match the .assignedto and/or .assignedaction criteria in the searchobject"""
    # search.assignedto == [None] means assigned to nobody
    if search.assignedto == [None]:
      assignitems = self.getunassigned(search.assignedaction)
    else:
      # filter based on assign criteria
      assigns = self.getassigns()
      if search.assignedto:
        usernames = [search.assignedto]
      else:
        usernames = assigns.iterkeys()
      assignitems = []
      for username in usernames:
        if search.assignedaction:
          actionitems = assigns[username].get(search.assignedaction, [])
          assignitems.extend(actionitems)
        else:
          for actionitems in assigns[username].itervalues():
            assignitems.extend(actionitems)
    return assignitems

class pootlefile(po.pofile):
  """this represents a pootle-managed .po file and its associated files"""
  x_generator = "Pootle %s" % __version__.ver
  def __init__(self, project=None, pofilename=None, stats=True):
    po.pofile.__init__(self, unitclass=pootleunit)
    self.pofilename = pofilename
    if project is None:
      from Pootle import projects
      self.project = projects.DummyProject(None)
      self.checker = None
      self.filename = self.pofilename
    else:
      self.project = project
      self.checker = self.project.checker
      self.filename = os.path.join(self.project.podir, self.pofilename)
    self.lockedfile = LockedFile(self.filename)
    # we delay parsing until it is required
    self.pomtime = None
    self.statistics = pootlestatistics(self, stats)
    self.assigns = pootleassigns(self)
    self.tracker = timecache.timecache(20*60)

  def track(self, item, message):
    """sets the tracker message for the given item"""
    self.tracker[item] = message

  def readpofile(self):
    """reads and parses the main po file"""
    # make sure encoding is reset so it is read from the file
    self.encoding = None
    self.units = []
    pomtime, filecontents = self.lockedfile.getcontents()
    # note: we rely on this not resetting the filename, which we set earlier, when given a string
    self.parse(filecontents)
    # we ignore all the headers by using this filtered set
    self.transunits = [poel for poel in self.units if not (poel.isheader() or poel.isblank())]
    self.statistics.classifyunits()
    self.pomtime = pomtime

  def savepofile(self):
    """saves changes to the main file to disk..."""
    output = str(self)
    self.pomtime = self.lockedfile.writecontents(output)

  def pofreshen(self):
    """makes sure we have a freshly parsed pofile"""
    if not os.path.exists(self.filename):
      # the file has been removed, update the project index (and fail below)
      self.project.scanpofiles()
    if self.pomtime != self.lockedfile.readmodtime():
      self.readpofile()

  def getoutput(self):
    """returns pofile output"""
    self.pofreshen()
    return super(pootlefile, self).getoutput()

  def setmsgstr(self, item, newmsgstr, userprefs, languageprefs):
    """updates a translation with a new msgstr value"""
    self.pofreshen()
    thepo = self.transunits[item]
    thepo.unquotedmsgstr = newmsgstr
    thepo.markfuzzy(False)
    po_revision_date = time.strftime("%F %H:%M%z")
    headerupdates = {"PO_Revision_Date": po_revision_date, "X_Generator": self.x_generator}
    if userprefs:
      if getattr(userprefs, "name", None) and getattr(userprefs, "email", None):
        headerupdates["Last_Translator"] = "%s <%s>" % (userprefs.name, userprefs.email)
    self.updateheader(add=True, **headerupdates)
    if languageprefs:
      nplurals = getattr(languageprefs, "nplurals", None)
      pluralequation = getattr(languageprefs, "pluralequation", None)
      if nplurals and pluralequation:
        self.updateheaderplural(nplurals, pluralequation)
    self.savepofile()
    self.statistics.reclassifyunit(item)

  def iteritems(self, search, lastitem=None):
    """iterates through the items in this pofile starting after the given lastitem, using the given search"""
    # update stats if required
    self.statistics.getstats()
    if lastitem is None:
      minitem = 0
    else:
      minitem = lastitem + 1
    maxitem = len(self.transunits)
    validitems = range(minitem, maxitem)
    if search.assignedto or search.assignedaction:
      assignitems = self.assigns.finditems(search)
      validitems = [item for item in validitems if item in assignitems]
    # loop through, filtering on matchnames if required
    for item in validitems:
      if not search.matchnames:
        yield item
      for name in search.matchnames:
        if item in self.statistics.classify[name]:
          yield item

  def matchitems(self, newpofile, uselocations=False):
    """matches up corresponding items in this pofile with the given newpofile, and returns tuples of matching poitems (None if no match found)"""
    if not hasattr(self, "sourceindex"):
      self.makeindex()
    if not hasattr(newpofile, "sourceindex"):
      newpofile.makeindex()
    matches = []
    for newpo in newpofile.units:
      if newpo.isheader():
        continue
      foundid = False
      if uselocations:
        newlocations = newpo.getlocations()
        mergedlocations = []
        for location in newlocations:
          if location in mergedlocations:
            continue
          if location in self.locationindex:
            oldpo = self.locationindex[location]
            if oldpo is not None:
              foundid = True
              matches.append((oldpo, newpo))
              mergedlocations.append(location)
              continue
      if not foundid:
        msgid = newpo.source
        if msgid in self.sourceindex:
          oldpo = self.sourceindex[msgid]
          matches.append((oldpo, newpo))
        else:
          matches.append((None, newpo))
    # find items that have been removed
    matcheditems = [oldpo for oldpo, newpo in matches if oldpo]
    for oldpo in self.units:
      if not oldpo in matcheditems:
        matches.append((oldpo, None))
    return matches

  def mergeitem(self, oldpo, newpo, username):
    """merges any changes from newpo into oldpo"""
    unchanged = oldpo.target == newpo.target
    if oldpo.isblankmsgstr() or newpo.isblankmsgstr() or oldpo.isheader() or newpo.isheader() or unchanged:
      oldpo.merge(newpo)
    else:
      for item, matchpo in enumerate(self.transunits):
        if matchpo == oldpo:
          # TODO: copy over old
          raise NotImplementedError("need to add code for merging without suggestions")
          # self.addsuggestion(item, newpo.unquotedmsgstr, username)
          return
      raise KeyError("Could not find item for merge")

  def mergefile(self, newpofile, username, allownewstrings=True):
    """make sure each msgid is unique ; merge comments etc from duplicates into original"""
    self.makeindex()
    matches = self.matchitems(newpofile)
    for oldpo, newpo in matches:
      if oldpo is None:
        if allownewstrings:
          self.units.append(newpo)
      elif newpo is None:
        # TODO: mark the old one as obsolete
        pass
      else:
        self.mergeitem(oldpo, newpo, username)
        # we invariably want to get the ids (source locations) from the newpo
        oldpo.sourcecomments = newpo.sourcecomments

    #Let's update selected header entries. Only the ones listed below, and ones
    #that are empty in self can be updated. The check in header_order is just
    #a basic sanity check so that people don't insert garbage.
    updatekeys = ['Content-Type', 
                  'POT-Creation-Date', 
                  'Last-Translator', 
                  'Project-Id-Version', 
                  'PO-Revision-Date', 
                  'Language-Team']
    headerstoaccept = {}
    ownheader = self.parseheader()
    for (key, value) in newpofile.parseheader().items():
      if key in updatekeys or (not key in ownheader or not ownheader[key]) and key in self.header_order:
        headerstoaccept[key] = value
    self.updateheader(add=True, **headerstoaccept)
    
    #Now update the comments above the header:
    header = self.header()
    newheader = newpofile.header()
    if header is None and not newheader is None:
      header = self.UnitClass("", encoding=self.encoding)
      header.target = ""
    if header:
      header.initallcomments(blankall=True)
      if newheader:
        for i in range(len(header.allcomments)):
          header.allcomments[i].extend(newheader.allcomments[i])
    
    self.savepofile()
    # the easiest way to recalculate everything
    self.readpofile()

class Search:
  """an object containing all the searching information"""
  def __init__(self, dirfilter=None, matchnames=[], assignedto=None, assignedaction=None, searchtext=None):
    self.dirfilter = dirfilter
    self.matchnames = matchnames
    self.assignedto = assignedto
    self.assignedaction = assignedaction
    self.searchtext = searchtext

  def copy(self):
    """returns a copy of this search"""
    return Search(self.dirfilter, self.matchnames, self.assignedto, self.assignedaction, self.searchtext)

