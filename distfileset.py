#!/usr/bin/env python

import os.path

join = os.path.join

class fileset(list):
  """this is a installation list of a set of files from a directory"""
  def __init__(self, src, dest, destsubdir):
    """creates the fileset by walking through src directory"""
    self.src = src
    self.dest = dest
    self.destsubdir = destsubdir
    # this calls self.adddirfiles(None, dirname, names) for each subdirectory dirname of self.src
    os.path.walk(self.src, self.adddirfiles, None)

  def adddirfiles(self, arg, dirname, names):
    """adds the files names from dirname to self (which is a list)"""
    # arg is ignored
    if 'CVS' in names:
      names.remove('CVS')
    filenames = []
    for name in names:
      filename = join(dirname,name)
      if not os.path.isdir(filename):
        filenames.append(filename)
    if len(filenames) > 0:
      destsubdirname = dirname.replace(self.src,self.destsubdir,1)
      destpath = join(self.dest,destsubdirname)
      self.append((destpath,filenames))

