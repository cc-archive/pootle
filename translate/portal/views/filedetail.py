#!/usr/bin/env python

"""
Autogenerated by CHEETAH: The Python-Powered Template Engine
 CHEETAH VERSION: 0.9.15
 Generation time: Tue Jul 20 00:13:27 2004
   Source file: filedetail.tmpl
   Source file last modified: Tue Jul 20 00:13:25 2004
"""

__CHEETAH_genTime__ = 'Tue Jul 20 00:13:27 2004'
__CHEETAH_src__ = 'filedetail.tmpl'
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

class filedetail(Template):
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
        
        write('''<html>
    <head>
        <title>File details</title>
    </head>
    <body>
        <small><a href="index?view=projectlist">Home</a></small>>
        <small><a href="index?view=projectdetail&project=''')
        write(filter(VFS(SL + [globals(), __builtin__],"file.project.id",True), rawExpr='$file.project.id')) # from line 7, col 58.
        write('">')
        write(filter(VFS(SL + [globals(), __builtin__],"format",False)(VFS(SL + [globals(), __builtin__],"file.project.name",True)), rawExpr='$format($file.project.name)')) # from line 7, col 76.
        write(' (')
        write(filter(VFS(SL + [globals(), __builtin__],"format",False)(VFS(SL + [globals(), __builtin__],"file.project.version",True)), rawExpr='$format($file.project.version)')) # from line 7, col 105.
        write(')</a></small> >\n        <small><u>')
        write(filter(VFS(SL + [globals(), __builtin__],"format",False)(VFS(SL + [globals(), __builtin__],"file.name",True)), rawExpr='$format($file.name)')) # from line 8, col 19.
        write('''</u></small>        
        <h1>File details</h1>
        <hr/>
        <h2>Properties:</h2>
        <table border="0">
            <tr><td align="right">Name : </td><td>''')
        write(filter(VFS(SL + [globals(), __builtin__],"format",False)(VFS(SL + [globals(), __builtin__],"file.name",True)), rawExpr='$format($file.name)')) # from line 13, col 51.
        write('''</td></tr>
        </table>
        <hr/>
        <h2>Strings:</h2>
''')
        for original in VFN(VFS(SL + [globals(), __builtin__],"file",True),"getOriginals",False)():
            write('')
            displayname = VFN(original,"getStripped",False)()
            write('')
            if len(displayname) > 40:
                write('                <p><a href="index?view=stringdetail&original=')
                write(filter(VFN(original,"id",True), rawExpr='$original.id')) # from line 20, col 62.
                write('">')
                write(filter(VFS(SL + [globals(), __builtin__],"format",False)(displayname[:40]), rawExpr='$format($displayname[:40])')) # from line 20, col 76.
                write(' ...</a></p>\n')
            else:
                write('                <p><a href="index?view=stringdetail&original=')
                write(filter(VFN(original,"id",True), rawExpr='$original.id')) # from line 22, col 62.
                write('">')
                write(filter(VFS(SL + [globals(), __builtin__],"format",False)(displayname), rawExpr='$format($displayname)')) # from line 22, col 76.
                write('</a></p>\n')
            write('            <br/>         \n')
        write('    </body>\n</html>\n')
        
        ########################################
        ## END - generated method body
        
        if dummyTrans:
            return trans.response().getvalue()
        else:
            return ""
        
    ##################################################
    ## GENERATED ATTRIBUTES


    __str__ = respond

    _mainCheetahMethod_for_filedetail= 'respond'


# CHEETAH was developed by Tavis Rudd, Mike Orr, Ian Bicking and Chuck Esterbrook;
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org

##################################################
## if run from command line:
if __name__ == '__main__':
    filedetail().runAsMainProgram()

