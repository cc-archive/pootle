#!/usr/bin/env python

from distutils.core import setup, Extension, Distribution
import distutils.sysconfig
import sys
import os.path
from translate import __version__
from translate import __doc__
try:
  import py2exe
except ImportError:
  py2exe = None

# TODO: check out installing into a different path with --prefix/--home

join = os.path.join

translateversion = __version__.ver

packagesdir = distutils.sysconfig.get_python_lib()
sitepackages = packagesdir.replace(sys.prefix + os.sep, '')

infofiles = [(join(sitepackages,'translate'),
             [join('translate',filename) for filename in 'ChangeLog', 'COPYING', 'LICENSE', 'README'])]
initfiles = [(join(sitepackages,'translate'),[join('translate','__init__.py')])]

subpackages = ["convert", "misc", "storage", "filters", "pootle", "tools"]
# TODO: elementtree doesn't work in sdist, fix this
packages = ["translate"]

convertscripts = [apply(join, ('translate', ) + script) for script in
                  ('convert', 'moz2po'), ('convert', 'po2moz'),
                  ('convert', 'oo2po'),  ('convert', 'po2oo'),
                  ('convert', 'csv2po'), ('convert', 'po2csv'),
                  ('convert', 'txt2po'), ('convert', 'po2txt'),
                  ('convert', 'html2po'),
                  ('convert', 'sxw2po'),
                  ('filters', 'pofilter'),
                  ('tools', 'podebug'), ('tools', 'pogrep'),
                  ('tools', 'pomerge'), ('tools', 'pocount')]

def addsubpackages(subpackages):
  for subpackage in subpackages:
    initfiles.append((join(sitepackages, 'translate', subpackage),
                      [join('translate', subpackage, '__init__.py')]))
    for infofile in ('README', 'TODO'):
      infopath = join('translate', subpackage, infofile)
      if os.path.exists(infopath):
        infofiles.append((join(sitepackages, 'translate', subpackage), [infopath]))
    packages.append("translate.%s" % subpackage)

def import_setup_module(modulename, modulepath):
  import imp
  modfile, pathname, description = imp.find_module(modulename, [modulepath])
  return imp.load_module(modulename, modfile, pathname, description)

# need csv support for versions prior to Python 2.3
def testcsvsupport():
  try:
    import csv
    return 1
  except ImportError:
    return 0

def getcsvmodule():
  csvPath = join('translate', 'misc')
  csvSetup = import_setup_module('setup', join(os.getcwd(), 'translate', 'misc'))
  return csvSetup.csvExtension(csvPath)

def getdatafiles():
  # TODO: add pootle.prefs, pootle/html
  datafiles = initfiles + infofiles
  docfiles = [join('translate', 'doc', docfile) for docfile in os.listdir(join('translate', 'doc'))]
  datafiles.append((join(sitepackages, 'translate', 'doc'), docfiles))
  includecsv = 0
  if includecsv:
    # TODO: work out csv.so/pyd
    csvModuleFile = (sitepackages, ['_csv.so'])
    datafiles.append(csvModuleFile)
  return datafiles

def buildinfolinks():
  linkfile = getattr(os, 'symlink', None)
  linkdir = getattr(os, 'symlink', None)
  import shutil
  if linkfile is None:
    linkfile = shutil.copy2
  if linkdir is None:
    linkdir = shutil.copytree
  basedir = os.path.abspath(os.curdir)
  os.chdir("translate")
  if not os.path.exists("LICENSE"):
    linkfile("COPYING", "LICENSE")
  if not os.path.islink("doc"):
    docdir = os.path.join(os.path.dirname(basedir), "html", "doc")
    if os.path.isdir(docdir):
      if os.path.exists("doc"):
        shutil.rmtree("doc")
      linkdir(docdir, "doc")
  os.chdir(basedir)
  for filename in ["COPYING", "README", "LICENSE"]:
    if not os.path.exists(filename):
      linkfile(os.path.join("translate", filename), filename)

def buildmanifest_in(file, scripts):
  """This writes the required files to a MANIFEST.in file"""
  print >>file, "# MANIFEST.in: the below autogenerated by setup.py from translate %s" % translateversion
  print >>file, "# things needed by translate setup.py to rebuild"
  print >>file, "# informational files"
  for filename in ("README", "TODO", "ChangeLog", "COPYING", "LICENSE", "*.txt"):
    print >>file, "global-include %s" % filename
  print >>file, "# C programs"
  print >>file, "global-include *.c"
  print >> file, "# scripts which don't get included by default in sdist"
  for scriptname in scripts:
    print >>file, "include %s" % scriptname
  # wordlist, portal are in the source tree but unconnected to the python code
  print >>file, "prune wordlist"
  print >>file, "prune portal"
  print >>file, "graft translate/doc"
  print >>file, "# MANIFEST.in: the above autogenerated by setup.py from translate %s" % translateversion

class TranslateDistribution(Distribution):
  """a modified distribution class for translate"""
  def __init__(self, attrs):
    baseattrs = {}
    py2exeoptions = {}
    py2exeoptions["packages"] = ["translate", "encodings"]
    py2exeoptions["compressed"] = True
    version = attrs.get("version", translateversion)
    py2exeoptions["dist_dir"] = "translate-%s" % version
    options = {"py2exe": py2exeoptions}
    baseattrs['options'] = options
    if py2exe:
      self.com_server = []
      self.service = []
      self.windows = []
      self.console = convertscripts
      self.zipfile = "translate.zip"
    baseattrs.update(attrs)
    Distribution.__init__(self, baseattrs)

def standardsetup(name, version, custompackages=[], customdatafiles=[]):
  buildinfolinks()
  # TODO: make these end with .py ending on Windows...
  try:
    manifest_in = open("MANIFEST.in", "w")
    buildmanifest_in(manifest_in, convertscripts)
    manifest_in.close()
  except IOError, e:
    print >> sys.stderr, "warning: could not recreate MANIFEST.in, continuing anyway. Error was %s" % e
  addsubpackages(subpackages)
  datafiles = getdatafiles()
  ext_modules = []
  if not testcsvsupport():
    csvModule = getcsvmodule()
    ext_modules.append(csvModule)
  dosetup(name, version, packages + custompackages, datafiles + customdatafiles, convertscripts, ext_modules)

classifiers = [
  "Development Status :: 5 - Production/Stable",
  "Environment :: Console",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: GNU General Public License (GPL)",
  "Programming Language :: Python",
  "Topic :: Software Development :: Localization",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Operating System :: OS Independent",
  "Operating System :: Microsoft :: Windows",
  "Operating System :: Unix"
  ]

def dosetup(name, version, packages, datafiles, scripts, ext_modules=[]):
  long_description = __doc__
  description = __doc__.split("\n", 1)[0]
  setup(name=name,
        version=version,
        license="GNU General Public License (GPL)",
        description=description,
        long_description=long_description,
        author="David Fraser, translate.org.za",
        author_email="translate-devel@lists.sourceforge.net",
        url="http://translate.sourceforge.net/",
        download_url="http://sourceforge.net/project/showfiles.php?group_id=91920&package_id=97082",
        platforms=["any"],
        classifiers=classifiers,
        packages=packages,
        data_files=datafiles,
        scripts=scripts,
        ext_modules=ext_modules,
        distclass=TranslateDistribution
        )

if __name__ == "__main__":
  standardsetup("translate toolkit", translateversion)

