#!/usr/bin/env python

from translate.convert import convert
import os
import sys
from py import test

class TestConvertCommand:
    """Tests running actual commands on files"""
    convertmodule=convert
    def setup_method(self, method):
        """creates a clean test directory for the given method"""
        self.testdir = "%s_%s" % (self.__class__.__name__, method.__name__)
        self.cleardir()
        os.mkdir(self.testdir)
        self.rundir = os.path.abspath(os.getcwd())

    def teardown_method(self, method):
        """removes the test directory for the given method"""
        os.chdir(self.rundir)
        self.cleardir()

    def cleardir(self):
        """removes the test directory"""
        if os.path.exists(self.testdir):
            for dirpath, subdirs, filenames in os.walk(self.testdir, topdown=False):
                for name in filenames:
                    os.remove(os.path.join(dirpath, name))
                for name in subdirs:
                    os.rmdir(os.path.join(dirpath, name))
        if os.path.exists(self.testdir): os.rmdir(self.testdir)
        assert not os.path.exists(self.testdir)

    def run_command(self, *argv, **kwargs):
        """runs the command via the main function, passing self.defaultoptions and keyword arguments as --long options and argv arguments straight"""
        os.chdir(self.testdir)
        argv = list(argv)
        kwoptions = getattr(self, "defaultoptions", {}).copy()
        kwoptions.update(kwargs)
        for key, value in kwoptions.iteritems():
            if value is True:
                argv.append("--%s" % key)
            else:
                argv.append("--%s=%s" % (key, value))
        try:
            self.convertmodule.main(argv)
        finally:
            os.chdir(self.rundir)

    def get_testfilename(self, filename):
        """gets the path to the test file"""
        return os.path.join(self.testdir, filename)

    def open_testfile(self, filename, mode="r"):
        """opens the given filename in the testdirectory in the given mode"""
        return open(self.get_testfilename(filename), mode)

    def test_help(self):
        """tests getting help (returning the help_string so further tests can be done)"""
        stdout = sys.stdout
        helpfile = self.open_testfile("help.txt", "w")
        sys.stdout = helpfile
        try:
            test.raises(SystemExit, self.run_command, help=True)
        finally:
            sys.stdout = stdout
        helpfile.close()
        help_string = self.open_testfile("help.txt").read()
        assert self.convertmodule.__doc__ in help_string
        usageline = help_string[:help_string.find("\n")]
        assert usageline.startswith("usage: ") and "[--version] [-h|--help]" in usageline
        assert "--progress=PROGRESS" in help_string
        return help_string

