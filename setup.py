#!/usr/bin/env python

from distutils.core import setup, Extension, Distribution
import distutils.sysconfig
import sys
import os.path
from translate import __version__
try:
  import py2exe
except ImportError:
  py2exe = None

join = os.path.join

translateversion = __version__.ver

packagesdir = distutils.sysconfig.get_python_lib()
sitepackages = packagesdir.replace(sys.prefix + os.sep, '')

infofiles = [(join(sitepackages,'translate'),
             [join('translate',filename) for filename in 'ChangeLog', 'COPYING', 'README'])]
initfiles = [(join(sitepackages,'translate'),[join('translate','__init__.py')])]

convertscripts = [apply(join, ('translate', ) + script) for script in
                  ('convert', 'moz2po'), ('convert', 'po2moz'),
                  ('convert', 'oo2po'), ('convert', 'po2oo'),
                  ('convert', 'csv2po'), ('convert', 'po2csv'),
                  ('convert', 'txt2po'), ('convert', 'html2po'),
                  ('filters', 'pofilter'), ('filters', 'pogrep'),
                  ('tools', 'pomerge')]

subpackages = ["convert", "misc", "storage", "filters"]
packages = ["translate"]
for subpackage in subpackages:
  initfiles.append((join(sitepackages, 'translate', subpackage),
                    [join('translate', subpackage, '__init__.py')]))
  for infofile in ('README', 'TODO'):
    infopath = join('translate', subpackage, infofile)
    if os.path.exists(infopath):
      infofiles.append((join(sitepackages, 'translate', subpackage), [infopath]))
  packages.append("translate.%s" % subpackage)

setuppackages = packages
standarddatafiles = initfiles + infofiles
# TODO: make these end with .py ending on Windows...
scripts = convertscripts
ext_modules = []

def import_setup_module(modulename, modulepath):
  import imp
  modfile, pathname, description = imp.find_module(modulename, [modulepath])
  return imp.load_module(modulename, modfile, pathname, description)

# need csv support for versions prior to Python 2.3
buildcsv = 1
includecsv = 0
if buildcsv:
  csvPath = join('translate', 'misc')
  csvSetup = import_setup_module('setup', join(os.getcwd(), 'translate', 'misc'))
  csvModule = csvSetup.csvExtension(csvPath)
  ext_modules.append(csvModule)
elif includecsv:
  # TODO: work out csv.so/pyd
  csvModuleFile = (sitepackages, ['_csv.so'])
  standarddatafiles.append(csvModuleFile)

setupdatafiles = standarddatafiles

def buildmanifest_in(file, scripts):
  """This writes the required files to a MANIFEST.in file"""
  print >>file, "# MANIFEST.in: the below autogenerated by setup.py from translate %s" % translateversion
  print >>file, "# things needed by translate setup.py to rebuild"
  print >>file, "include MANIFEST.in"
  print >>file, "# informational files"
  for filename in ("README", "TODO", "ChangeLog", "COPYING", "*.txt"):
    print >>file, "global-include %s" % filename
  print >>file, "# C programs"
  print >>file, "global-include *.c"
  print >> file, "# scripts which don't get included by default in sdist"
  for scriptname in scripts:
    print >>file, "include %s" % scriptname
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
  manifest_in = open("MANIFEST.in", "w")
  buildmanifest_in(manifest_in, scripts)
  manifest_in.close()
  dosetup(name, version, setuppackages + custompackages, setupdatafiles + customdatafiles)

def dosetup(name, version, packages, datafiles):
  setup(name=name,
        version=version,
        description="translate web framework",
        author="translate.org.za",
        author_email="translate-devel@lists.sourceforge.net",
        url="http://translate.sourceforge.net/",
        packages=packages,
        data_files=datafiles,
        scripts=scripts,
        ext_modules=ext_modules,
        distclass=TranslateDistribution
        )

if __name__ == "__main__":
  standardsetup("translate", translateversion)

