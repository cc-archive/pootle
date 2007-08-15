import os
from translate.storage import statsdb
from translate.filters import checks

def getmodtime(filename, default=None):
  """gets the modificationtime of the given file"""
  if os.path.exists(filename):
    return os.stat(filename)[os.path.stat.ST_MTIME]
  else:
    return default

class StatsFile:
  """Manages a statistics data file"""
  def __init__(self, basefile):
    self.basefile = basefile
    self.refname = self.basefile.filename
    self.filename = self.refname + os.extsep + "stats"

  def read(self):
    """return the contents of the stats file"""
    sfile =  open(self.filename, "r")
    contents = sfile.read()
    sfile.close()
    return contents

  def save(self, statsstring):
    """save the stats data"""
    sfile = open(self.filename, "w")
    if os.path.exists(self.basefile.pendingfilename):
      sfile.write("%d %d\n" % (getmodtime(self.basefile.filename), getmodtime(self.basefile.pendingfilename)))
    else:
      sfile.write("%d\n" % getmodtime(self.basefile.filename))
    sfile.write(statsstring)
    sfile.close()

  def hasparent(self):
    """check if the stats file has a parent data file, if not delete it"""
    if os.path.exists(self.basefile.filename):
      return True
    else:
      if os.path.exists(self.filename):
        os.remove(self.filename)
      return False

class pootlestatistics:
  """this represents the statistics known about a file"""
  def __init__(self, basefile, generatestats=True):
    """constructs statistic object for the given file"""
    # TODO: try and remove circular references between basefile and this class
    self.basefile = basefile
    self.sfile = StatsFile(self.basefile)
    self.classify = {}
    self.sourcewordcounts = []
    self.targetwordcounts = []
    self.stats = {}
    self.totals = {}
    if generatestats:
      self.getstats()

  def getquickstats(self):
    """returns the quick statistics (totals only)"""
    if not self.totals:
      statscache = statsdb.StatsCache()
      self.totals = statscache.filetotals(self.basefile.filename)
    return self.totals

  def getstats(self):
    """reads the stats if neccessary or returns them from the cache"""
    if not self.stats:
      statscache = statsdb.StatsCache()
      self.stats = statscache.filestats(self.basefile.filename, self.basefile.checker)
    return self.stats

  def updatequickstats(self, save=True):
    """updates the project's quick stats on this file"""
    totals = self.getquickstats()
    self.basefile.project.updatequickstats(self.basefile.pofilename, 
        totals["translatedsourcewords"], totals["translated"], 
        totals["fuzzysourcewords"], totals["fuzzy"],
        totals["totalsourcewords"], totals["total"],
        save)

  def classifyunit(self, unit):
    """returns all classify keys that the unit should match"""
    # XXX: This is used to enable iteration through a check, for example. We 
    # probably want to do that directly from the database, if locking allows
    # us.
    classes = ["total"]
    if unit.isfuzzy():
      classes.append("fuzzy")
    if unit.gettargetlen() == 0:
      classes.append("blank")
    if unit.istranslated():
      classes.append("translated")
    checkresult = self.basefile.checker.run_filters(unit)
    for checkname, checkmessage in checkresult:
      classes.append("check-" + checkname)
    return classes

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
    for item, unit in enumerate(self.basefile.transunits):
      classes = self.classifyunit(unit)
      if self.basefile.getsuggestions(item):
        classes.append("has-suggestion")
      for classname in classes:
        if classname in self.classify:
          self.classify[classname].append(item)
        else:
          self.classify[classname] = item
    self.countwords()

  def countwords(self):
    """counts the words in each of the units"""
    self.sourcewordcounts = []
    self.targetwordcounts = []
    for unit in self.basefile.transunits:
      self.sourcewordcounts.append([statsdb.wordcount(text) for text in unit.source.strings])
      self.targetwordcounts.append([statsdb.wordcount(text) for text in unit.target.strings])

  def reclassifyunit(self, item):
    """updates the classification of a unit in self.classify"""
    # TODO: Actually update database
    unit = self.basefile.transunits[item]
    self.sourcewordcounts[item] = [statsdb.wordcount(text) for text in unit.source.strings]
    self.targetwordcounts[item] = [statsdb.wordcount(text) for text in unit.target.strings]
    classes = self.classifyunit(unit)
    if self.basefile.getsuggestions(item):
      classes.append("has-suggestion")
    for classname, matchingitems in self.classify.items():
      if (classname in classes) != (item in matchingitems):
        if classname in classes:
          self.classify[classname].append(item)
        else:
          self.classify[classname].remove(item)
        self.classify[classname].sort()

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
