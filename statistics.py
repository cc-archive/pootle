import os
from translate.storage import statsdb
from translate.filters import checks
from translate.misc.multistring import multistring

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
    for checkname, checkmessage in checkresult.iteritems():
      classes.append("check-" + checkname)
    return classes

  def getitemslen(self):
    """gets the number of items in the file"""
    return self.getquickstats()["total"]
