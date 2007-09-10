import os
from translate.storage import statsdb
from translate.filters import checks

def getmodtime(filename, default=None):
  """gets the modificationtime of the given file"""
  if os.path.exists(filename):
    return os.stat(filename)[os.path.stat.ST_MTIME]
  else:
    return default

class pootlestatistics:
  """this represents the statistics known about a file"""
  def __init__(self, basefile, generatestats=True):
    """constructs statistic object for the given file"""
    # TODO: try and remove circular references between basefile and this class
    self.basefile = basefile
    self.stats = {}
    self.totals = {}
    self.statscache = statsdb.StatsCache()
    if generatestats:
      self.getstats()

  def getquickstats(self):
    """returns the quick statistics (totals only)"""
    if not self.totals:
      self.totals = self.statscache.filetotals(self.basefile.filename)
    return self.totals

  def getstats(self):
    """reads the stats if neccessary or returns them from the cache"""
    if not self.stats:
      self.stats = self.statscache.filestats(self.basefile.filename, self.basefile.checker)
    return self.stats

  def updatequickstats(self, save=True):
    """updates the project's quick stats on this file"""
    totals = self.getquickstats()
    self.basefile.project.updatequickstats(self.basefile.pofilename, 
        totals["translatedsourcewords"], totals["translated"], 
        totals["fuzzysourcewords"], totals["fuzzy"],
        totals["totalsourcewords"], totals["total"],
        save)

  def reclassifyunit(self, item):
    """Reclassifies all the information in the database and self.stats about 
    the given unit"""
    unit = self.basefile.getitem(item)
    item = self.stats["total"][item]
    
    classes = self.statscache.recacheunit(self.basefile.filename, self.basefile.checker, unit)
    for classname, matchingitems in self.stats.items():
      if (classname in classes) != (item in matchingitems):
        if classname in classes:
          self.stats[classname].append(item)
        else:
          self.stats[classname].remove(item)
        self.stats[classname].sort()
    # We should be doing better, but for now it is easiet to simply force a 
    # reload from the database
    self.totals = {}

  def getitemslen(self):
    """gets the number of items in the file"""
    return self.getquickstats()["total"]
