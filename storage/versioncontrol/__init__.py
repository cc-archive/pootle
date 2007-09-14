#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2004-2007 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""This module manages interaction with version control systems.

To implement support for a new version control system, inherit the class
GenericRevisionControlSystem. 

TODO:
    * move to the translate toolkit and split into different files
"""

import re
import os
import translate.storage.versioncontrol

DEFAULT_RCS = ["svn", "cvs", "darcs", "git", "bzr"]
"""the names of all supported revision control systems

modules of the same name containing a class with the same name are expected
to be defined below 'translate.storage.versioncontrol'
"""

__CACHED_RCS_CLASSES = {}
"""The dynamically loaded revision control system implementations (python
modules) are cached here for faster access.
"""

def __get_rcs_class(name):
    if not name in __CACHED_RCS_CLASSES:
        try:
            module = __import__("translate.storage.versioncontrol.%s" % name,
                    globals(), {}, name)
            rcs_class = getattr(module, name)
        except [ImportError, AttributeError]:
            return None
        __CACHED_RCS_CLASSES[name] = rcs_class
    return __CACHED_RCS_CLASSES[name]


# use either 'popen2' or 'subprocess' for command execution
try:
    # available for python >= 2.4
    import subprocess

    # The subprocess module allows to use cross-platform command execution
    # without using the shell (increases security).

    def run_command(command):
        """Runs a command (array of program name and arguments) and returns the
        exitcode, the output and the error as a tuple.
        """
        # ok - we use "subprocess"
        proc = subprocess.Popen(args = command,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                stdin = subprocess.PIPE)
        (output, error) = proc.communicate()
        ret = proc.returncode
        return ret, output, error

except ImportError:
    # fallback for python < 2.4
    import popen2

    def run_command(command):
        """Runs a command (array of program name and arguments) and returns the
        exitcode, the output and the error as a tuple.
        """
        escaped_command = " ".join([__shellescape(arg) for arg in command])
        proc = popen2.Popen3(escaped_command, True)
        (c_stdin, c_stdout, c_stderr) = (proc.tochild, proc.fromchild, proc.childerr)
        output = c_stdout.read()
        error = c_stderr.read()
        ret = proc.wait()
        c_stdout.close()
        c_stderr.close()
        c_stdin.close()
        return ret, output, error

def __shellescape(path):
    """Shell-escape any non-alphanumeric characters."""
    return re.sub(r'(\W)', r'\\\1', path)


class GenericRevisionControlSystem:
    """The super class for all version control classes.

    Always inherit from this class to implement another RC interface.

    At least the two attributes "RCS_METADIR" and "SCAN_PARENTS" must be 
    overriden by all implementations that derive from this class.

    By default, all implementations can rely on the following attributes:
        root_dir: the parent of the metadata directory of the working copy
        location_abs: the absolute path of the RCS object
        location_rel: the path of the RCS object relative to 'root_dir'
    """

    RCS_METADIR = None
    """The name of the metadata directory of the RCS

    e.g.: for Subversion -> ".svn"
    """

    SCAN_PARENTS = None
    """whether to check the parent directories for the metadata directory of
    the RCS working copy
    
    some revision control systems store their metadata directory only
    in the base of the working copy (e.g. bzr, GIT and Darcs)
    use "True" for these RCS

    other RCS store a metadata directory in every single directory of
    the working copy (e.g. Subversion and CVS)
    use "False" for these RCS
    """

    def __init__(self, location):
        """find the relevant information about this RCS object
        
        The IOError exception indicates that the specified object (file or
        directory) is not controlled by the given version control system.
        """
        # check if the implementation looks ok - otherwise raise IOError
        self._self_check()
        # search for the repository information
        result = self._find_rcs_directory(location)
        if result is None:
            raise IOError("Could not find revision control information: %s" \
                    % location)
        else:
            self.root_dir, self.location_abs, self.location_rel = result

    def _find_rcs_directory(self, rcs_obj):
        """Try to find the metadata directory of the RCS

        returns a tuple:
            the absolute path of the directory, that contains the metadata directory
            the absolute path of the RCS object
            the relative path of the RCS object based on the directory above
        """
        rcs_obj_dir = os.path.dirname(os.path.abspath(rcs_obj))
        if os.path.isdir(os.path.join(rcs_obj_dir, self.RCS_METADIR)):
            # is there a metadir next to the rcs_obj?
            # (for Subversion, CVS, ...)
            location_abs = os.path.abspath(rcs_obj)
            location_rel = os.path.basename(location_abs)
            return (rcs_obj_dir, location_abs, location_rel)
        elif self.SCAN_PARENTS:
            # scan for the metadir in parent directories
            # (for bzr, GIT, Darcs, ...)
            return self._find_rcs_in_parent_directories(rcs_obj)
        else:
            # no RCS metadata found
            return None
    
    def _find_rcs_in_parent_directories(self, rcs_obj):
        """Try to find the metadata directory in all parent directories"""
        # first: resolve possible symlinks
        current_dir = os.path.dirname(os.path.realpath(rcs_obj))
        # prevent infite loops
        max_depth = 64
        # stop as soon as we find the metadata directory
        while not os.path.isdir(os.path.join(current_dir, self.RCS_METADIR)):
            if os.path.dirname(current_dir) == current_dir:
                # we reached the root directory - stop
                return None
            if max_depth <= 0:
                # some kind of dead loop or a _very_ deep directory structure
                return None
            # go to the next higher level
            current_dir = os.path.dirname(current_dir)
        # the loop was finished successfully
        # i.e.: we found the metadata directory
        rcs_dir = current_dir
        location_abs = os.path.realpath(rcs_obj)
        # strip the base directory from the path of the rcs_obj
        basedir = rcs_dir + os.path.sep
        if location_abs.startswith(basedir):
            # remove the base directory (including the trailing slash)
            location_rel = location_abs.replace(basedir, "", 1)
            # successfully finished
            return (rcs_dir, location_abs, location_rel)
        else:
            # this should never happen
            return None
        
    def _self_check(self):
        """Check if all necessary attributes are defined

        Useful to make sure, that a new implementation does not forget
        something like "RCS_METADIR"
        """
        if self.RCS_METADIR is None:
            raise IOError("Incomplete RCS interface implementation: " \
                    + "self.RCS_METADIR is None")
        if self.SCAN_PARENTS is None:
            raise IOError("Incomplete RCS interface implementation: " \
                    + "self.SCAN_PARENTS is None")
        # we do not check for implemented functions - they raise
        # NotImplementedError exceptions anyway
        return True
                    
    def getcleanfile(self, revision=None):
        """Dummy to be overridden by real implementations"""
        raise NotImplementedError("Incomplete RCS interface implementation:" \
                + " 'getcleanfile' is missing")


    def commit(self, revision=None):
        """Dummy to be overridden by real implementations"""
        raise NotImplementedError("Incomplete RCS interface implementation:" \
                + " 'commit' is missing")


    def update(self, revision=None):
        """Dummy to be overridden by real implementations"""
        raise NotImplementedError("Incomplete RCS interface implementation:" \
                + " 'update' is missing")


def get_versioned_object(
        location,
        versioning_systems=DEFAULT_RCS,
        follow_symlinks=True):
    """return a versioned object for the given file"""
    # go through all RCS and return a versioned object if possible
    for vers_sys in versioning_systems:
        try:
            vers_sys_class = __get_rcs_class(vers_sys)
            if not vers_sys_class is None:
                return vers_sys_class(location)
        except IOError:
            continue
    # if 'location' is a symlink, then we should try the original file
    if follow_symlinks and os.path.islink(location):
        return get_versioned_object(os.path.realpath(location),
                versioning_systems = versioning_systems,
                follow_symlinks = False)
    # if everything fails:
    raise IOError("Could not find version control information: %s" % location)

# stay compatible to the previous version
def updatefile(filename):
    return get_versioned_object(filename).update()

def getcleanfile(filename, revision=None):
    return get_versioned_object(filename).getcleanfile(revision)

def commitfile(filename, message=None):
    return get_versioned_object(filename).commit(message)

def hasversioning(item):
    try:
        # try all available version control systems
        get_versioned_object(item)
        return True
    except IOError:
        return False


    
if __name__ == "__main__":
    import sys
    filenames = sys.argv[1:]
    for filename in filenames:
        contents = getcleanfile(filename)
        sys.stdout.write("\n\n******** %s ********\n\n" % filename)
        sys.stdout.write(contents)

