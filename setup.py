#!/usr/bin/env python

from distutils.core import setup, Extension
import distutils.sysconfig
import sys
import os.path
from translate import __version__

join = os.path.join

translateversion = __version__.ver

packagesdir = distutils.sysconfig.get_python_lib()
sitepackages = packagesdir.replace(sys.prefix + os.sep, '')

infofiles = [(join(sitepackages,'translate'),
             [join('translate',filename) for filename in 'ChangeLog', 'COPYING', 'README', 'intro.txt'])]
initfiles = [(join(sitepackages,'translate'),[join('translate','__init__.py')])]

convertscripts = [apply(join, ('translate', ) + script) for script in
                  ('convert', 'moz2po'), ('convert', 'po2moz'),
                  ('convert', 'oo2po'), ('convert', 'po2oo'),
                  ('convert', 'csv2po'), ('convert', 'po2csv'),
                  ('filters', 'pofilter'), ('filters', 'pogrep'),
                  ('tools', 'pomerge')]

subpackages = ["convert", "misc", "portal", "storage", "filters"]
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


def standardsetup(name, version, custompackages=[], customdatafiles=[]):
  dosetup(name, version, setuppackages + custompackages, setupdatafiles + customdatafiles)

def dosetup(name, version, packages, datafiles):
  setup(name=name,
        version=version,
        description="translate web framework",
        author="translate.org.za",
        author_email="translate-devel@lists.sourceforge.net",
        url="http://translate.sourceforge.net/",
        packages = packages,
        data_files = datafiles,
        scripts = scripts,
        ext_modules = ext_modules
        )

if __name__ == "__main__":
  standardsetup("translate", translateversion)

