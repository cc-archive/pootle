#!/usr/bin/env python

"""
Autogenerated by CHEETAH: The Python-Powered Template Engine
 CHEETAH VERSION: 0.9.15
 Generation time: Tue Jul 20 00:13:28 2004
   Source file: testing.tmpl
   Source file last modified: Thu Jun 17 16:53:21 2004
"""

__CHEETAH_genTime__ = 'Tue Jul 20 00:13:28 2004'
__CHEETAH_src__ = 'testing.tmpl'
__CHEETAH_version__ = '0.9.15'

##################################################
## DEPENDENCIES

import sys
import os
import os.path
from os.path import getmtime, exists
import time
import types
import __builtin__
from Cheetah.Template import Template
from Cheetah.DummyTransaction import DummyTransaction
from Cheetah.NameMapper import NotFound, valueForName, valueFromSearchList
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers

##################################################
## MODULE CONSTANTS

try:
    True, False
except NameError:
    True, False = (1==1), (1==0)
VFS=valueFromSearchList
VFN=valueForName
currentTime=time.time

##################################################
## CLASSES

class testing(Template):
    """
    
    Autogenerated by CHEETAH: The Python-Powered Template Engine
    """

    ##################################################
    ## GENERATED METHODS


    def __init__(self, *args, **KWs):
        """
        
        """

        Template.__init__(self, *args, **KWs)

    def respond(self,
            trans=None,
            dummyTrans=False,
            VFS=valueFromSearchList,
            VFN=valueForName,
            getmtime=getmtime,
            currentTime=time.time,
            globals=globals,
            locals=locals,
            __builtin__=__builtin__):


        """
        This is the main method generated by Cheetah
        """

        if not trans:
            trans = DummyTransaction()
            dummyTrans = True
        write = trans.response().write
        SL = self._searchList
        filter = self._currentFilter
        globalSetVars = self._globalSetVars
        
        ########################################
        ## START - generated method body
        
        write('''<h1>Test view:</h1>
<ul>
<li>This is a test
<li>If you're seeing this, then some things are working
<li> Name: <i>''')
        write(filter(VFS(SL + [globals(), __builtin__],"name",True), rawExpr='$name')) # from line 5, col 15.
        write('</i>\n<li> Time: <i>')
        write(filter(VFS(SL + [globals(), __builtin__],"time",True), rawExpr='$time')) # from line 6, col 15.
        write('</i>\n\n')
        
        ########################################
        ## END - generated method body
        
        if dummyTrans:
            return trans.response().getvalue()
        else:
            return ""
        
    ##################################################
    ## GENERATED ATTRIBUTES


    __str__ = respond

    _mainCheetahMethod_for_testing= 'respond'


# CHEETAH was developed by Tavis Rudd, Mike Orr, Ian Bicking and Chuck Esterbrook;
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org

##################################################
## if run from command line:
if __name__ == '__main__':
    testing().runAsMainProgram()

