#!/usr/bin/env python

"""
Autogenerated by CHEETAH: The Python-Powered Template Engine
 CHEETAH VERSION: 0.9.15
 Generation time: Fri Jun 18 10:15:35 2004
   Source file: views/stringdetail.tmpl
   Source file last modified: Fri Jun 18 10:15:33 2004
"""

__CHEETAH_genTime__ = 'Fri Jun 18 10:15:35 2004'
__CHEETAH_src__ = 'views/stringdetail.tmpl'
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
from translate.portal.database.model import Translation

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

class stringdetail(Template):
    """
    
    Autogenerated by CHEETAH: The Python-Powered Template Engine
    """

    ##################################################
    ## GENERATED METHODS


    def __init__(self, *args, **KWs):
        """
        
        """

        Template.__init__(self, *args, **KWs)

    def showTranslation(self,
            transl,
            ed,
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
        Generated from #def showTranslation($transl,$ed) at line 2, col 1.
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
        
        write('')
        lang = VFN(transl,"language",True)
        write('    <hr/>\n    <h2>')
        write(filter(VFN(lang,"name",True), rawExpr='$lang.name')) # from line 5, col 9.
        write(' (')
        write(filter(VFN(lang,"iso639_2",True), rawExpr='$lang.iso639_2')) # from line 5, col 21.
        write(' ')
        write(filter(VFN(lang,"iso639_3",True), rawExpr='$lang.iso639_3')) # from line 5, col 36.
        write(' ')
        write(filter(VFN(lang,"country_iso3166_2",True), rawExpr='$lang.country_iso3166_2')) # from line 5, col 51.
        write(''')</h2>   
    <table border="0">
        <tr>
            <td align="right">Translation version : </td><td>''')
        write(filter(VFN(transl,"version",True), rawExpr='$transl.version')) # from line 8, col 62.
        write('</td>\n        </tr>\n')
        if ed:
            write('            <form name="editForm" action="index">\n            <tr>\n                <td align="right">Raw string : </td><td><textarea name="raw">')
            write(filter(VFN(transl,"raw",True), rawExpr='$transl.raw')) # from line 13, col 78.
            write('''</textarea></td> 
            </tr>
            <tr>               
                <td align="right">
                    <input type="hidden" name="action" value="translationsave">
                    <input type="hidden" name="translationid" value="''')
            write(filter(VFN(transl,"id",True), rawExpr='$transl.id')) # from line 18, col 70.
            write('">\n                    <input type="hidden" name="originalid" value="')
            write(filter(VFN(transl,"original.id",True), rawExpr='$transl.original.id')) # from line 19, col 67.
            write('''">                    
                    <input type="hidden" name="view" value="stringdetail"/>
                </td><td><input type="submit"  value="save"/></td>                     
            </tr>
            <form>
''')
        else:
            write('            <tr>\n                <td align="right">Raw string : </td><td>')
            write(filter(VFN(transl,"raw",True), rawExpr='$transl.raw')) # from line 26, col 57.
            write('</td>\n            </tgr>\n')
        write('        </tr>\n        <tr>\n            <td align="right">Accelerator : </td><td>')
        write(filter(VFN(transl,"getAccelerator",False)(), rawExpr='$transl.getAccelerator()')) # from line 31, col 54.
        write('''</td>
        </tr>
        <tr>
            <td align="right">Stripped string : </td><td>''')
        write(filter(VFN(transl,"getStripped",False)(), rawExpr='$transl.getStripped()')) # from line 34, col 58.
        write('''</td>
        </tr>
        <tr>
            <td align="right">Number of words : </td><td>''')
        write(filter(VFN(transl,"getWordcount",False)(), rawExpr='$transl.getWordcount()')) # from line 37, col 58.
        write('''</td>
        </tr>
        <tr>
            <td align="right">Number of characters : </td><td>''')
        write(filter(VFN(transl,"getCharcount",False)(), rawExpr='$transl.getCharcount()')) # from line 40, col 63.
        write('''</td>
        </tr>
    </table>
''')
        
        ########################################
        ## END - generated method body
        
        if dummyTrans:
            return trans.response().getvalue()
        else:
            return ""
        

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
        
        write('''
<html>
    <head>
''')
        displayname = VFN(VFS(SL + [globals(), __builtin__],"original",True),"getStripped",False)()
        write('        <small><a href="index?view=filelist">Home</a></small> >\n        <small><a href="index?view=filedetail&file=')
        write(filter(VFS(SL + [globals(), __builtin__],"original.file.id",True), rawExpr='$original.file.id')) # from line 49, col 52.
        write('">')
        write(filter(VFS(SL + [globals(), __builtin__],"original.file.name",True), rawExpr='$original.file.name')) # from line 49, col 71.
        write('</a></small>>\n        <small><u>')
        write(filter(displayname[:20], rawExpr='$displayname[:20]')) # from line 50, col 19.
        write(''' ...</u></small>
        <title>String details</title>
    </head>
    <body>
        <h1>String details</h1>
''')
        if not VFS(SL + [globals(), __builtin__],"editing",True):
            write('            <a href="index?view=stringdetail&edit=yes&original=')
            write(filter(VFS(SL + [globals(), __builtin__],"original.id",True), rawExpr='$original.id')) # from line 56, col 64.
            write('&language=')
            write(filter(VFS(SL + [globals(), __builtin__],"languageid",True), rawExpr='$languageid')) # from line 56, col 86.
            write('">edit</a>        \n')
        write('''        <hr/>
        <h2>Original</h2>
        <table border="0">
            <tr>
                <td align="right">Translator comment : </td><td>''')
        write(filter(VFS(SL + [globals(), __builtin__],"original.translator_comment",True), rawExpr='$original.translator_comment')) # from line 62, col 65.
        write('''</td>
            </tr>
            <tr>
                <td align="right">Comment : </td><td>''')
        write(filter(VFS(SL + [globals(), __builtin__],"original.comment",True), rawExpr='$original.comment')) # from line 65, col 54.
        write('''</td>
            </tr>
            <tr>
                <td align="right">Raw string : </td><td>''')
        write(filter(VFS(SL + [globals(), __builtin__],"original.raw",True), rawExpr='$original.raw')) # from line 68, col 57.
        write('''</td>
            </tr>
            <tr>
                <td align="right">Accelerator : </td><td>''')
        write(filter(VFN(VFS(SL + [globals(), __builtin__],"original",True),"getAccelerator",False)(), rawExpr='$original.getAccelerator()')) # from line 71, col 58.
        write('''</td>
            </tr>
            <tr>
                <td align="right">Stripped string : </td><td>''')
        write(filter(VFN(VFS(SL + [globals(), __builtin__],"original",True),"getStripped",False)(), rawExpr='$original.getStripped()')) # from line 74, col 62.
        write('''</td>
            </tr>
            <tr>
                <td align="right">Number of words : </td><td>''')
        write(filter(VFN(VFS(SL + [globals(), __builtin__],"original",True),"getWordcount",False)(), rawExpr='$original.getWordcount()')) # from line 77, col 62.
        write('''</td>
            </tr>
            <tr>
                <td align="right">Number of characters : </td><td>''')
        write(filter(VFN(VFS(SL + [globals(), __builtin__],"original",True),"getCharcount",False)(), rawExpr='$original.getCharcount()')) # from line 80, col 67.
        write('''</td>
            </tr>
        </table>
        <hr/>
        <form name="langselectForm" action="index">
            <input type="hidden" name="view" value="stringdetail"/>
            <input type="hidden" name="edit" value="''')
        write(filter(VFS(SL + [globals(), __builtin__],"editing",True), rawExpr='$editing')) # from line 86, col 53.
        write('"/>\n            <input type="hidden" name="original" value="')
        write(filter(VFS(SL + [globals(), __builtin__],"original.id",True), rawExpr='$original.id')) # from line 87, col 57.
        write('"/>\n            Select your preferred language: <select name="language" onChange="document.langselectForm.submit()")">\n')
        if not VFS(SL + [globals(), __builtin__],"editing",True):
            write('                <option value="-1">All</option>\n')
        write('')
        for l in VFS(SL + [globals(), __builtin__],"languages",True):
            write('                <option value="')
            write(filter(VFN(l,"id",True), rawExpr='$l.id')) # from line 93, col 32.
            write('" \n')
            if VFN(l,"id",True) == VFS(SL + [globals(), __builtin__],"languageid",True):
                write('                    selected \n')
            write('                >')
            write(filter(VFN(l,"name",True), rawExpr='$l.name')) # from line 97, col 18.
            write(' (')
            write(filter(VFN(l,"iso639_2",True), rawExpr='$l.iso639_2')) # from line 97, col 27.
            write(' ')
            write(filter(VFN(l,"iso639_3",True), rawExpr='$l.iso639_3')) # from line 97, col 39.
            write(' ')
            write(filter(VFN(l,"country_iso3166_2",True), rawExpr='$l.country_iso3166_2')) # from line 97, col 51.
            write(')</option>\n')
        write('           </select></form>\n')
        if not VFS(SL + [globals(), __builtin__],"translations",True):
            write('            <hr/>\n')
            if VFS(SL + [globals(), __builtin__],"editing",True):
                write('')
                translation = Translation()
                write('                ')
                write(filter(VFN(translation,"setLanguage",False)(VFS(SL + [globals(), __builtin__],"language",True)), rawExpr='$translation.setLanguage($language)')) # from line 104, col 17.
                write('\n                ')
                write(filter(VFN(translation,"setOriginal",False)(VFS(SL + [globals(), __builtin__],"original",True)), rawExpr='$translation.setOriginal($original)')) # from line 105, col 17.
                write('\n                ')
                write(filter(VFS(SL + [globals(), __builtin__],"showTranslation",False)(translation,VFS(SL + [globals(), __builtin__],"editing",True)), rawExpr='$showTranslation($translation,$editing)')) # from line 106, col 17.
                write('\n')
            else:
                write('                <i>No translations for that selection</i>\n')
            write('')
        write('')
        for translation in VFS(SL + [globals(), __builtin__],"translations",True):
            write('            ')
            write(filter(VFS(SL + [globals(), __builtin__],"showTranslation",False)(translation,VFS(SL + [globals(), __builtin__],"editing",True)), rawExpr='$showTranslation($translation,$editing)')) # from line 112, col 13.
            write('\n')
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

    _mainCheetahMethod_for_stringdetail= 'respond'


# CHEETAH was developed by Tavis Rudd, Mike Orr, Ian Bicking and Chuck Esterbrook;
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org

##################################################
## if run from command line:
if __name__ == '__main__':
    stringdetail().runAsMainProgram()

