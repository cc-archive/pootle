#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2004-2008 Zuza Software Foundation
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

"""This is a set of validation checks that can be performed on translation 
units.

Derivatives of UnitChecker (like StandardUnitChecker) check translation units,
and derivatives of TranslationChecker (like StandardChecker) check 
(source, target) translation pairs.

When adding a new test here, please document and explain the behaviour on the 
U{wiki <http://translate.sourceforge.net/wiki/toolkit/pofilter_tests>}.
"""

from translate.filters import helpers
from translate.filters import decoration
from translate.filters import prefilters
from translate.filters import spelling
from translate.lang import factory
from translate.lang import data
# The import of xliff could fail if the user doesn't have lxml installed. For
# now we try to continue gracefully to help users who aren't interested in 
# support for XLIFF or other XML formats.
try:
    from translate.storage import xliff
except ImportError, e:
    xliff = None
import re

# These are some regular expressions that are compiled for use in some tests

# printf syntax based on http://en.wikipedia.org/wiki/Printf which doens't cover everything we leave \w instead of specifying the exact letters as
# this should capture printf types defined in other platforms.
printf_pat = re.compile('%((?:(?P<ord>\d+)\$)*(?P<fullvar>[+#-]*(?:\d+)*(?:\.\d+)*(hh\|h\|l\|ll)*(?P<type>[\w%])))')

# The name of the XML tag
tagname_re = re.compile("<[\s]*([\w\/]*)")

# We allow escaped quotes, probably for old escaping style of OOo helpcontent
#TODO: remove escaped strings once usage is audited
property_re = re.compile(" (\w*)=((\\\\?\".*?\\\\?\")|(\\\\?'.*?\\\\?'))")

# The whole tag
tag_re = re.compile("<[^>]+>")

def tagname(string):
    """Returns the name of the XML/HTML tag in string"""
    return tagname_re.match(string).groups(1)[0]

def intuplelist(pair, list):
    """Tests to see if pair == (a,b,c) is in list, but handles None entries in 
    list as wildcards (only allowed in positions "a" and "c"). We take a shortcut
    by only considering "c" if "b" has already matched."""
    a, b, c = pair
    if (b, c) == (None, None):
        #This is a tagname
        return pair
    for pattern in list:
        x, y, z = pattern
        if (x, y) in [(a, b), (None, b)]:
            if z in [None, c]:
                return pattern
    return pair

def tagproperties(strings, ignore):
    """Returns all the properties in the XML/HTML tag string as 
    (tagname, propertyname, propertyvalue), but ignore those combinations 
    specified in ignore."""
    properties = []
    for string in strings:
        tag = tagname(string)
        properties += [(tag, None, None)]
        #Now we isolate the attribute pairs. 
        pairs = property_re.findall(string)
        for property, value, a, b in pairs:
            #Strip the quotes:
            value = value[1:-1]

            canignore = False
            if (tag, property, value) in ignore or \
                    intuplelist((tag,property,value), ignore) != (tag,property,value):
                canignore = True
                break
            if not canignore:
                properties += [(tag, property, value)]
    return properties
        

class FilterFailure(Exception):
    """This exception signals that a Filter didn't pass, and gives an explanation 
    or a comment"""
    def __init__(self, messages):
        if not isinstance(messages, list):
            messages = [messages]
        strmessages = []
        for message in messages:
            if isinstance(message, unicode):
                message = message.encode("utf-8")
            strmessages.append(message)
        messages = ", ".join(strmessages)
        Exception.__init__(self, messages)

class SeriousFilterFailure(FilterFailure):
    """This exception signals that a Filter didn't pass, and the bad translation 
    might break an application (so the string will be marked fuzzy)"""
    pass

#(tag, attribute, value) specifies a certain attribute which can be changed/
#ignored if it exists inside tag. In the case where there is a third element
#in the tuple, it indicates a property value that can be ignored if present 
#(like defaults, for example)
#If a certain item is None, it indicates that it is relevant for all values of
#the property/tag that is specified as None. A non-None value of "value"
#indicates that the value of the attribute must be taken into account.
common_ignoretags = [(None, "xml-lang", None)]
common_canchangetags = [("img", "alt", None)]

class CheckerConfig(object):
    """object representing the configuration of a checker"""
    def __init__(self, targetlanguage=None, accelmarkers=None, varmatches=None, 
                    notranslatewords=None, musttranslatewords=None, validchars=None, 
                    punctuation=None, endpunctuation=None, ignoretags=None, 
                    canchangetags=None, criticaltests=None, credit_sources=None):
        # Init lists
        self.accelmarkers = self._init_list(accelmarkers)
        self.varmatches = self._init_list(varmatches)
        self.criticaltests = self._init_list(criticaltests)
        self.credit_sources = self._init_list(credit_sources)
        # Lang data
        self.targetlanguage = targetlanguage
        self.updatetargetlanguage(targetlanguage)
        self.sourcelang = factory.getlanguage('en')
        # Inits with default values
        self.punctuation = self._init_default(data.forceunicode(punctuation),  self.lang.punctuation)
        self.endpunctuation = self._init_default(data.forceunicode(endpunctuation), self.lang.sentenceend)
        self.ignoretags = self._init_default(ignoretags, common_ignoretags)
        self.canchangetags = self._init_default(canchangetags, common_canchangetags)
        # Other data
        # TODO: allow user configuration of untranslatable words
        self.notranslatewords = dict.fromkeys([data.forceunicode(key) for key in self._init_list(notranslatewords)])
        self.musttranslatewords = dict.fromkeys([data.forceunicode(key) for key in self._init_list(musttranslatewords)])
        validchars = data.forceunicode(validchars)
        self.validcharsmap = {}
        self.updatevalidchars(validchars)

    def _init_list(self, list):
        """initialise configuration paramaters that are lists

        @type list: List
        @param list: None (we'll initialise a blank list) or a list paramater
        @rtype: List
        """
        if list is None:
            list = []
        return list

    def _init_default(self, param, default):
        """initialise parameters that can have default options

        @param param: the user supplied paramater value
        @param default: default values when param is not specified
        @return: the paramater as specified by the user of the default settings
        """
        if param is None:
            return default
        return param

    def update(self, otherconfig):
        """combines the info in otherconfig into this config object"""
        self.targetlanguage = otherconfig.targetlanguage or self.targetlanguage
        self.updatetargetlanguage(self.targetlanguage)
        self.accelmarkers.extend([c for c in otherconfig.accelmarkers if not c in self.accelmarkers])
        self.varmatches.extend(otherconfig.varmatches)
        self.notranslatewords.update(otherconfig.notranslatewords)
        self.musttranslatewords.update(otherconfig.musttranslatewords)
        self.validcharsmap.update(otherconfig.validcharsmap)
        self.punctuation += otherconfig.punctuation
        self.endpunctuation += otherconfig.endpunctuation
        #TODO: consider also updating in the following cases:
        self.ignoretags = otherconfig.ignoretags
        self.canchangetags = otherconfig.canchangetags
        self.criticaltests.extend(otherconfig.criticaltests)
        self.credit_sources = otherconfig.credit_sources

    def updatevalidchars(self, validchars):
        """updates the map that eliminates valid characters"""
        if validchars is None:
            return True
        validcharsmap = dict([(ord(validchar), None) for validchar in data.forceunicode(validchars)])
        self.validcharsmap.update(validcharsmap)

    def updatetargetlanguage(self, langcode):
        """Updates the target language in the config to the given target language"""
        self.lang = factory.getlanguage(langcode)

class UnitChecker(object):
    """Parent Checker class which does the checking based on functions available 
    in derived classes."""
    preconditions = {}

    def __init__(self, checkerconfig=None, excludefilters=None, limitfilters=None, errorhandler=None):
        self.errorhandler = errorhandler
        if checkerconfig is None:
            self.setconfig(CheckerConfig())
        else:
            self.setconfig(checkerconfig)
        # exclude functions defined in UnitChecker from being treated as tests...
        self.helperfunctions = {}
        for functionname in dir(UnitChecker):
            function = getattr(self, functionname)
            if callable(function):
                self.helperfunctions[functionname] = function
        self.defaultfilters = self.getfilters(excludefilters, limitfilters)

    def getfilters(self, excludefilters=None, limitfilters=None):
        """returns dictionary of available filters, including/excluding those in 
        the given lists"""
        filters = {}
        if limitfilters is None:
            # use everything available unless instructed
            limitfilters = dir(self)
        if excludefilters is None:
            excludefilters = {}
        for functionname in limitfilters:
            if functionname in excludefilters: continue
            if functionname in self.helperfunctions: continue
            if functionname == "errorhandler": continue
            filterfunction = getattr(self, functionname, None)
            if not callable(filterfunction): continue
            filters[functionname] = filterfunction
        return filters

    def setconfig(self, config):
        """sets the accelerator list"""
        self.config = config
        self.accfilters = [prefilters.filteraccelerators(accelmarker) for accelmarker in self.config.accelmarkers]
        self.varfilters = [prefilters.filtervariables(startmatch, endmatch, prefilters.varname)
                for startmatch, endmatch in self.config.varmatches]
        self.removevarfilter = [prefilters.filtervariables(startmatch, endmatch, prefilters.varnone)
                for startmatch, endmatch in self.config.varmatches]

    def setsuggestionstore(self, store):
        """Sets the filename that a checker should use for evaluating suggestions."""
        self.suggestion_store = store

    def filtervariables(self, str1):
        """filter out variables from str1"""
        return helpers.multifilter(str1, self.varfilters)

    def removevariables(self, str1):
        """remove variables from str1"""
        return helpers.multifilter(str1, self.removevarfilter)

    def filteraccelerators(self, str1, acceptlist=None):
        """filter out accelerators from str1"""
        return helpers.multifilter(str1, self.accfilters, acceptlist)

    def filterwordswithpunctuation(self, str1):
        """replaces words with punctuation with their unpunctuated equivalents"""
        return prefilters.filterwordswithpunctuation(str1)

    def filterxml(self, str1):
        """filter out XML from the string so only text remains"""
        return tag_re.sub("", str1)

    def run_test(self, test, unit):
        """Runs the given test on the given unit.
        
        Note that this can raise a FilterFailure as part of normal operation"""
        return test(unit)

    def run_filters(self, unit):
        """run all the tests in this suite, return failures as testname, message_or_exception"""
        failures = {}
        ignores = self.config.lang.ignoretests[:]
        functionnames = self.defaultfilters.keys()
        priorityfunctionnames = self.preconditions.keys()
        otherfunctionnames = filter(lambda functionname: functionname not in self.preconditions, functionnames)
        for functionname in priorityfunctionnames + otherfunctionnames:
            if functionname in ignores:
                continue
            filterfunction = getattr(self, functionname, None)
            # this filterfunction may only be defined on another checker if using TeeChecker
            if filterfunction is None:
                continue
            filtermessage = filterfunction.__doc__
            try:
                filterresult = self.run_test(filterfunction, unit)
            except FilterFailure, e:
                filterresult = False
                filtermessage = str(e).decode('utf-8')
            except Exception, e:
                if self.errorhandler is None:
                    raise ValueError("error in filter %s: %r, %r, %s" % \
                            (functionname, unit.source, unit.target, e))
                else:
                    filterresult = self.errorhandler(functionname, unit.source, unit.target, e)
            if not filterresult:
                # we test some preconditions that aren't actually a cause for failure
                if functionname in self.defaultfilters:
                    failures[functionname] = filtermessage
                if functionname in self.preconditions:
                    for ignoredfunctionname in self.preconditions[functionname]:
                        ignores.append(ignoredfunctionname)
        return failures

class TranslationChecker(UnitChecker):
    """A checker that passes source and target strings to the checks, not the 
    whole unit.
    
    This provides some speedup and simplifies testing."""
    def __init__(self, checkerconfig=None, excludefilters=None, limitfilters=None, errorhandler=None):
        super(TranslationChecker, self).__init__(checkerconfig, excludefilters, limitfilters, errorhandler)

    def run_test(self, test, unit):
        """Runs the given test on the given unit.
        
        Note that this can raise a FilterFailure as part of normal operation."""
        if self.hasplural:
            for pluralform in unit.target.strings:
                if not test(self.str1, pluralform):
                    return False
            else:
                return True
        else:
            return test(self.str1, self.str2)

    def run_filters(self, unit):
        """Do some optimisation by caching some data of the unit for the benefit 
        of run_test()."""
        self.str1 = data.forceunicode(unit.source)
        self.str2 = data.forceunicode(unit.target)
        self.hasplural = unit.hasplural()
        return super(TranslationChecker, self).run_filters(unit)

class TeeChecker:
    """A Checker that controls multiple checkers."""
    def __init__(self, checkerconfig=None, excludefilters=None, limitfilters=None, 
            checkerclasses=None, errorhandler=None, languagecode=None):
        """construct a TeeChecker from the given checkers"""
        self.limitfilters = limitfilters
        if checkerclasses is None:
            checkerclasses = [StandardChecker]
        self.checkers = [checkerclass(checkerconfig=checkerconfig, excludefilters=excludefilters, limitfilters=limitfilters, errorhandler=errorhandler) for checkerclass in checkerclasses]
        if languagecode:
            for checker in self.checkers:
                checker.config.updatetargetlanguage(languagecode)
            # Let's hook up the language specific checker
            lang_checker = self.checkers[0].config.lang.checker
            if lang_checker:
                self.checkers.append(lang_checker)

        self.combinedfilters = self.getfilters(excludefilters, limitfilters)
        self.config = checkerconfig or self.checkers[0].config

    def getfilters(self, excludefilters=None, limitfilters=None):
        """returns dictionary of available filters, including/excluding those in 
        the given lists"""
        if excludefilters is None:
            excludefilters = {}
        filterslist = [checker.getfilters(excludefilters, limitfilters) for checker in self.checkers]
        self.combinedfilters = {}
        for filters in filterslist:
            self.combinedfilters.update(filters)
        # TODO: move this somewhere more sensible (a checkfilters method?)
        if limitfilters is not None:
            for filtername in limitfilters:
                if not filtername in self.combinedfilters:
                    import sys
                    print >> sys.stderr, "warning: could not find filter %s" % filtername
        return self.combinedfilters

    def run_filters(self, unit):
        """run all the tests in the checker's suites"""
        failures = {}
        for checker in self.checkers:
            failures.update(checker.run_filters(unit))
        return failures

    def setsuggestionstore(self, store):
        """Sets the filename that a checker should use for evaluating suggestions."""
        for checker in self.checkers:
            checker.setsuggestionstore(store)


class StandardChecker(TranslationChecker):
    """The basic test suite for source -> target translations."""
    def untranslated(self, str1, str2):
        """checks whether a string has been translated at all"""
        str2 = prefilters.removekdecomments(str2)
        return not (len(str1.strip()) > 0 and len(str2) == 0)

    def unchanged(self, str1, str2):
        """checks whether a translation is basically identical to the original string"""
        str1 = self.filteraccelerators(str1)
        str2 = self.filteraccelerators(str2)
        if len(str1.strip()) == 0:
            return True
        if str1.isupper() and str1 == str2:
            return True
        if self.config.notranslatewords:
            words1 = str1.split()
            if len(words1) == 1 and [word for word in words1 if word in self.config.notranslatewords]:
                return True
        str1 = self.removevariables(str1)
        str2 = self.removevariables(str2)
        if not (str1.strip().isdigit() or len(str1) < 2 or decoration.ispurepunctuation(str1.strip())) and (str1.strip().lower() == str2.strip().lower()):
            raise FilterFailure("please translate")
        return True

    def blank(self, str1, str2):
        """checks whether a translation only contains spaces"""
        len1 = len(str1.strip())
        len2 = len(str2.strip())
        return not (len1 > 0 and len(str2) != 0 and len2 == 0)

    def short(self, str1, str2):
        """checks whether a translation is much shorter than the original string"""
        len1 = len(str1.strip())
        len2 = len(str2.strip())
        return not ((len1 > 0) and (0 < len2 < (len1 * 0.1)) or ((len1 > 1) and (len2 == 1)))

    def long(self, str1, str2):
        """checks whether a translation is much longer than the original string"""
        len1 = len(str1.strip())
        len2 = len(str2.strip())
        return not ((len1 > 0) and (0 < len1 < (len2 * 0.1)) or ((len1 == 1) and (len2 > 1))) 

    def escapes(self, str1, str2):
        """checks whether escaping is consistent between the two strings"""
        if not helpers.countsmatch(str1, str2, ("\\", "\\\\")):
            escapes1 = u", ".join([u"'%s'" % word for word in str1.split() if "\\" in word])
            escapes2 = u", ".join([u"'%s'" % word for word in str2.split() if "\\" in word])
            raise SeriousFilterFailure(u"escapes in original (%s) don't match escapes in translation (%s)" % (escapes1, escapes2))
        else:
            return True

    def newlines(self, str1, str2):
        """checks whether newlines are consistent between the two strings"""
        if not helpers.countsmatch(str1, str2, ("\n", "\r")):
            raise FilterFailure("line endings in original don't match line endings in translation")
        else:
            return True

    def tabs(self, str1, str2):
        """checks whether tabs are consistent between the two strings"""
        if not helpers.countmatch(str1, str2, "\t"):
            raise SeriousFilterFailure("tabs in original don't match tabs in translation")
        else:
            return True


    def singlequoting(self, str1, str2):
        """checks whether singlequoting is consistent between the two strings"""
        str1 = self.filterwordswithpunctuation(self.filteraccelerators(self.filtervariables(str1)))
        str2 = self.filterwordswithpunctuation(self.filteraccelerators(self.filtervariables(str2)))
        return helpers.countsmatch(str1, str2, ("'", "''", "\\'"))

    def doublequoting(self, str1, str2):
        """checks whether doublequoting is consistent between the two strings"""
        str1 = self.filteraccelerators(self.filtervariables(str1))
        str1 = self.filterxml(str1)
        str1 = self.config.lang.punctranslate(str1)
        str2 = self.filteraccelerators(self.filtervariables(str2))
        str2 = self.filterxml(str2)
        return helpers.countsmatch(str1, str2, ('"', '""', '\\"', u"«", u"»"))

    def doublespacing(self, str1, str2):
        """checks for bad double-spaces by comparing to original"""
        str1 = self.filteraccelerators(str1)
        str2 = self.filteraccelerators(str2)
        return helpers.countmatch(str1, str2, "  ")

    def puncspacing(self, str1, str2):
        """checks for bad spacing after punctuation"""
        if str1.find(u" ") == -1:
            return True
        str1 = self.filteraccelerators(self.filtervariables(str1))
        str1 = self.config.lang.punctranslate(str1)
        str2 = self.filteraccelerators(self.filtervariables(str2))
        for puncchar in self.config.punctuation:
            plaincount1 = str1.count(puncchar)
            plaincount2 = str2.count(puncchar)
            if not plaincount1 or plaincount1 != plaincount2:
                continue
            spacecount1 = str1.count(puncchar+" ")
            spacecount2 = str2.count(puncchar+" ")
            if spacecount1 != spacecount2:
                # handle extra spaces that are because of transposed punctuation
                if str1.endswith(puncchar) != str2.endswith(puncchar) and abs(spacecount1-spacecount2) == 1:
                    continue
                return False
        return True

    def printf(self, str1, str2):
        """checks whether printf format strings match"""
        count1 = count2 = None
        for var_num2, match2 in enumerate(printf_pat.finditer(str2)):
            count2 = var_num2 + 1
            if match2.group('ord'):
                for var_num1, match1 in enumerate(printf_pat.finditer(str1)):
                    count1 = var_num1 + 1
                    if int(match2.group('ord')) == var_num1 + 1:
                        if match2.group('fullvar') != match1.group('fullvar'):
                            return 0
            else:
                for var_num1, match1 in enumerate(printf_pat.finditer(str1)):
                    count1 = var_num1 + 1
                    if (var_num1 == var_num2) and (match1.group('fullvar') != match2.group('fullvar')):
                        return 0

        if count2 is None:
            if list(printf_pat.finditer(str1)):
                return 0

        if (count1 or count2) and (count1 != count2):
            return 0
        return 1

    def accelerators(self, str1, str2):
        """checks whether accelerators are consistent between the two strings"""
        str1 = self.filtervariables(str1)
        str2 = self.filtervariables(str2)
        messages = []
        for accelmarker in self.config.accelmarkers:
            counter1 = decoration.countaccelerators(accelmarker, self.config.sourcelang.validaccel)
            counter2 = decoration.countaccelerators(accelmarker, self.config.lang.validaccel)
            count1, countbad1 = counter1(str1)
            count2, countbad2 = counter2(str2)
            getaccel = decoration.getaccelerators(accelmarker, self.config.lang.validaccel)
            accel2, bad2 = getaccel(str2)
            if count1 == count2:
                continue
            if count1 == 1 and count2 == 0:
                if countbad2 == 1:
                    messages.append("accelerator %s appears before an invalid accelerator character '%s' (eg. space)" % (accelmarker, bad2[0]))
                else:
                    messages.append("accelerator %s is missing from translation" % accelmarker)
            elif count1 == 0:
                messages.append("accelerator %s does not occur in original and should not be in translation" % accelmarker)
            elif count1 == 1 and count2 > count1:
                messages.append("accelerator %s is repeated in translation" % accelmarker)
            else:
                messages.append("accelerator %s occurs %d time(s) in original and %d time(s) in translation" % (accelmarker, count1, count2))
        if messages:
            if "accelerators" in self.config.criticaltests:
                raise SeriousFilterFailure(messages)
            else:
                raise FilterFailure(messages)
        return True

#    def acceleratedvariables(self, str1, str2):
#        """checks that no variables are accelerated"""
#        messages = []
#        for accelerator in self.config.accelmarkers:
#            for variablestart, variableend in self.config.varmatches:
#                error = accelerator + variablestart
#                if str1.find(error) >= 0:
#                    messages.append("original has an accelerated variable")
#                if str2.find(error) >= 0:
#                    messages.append("translation has an accelerated variable")
#        if messages:
#            raise FilterFailure(messages)
#        return True

    def variables(self, str1, str2):
        """checks whether variables of various forms are consistent between the two strings"""
        messages = []
        mismatch1, mismatch2 = [], []
        varnames1, varnames2 = [], []
        for startmarker, endmarker in self.config.varmatches:
            varchecker = decoration.getvariables(startmarker, endmarker)
            if startmarker and endmarker:
                if isinstance(endmarker, int):
                    redecorate = lambda var: startmarker + var
                else:
                    redecorate = lambda var: startmarker + var + endmarker
            elif startmarker:
                redecorate = lambda var: startmarker + var
            else:
                redecorate = lambda var: var
            vars1 = varchecker(str1)
            vars2 = varchecker(str2)
            if vars1 != vars2:
                # we use counts to compare so we can handle multiple variables
                vars1, vars2 = [var for var in vars1 if vars1.count(var) > vars2.count(var)], [var for var in vars2 if vars1.count(var) < vars2.count(var)]
                # filter variable names we've already seen, so they aren't matched by more than one filter...
                vars1, vars2 = [var for var in vars1 if var not in varnames1], [var for var in vars2 if var not in varnames2]
                varnames1.extend(vars1)
                varnames2.extend(vars2)
                vars1 = map(redecorate, vars1)
                vars2 = map(redecorate, vars2)
                mismatch1.extend(vars1)
                mismatch2.extend(vars2)
        if mismatch1:
            messages.append("do not translate: %s" % ", ".join(mismatch1))
        elif mismatch2:
            messages.append("translation contains variables not in original: %s" % ", ".join(mismatch2))
        if messages and mismatch1:
            raise SeriousFilterFailure(messages)
        elif messages:
            raise FilterFailure(messages)
        return True

    def functions(self, str1, str2):
        """checks that function names are not translated"""
        return helpers.funcmatch(str1, str2, decoration.getfunctions, self.config.punctuation)

    def emails(self, str1, str2):
        """checks that emails are not translated"""
        return helpers.funcmatch(str1, str2, decoration.getemails)

    def urls(self, str1, str2):
        """checks that URLs are not translated"""
        return helpers.funcmatch(str1, str2, decoration.geturls)

    def numbers(self, str1, str2):
        """checks whether numbers of various forms are consistent between the two strings"""
        return helpers.countsmatch(str1, str2, decoration.getnumbers(str1))

    def startwhitespace(self, str1, str2):
        """checks whether whitespace at the beginning of the strings matches"""
        str1 = self.filteraccelerators(self.filtervariables(str1))
        str2 = self.filteraccelerators(self.filtervariables(str2))
        return helpers.funcmatch(str1, str2, decoration.spacestart)

    def endwhitespace(self, str1, str2):
        """checks whether whitespace at the end of the strings matches"""
        str1 = self.filteraccelerators(self.filtervariables(str1))
        str2 = self.filteraccelerators(self.filtervariables(str2))
        return helpers.funcmatch(str1, str2, decoration.spaceend)

    def startpunc(self, str1, str2):
        """checks whether punctuation at the beginning of the strings match"""
        str1 = self.filteraccelerators(self.filtervariables(self.filterwordswithpunctuation(str1)))
        str1 = self.config.lang.punctranslate(str1)
        str2 = self.filteraccelerators(self.filtervariables(self.filterwordswithpunctuation(str2)))
        return helpers.funcmatch(str1, str2, decoration.puncstart, self.config.punctuation)

    def endpunc(self, str1, str2):
        """checks whether punctuation at the end of the strings match"""
        str1 = self.filteraccelerators(self.filtervariables(self.filterwordswithpunctuation(str1)))
        str1 = self.config.lang.punctranslate(str1)
        str2 = self.filteraccelerators(self.filtervariables(self.filterwordswithpunctuation(str2)))
        return helpers.funcmatch(str1, str2, decoration.puncend, self.config.endpunctuation)

    def purepunc(self, str1, str2):
        """checks that strings that are purely punctuation are not changed"""
        # this test is a subset of startandend
        if (decoration.ispurepunctuation(str1)):
            return str1 == str2
        else:
            return not decoration.ispurepunctuation(str2)

    def brackets(self, str1, str2):
        """checks that the number of brackets in both strings match"""
        str1 = self.filtervariables(str1)
        str2 = self.filtervariables(str2)
        messages = []
        missing = []
        extra = []
        for bracket in ("[", "]", "{", "}", "(", ")"):
            count1 = str1.count(bracket)
            count2 = str2.count(bracket)
            if count2 < count1:
                missing.append("'%s'" % bracket)
            elif count2 > count1:
                extra.append("'%s'" % bracket)
        if missing:
            messages.append("translation is missing %s" % ", ".join(missing))
        if extra:
            messages.append("translation has extra %s" % ", ".join(extra))
        if messages:
            raise FilterFailure(messages)
        return True

    def sentencecount(self, str1, str2):
        """checks that the number of sentences in both strings match"""
        sentences1 = len(self.config.sourcelang.sentences(str1))
        sentences2 = len(self.config.lang.sentences(str2))
        if not sentences1 == sentences2:
            raise FilterFailure("The number of sentences differ: %d versus %d" % (sentences1, sentences2))
        return True

    def options(self, str1, str2):
        """checks that options are not translated"""
        str1 = self.filtervariables(str1)
        for word1 in str1.split():
            if word1 != "--" and word1.startswith("--") and word1[-1].isalnum():
                parts = word1.split("=")
                if not parts[0] in str2:
                    raise FilterFailure("The option %s does not occur or is translated in the translation." % parts[0]) 
                if len(parts) > 1 and parts[1] in str2:
                    raise FilterFailure("The parameter %(param)s in option %(option)s is not translated." % {"param": parts[0], "option": parts[1]})
        return True

    def startcaps(self, str1, str2):
        """checks that the message starts with the correct capitalisation"""
        str1 = self.filteraccelerators(str1)
        str2 = self.filteraccelerators(str2)
        if len(str1) > 1 and len(str2) > 1:
            return self.config.sourcelang.capsstart(str1) == self.config.lang.capsstart(str2)
        if len(str1) == 0 and len(str2) == 0:
            return True
        if len(str1) == 0 or len(str2) == 0:
            return False
        return True

    def simplecaps(self, str1, str2):
        """checks the capitalisation of two strings isn't wildly different"""
        str1 = self.removevariables(str1)
        str2 = self.removevariables(str2)
        # TODO: review this. The 'I' is specific to English, so it probably serves
        # no purpose to get sourcelang.sentenceend
        str1 = re.sub(u"[^%s]( I )" % self.config.sourcelang.sentenceend, " i ", str1)
        capitals1 = helpers.filtercount(str1, type(str1).isupper)
        capitals2 = helpers.filtercount(str2, type(str2).isupper)
        alpha1 = helpers.filtercount(str1, type(str1).isalpha)
        alpha2 = helpers.filtercount(str2, type(str2).isalpha)
        # Capture the all caps case
        if capitals1 == alpha1:
            return capitals2 == alpha2
        # some heuristic tests to try and see that the style of capitals is vaguely the same
        if capitals1 == 0 or capitals1 == 1:
            return capitals2 == capitals1
        elif capitals1 < len(str1) / 10:
            return capitals2 < len(str2) / 8
        elif len(str1) < 10:
            return abs(capitals1 - capitals2) < 3
        elif capitals1 > len(str1) * 6 / 10:
            return capitals2 > len(str2) * 6 / 10
        else:
            return abs(capitals1 - capitals2) < (len(str1) + len(str2)) / 6 

    def acronyms(self, str1, str2):
        """checks that acronyms that appear are unchanged"""
        acronyms = []
        allowed = []
        for startmatch, endmatch in self.config.varmatches:
            allowed += decoration.getvariables(startmatch, endmatch)(str1)
        allowed += self.config.musttranslatewords.keys()
        str1 = self.filteraccelerators(self.filtervariables(str1))
        iter = self.config.lang.word_iter(str1)
        str2 = self.filteraccelerators(self.filtervariables(str2))
        #TODO: strip XML? - should provide better error messsages
        # see mail/chrome/messanger/smime.properties.po
        #TODO: consider limiting the word length for recognising acronyms to 
        #something like 5/6 characters
        for word in iter:
            if word.isupper() and len(word) > 1 and word not in allowed:
                if str2.find(word) == -1:
                    acronyms.append(word)
        if acronyms:
            raise FilterFailure("acronyms should not be translated: " + ", ".join(acronyms))
        return True

    def doublewords(self, str1, str2):
        """checks for repeated words in the translation"""
        lastword = ""
        without_newlines = "\n".join(str2.split("\n"))
        words = self.filteraccelerators(self.removevariables(without_newlines)).replace(".", "").lower().split()
        for word in words:
            if word == lastword:
                raise FilterFailure("The word '%s' is repeated" % word)
            lastword = word
        return True

    def notranslatewords(self, str1, str2):
        """checks that words configured as untranslatable appear in the translation too"""
        if not self.config.notranslatewords:
            return True
        str1 = self.filtervariables(str1)
        str2 = self.filtervariables(str2)
        #The above is full of strange quotes and things in utf-8 encoding.
        #single apostrophe perhaps problematic in words like "doesn't"
        for seperator in self.config.punctuation:
            str1 = str1.replace(seperator, u" ")
            str2 = str2.replace(seperator, u" ")
        words1 = self.filteraccelerators(str1).split()
        words2 = self.filteraccelerators(str2).split()
        stopwords = [word for word in words1 if word in self.config.notranslatewords and word not in words2]
        if stopwords:
            raise FilterFailure("do not translate: %s" % (", ".join(stopwords)))
        return True

    def musttranslatewords(self, str1, str2):
        """checks that words configured as definitely translatable don't appear in 
        the translation"""
        if not self.config.musttranslatewords:
            return True
        str1 = self.removevariables(str1)
        str2 = self.removevariables(str2)
        #The above is full of strange quotes and things in utf-8 encoding.
        #single apostrophe perhaps problematic in words like "doesn't"
        for seperator in self.config.punctuation:
            str1 = str1.replace(seperator, " ")
            str2 = str2.replace(seperator, " ")
        words1 = self.filteraccelerators(str1).split()
        words2 = self.filteraccelerators(str2).split()
        stopwords = [word for word in words1 if word in self.config.musttranslatewords and word in words2]
        if stopwords:
            raise FilterFailure("please translate: %s" % (", ".join(stopwords)))
        return True

    def validchars(self, str1, str2):
        """checks that only characters specified as valid appear in the translation"""
        if not self.config.validcharsmap:
            return True
        invalid1 = str1.translate(self.config.validcharsmap)
        invalid2 = str2.translate(self.config.validcharsmap)
        invalidchars = ["'%s' (\\u%04x)" % (invalidchar.encode('utf-8'), ord(invalidchar)) for invalidchar in invalid2 if invalidchar not in invalid1]
        if invalidchars:
            raise FilterFailure("invalid chars: %s" % (", ".join(invalidchars)))
        return True

    def filepaths(self, str1, str2):
        """checks that file paths have not been translated"""
        for word1 in self.filteraccelerators(str1).split():
            if word1.startswith("/"):
                if not helpers.countsmatch(str1, str2, (word1,)):
                    return False
        return True

    def xmltags(self, str1, str2):
        """checks that XML/HTML tags have not been translated"""
        tags1 = tag_re.findall(str1)
        if len(tags1) > 0:
            if (len(tags1[0]) == len(str1)) and not "=" in tags1[0]:
                return True
            tags2 = tag_re.findall(str2)
            properties1 = tagproperties(tags1, self.config.ignoretags)
            properties2 = tagproperties(tags2, self.config.ignoretags)
            filtered1 = []
            filtered2 = []
            for property1 in properties1:
                filtered1 += [intuplelist(property1, self.config.canchangetags)]
            for property2 in properties2:
                filtered2 += [intuplelist(property2, self.config.canchangetags)]
            
            #TODO: consider the consequences of different ordering of attributes/tags
            if filtered1 != filtered2:
                return False
        else:
            # No tags in str1, let's just check that none were added in str2. This 
            # might be useful for fuzzy strings wrongly unfuzzied, for example.
            tags2 = tag_re.findall(str2)
            if len(tags2) > 0:
                return False
        return True

    def kdecomments(self, str1, str2):
        """checks to ensure that no KDE style comments appear in the translation"""
        return str2.find("\n_:") == -1 and not str2.startswith("_:")

    def compendiumconflicts(self, str1, str2):
        """checks for Gettext compendium conflicts (#-#-#-#-#)"""
        return str2.find("#-#-#-#-#") == -1

    def simpleplurals(self, str1, str2):
        """checks for English style plural(s) for you to review"""
        def numberofpatterns(string, patterns):
            number = 0
            for pattern in patterns:
                number += len(re.findall(pattern, string))
            return number

        sourcepatterns = ["\(s\)"]
        targetpatterns = ["\(s\)"]
        sourcecount = numberofpatterns(str1, sourcepatterns)
        targetcount = numberofpatterns(str2, targetpatterns)
        if self.config.lang.nplurals == 1:
            return not targetcount
        return sourcecount == targetcount

    def spellcheck(self, str1, str2):
        """checks words that don't pass a spell check"""
        if not self.config.targetlanguage:
            return True
        str1 = self.filteraccelerators(self.filtervariables(str1), self.config.sourcelang.validaccel)
        str2 = self.filteraccelerators(self.filtervariables(str2), self.config.lang.validaccel)
        ignore1 = []
        messages = []
        for word, index, suggestions in spelling.check(str1, lang="en"):
            ignore1.append(word)
        for word, index, suggestions in spelling.check(str2, lang=self.config.targetlanguage):
            if word in ignore1:
                continue
            # hack to ignore hyphenisation rules
            if word in suggestions:
                continue
            messages.append(u"check spelling of %s (could be %s)" % (word, u" / ".join(suggestions)))
        if messages:
            raise FilterFailure(messages)
        return True

    def credits(self, str1, str2):
        """checks for messages containing translation credits instead of normal translations."""
        return not str1 in self.config.credit_sources

    # If the precondition filter is run and fails then the other tests listed are ignored
    preconditions = {"untranslated": ("simplecaps", "variables", "startcaps",
                                    "accelerators", "brackets", "endpunc",
                                    "acronyms", "xmltags", "startpunc",
                                    "endwhitespace", "startwhitespace",
                                    "escapes", "doublequoting", "singlequoting", 
                                    "filepaths", "purepunc", "doublespacing",
                                    "sentencecount", "numbers", "isfuzzy",
                                    "isreview", "notranslatewords", "musttranslatewords",
                                    "emails", "simpleplurals", "urls", "printf",
                                    "tabs", "newlines", "functions", "options",
                                    "blank", "nplurals"),
                    "blank":        ("simplecaps", "variables", "startcaps",
                                    "accelerators", "brackets", "endpunc",
                                    "acronyms", "xmltags", "startpunc",
                                    "endwhitespace", "startwhitespace",
                                    "escapes", "doublequoting", "singlequoting", 
                                    "filepaths", "purepunc", "doublespacing",
                                    "sentencecount", "numbers", "isfuzzy",
                                    "isreview", "notranslatewords", "musttranslatewords",
                                    "emails", "simpleplurals", "urls", "printf",
                                    "tabs", "newlines", "functions", "options"),
                    "credits":      ("simplecaps", "variables", "startcaps",
                                    "accelerators", "brackets", "endpunc",
                                    "acronyms", "xmltags", "startpunc",
                                    "escapes", "doublequoting", "singlequoting", 
                                    "filepaths", "doublespacing",
                                    "sentencecount", "numbers",
                                    "emails", "simpleplurals", "urls", "printf",
                                    "tabs", "newlines", "functions", "options"),
                   "purepunc":      ("startcaps", "options"),
                   "startcaps":     ("simplecaps",),
                   "endwhitespace": ("endpunc",),
                   "startwhitespace":("startpunc",),
                   "unchanged":     ("doublewords",), 
                   "compendiumconflicts": ("accelerators", "brackets", "escapes", 
                                    "numbers", "startpunc", "long", "variables", 
                                    "startcaps", "sentencecount", "simplecaps",
                                    "doublespacing", "endpunc", "xmltags",
                                    "startwhitespace", "endwhitespace",
                                    "singlequoting", "doublequoting",
                                    "filepaths", "purepunc", "doublewords", "printf") }

# code to actually run the tests (use unittest?)

openofficeconfig = CheckerConfig(
    accelmarkers = ["~"],
    varmatches = [("&", ";"), ("%", "%"), ("%", None), ("%", 0), ("$(", ")"), ("$", "$"), ("${", "}"), ("#", "#"), ("#", 1), ("#", 0), ("($", ")"), ("$[", "]"), ("[", "]"), ("$", None)],
    ignoretags = [("alt", "xml-lang", None), ("ahelp", "visibility", "visible"), ("img", "width", None), ("img", "height", None)],
    canchangetags = [("link", "name", None)]
    )

class OpenOfficeChecker(StandardChecker):
    def __init__(self, **kwargs):
        checkerconfig = kwargs.get("checkerconfig", None)
        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig
        checkerconfig.update(openofficeconfig)
        StandardChecker.__init__(self, **kwargs)

mozillaconfig = CheckerConfig(
    accelmarkers = ["&"],
    varmatches = [("&", ";"), ("%", "%"), ("%", 1), ("$", "$"), ("$", None), ("#", 1), ("${", "}"), ("$(^", ")")],
    criticaltests = ["accelerators"]
    )

class MozillaChecker(StandardChecker):
    def __init__(self, **kwargs):
        checkerconfig = kwargs.get("checkerconfig", None)
        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig
        checkerconfig.update(mozillaconfig)
        StandardChecker.__init__(self, **kwargs)

gnomeconfig = CheckerConfig(
    accelmarkers = ["_"],
    varmatches = [("%", 1), ("$(", ")")],
    credit_sources = [u"translator-credits"]
    )

class GnomeChecker(StandardChecker):
    def __init__(self, **kwargs):
        checkerconfig = kwargs.get("checkerconfig", None)
        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig
        checkerconfig.update(gnomeconfig)
        StandardChecker.__init__(self, **kwargs)

kdeconfig = CheckerConfig(
    accelmarkers = ["&"],
    varmatches = [("%", 1)],
    credit_sources = [u"Your names", u"Your emails", u"ROLES_OF_TRANSLATORS"]
    )

class KdeChecker(StandardChecker):
    def __init__(self, **kwargs):
        # TODO allow setup of KDE plural and translator comments so that they do
        # not create false postives
        checkerconfig = kwargs.get("checkerconfig", None)
        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig
        checkerconfig.update(kdeconfig)
        StandardChecker.__init__(self, **kwargs)

cclicenseconfig = CheckerConfig(varmatches = [("@", "@")])
class CCLicenseChecker(StandardChecker):
    def __init__(self, **kwargs):
        checkerconfig = kwargs.get("checkerconfig", None)
        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig
        checkerconfig.update(cclicenseconfig)
        StandardChecker.__init__(self, **kwargs)

projectcheckers = {
    "openoffice": OpenOfficeChecker,
    "mozilla": MozillaChecker,
    "kde": KdeChecker,
    "wx": KdeChecker,
    "gnome": GnomeChecker,
    "creativecommons": CCLicenseChecker
    }


class StandardUnitChecker(UnitChecker):
    """The standard checks for common checks on translation units."""
    def isfuzzy(self, unit):
        """Check if the unit has been marked fuzzy."""
        return not unit.isfuzzy()

    def isreview(self, unit):
        """Check if the unit has been marked review."""
        return not unit.isreview()

    def nplurals(self, unit):
        """Checks for the correct number of noun forms for plural translations."""
        if unit.hasplural():
            # if we don't have a valid nplurals value, don't run the test
            nplurals = self.config.lang.nplurals
            if nplurals > 0:
                return len(unit.target.strings) == nplurals
        return True

    def hassuggestion(self, unit):
        """Checks if there is at least one suggested translation for this unit."""
        self.suggestion_store = getattr(self, 'suggestion_store', None)
        suggestions = []
        if self.suggestion_store:
            source = unit.source
            suggestions = [unit for unit in self.suggestion_store.units if unit.source == source]
        elif xliff and isinstance(unit, xliff.xliffunit):
            # TODO: we probably want to filter them somehow
            suggestions = unit.getalttrans()
        return not bool(suggestions)


def runtests(str1, str2, ignorelist=()):
    """verifies that the tests pass for a pair of strings"""
    from translate.storage import base
    str1 = data.forceunicode(str1)
    str2 = data.forceunicode(str2)
    unit = base.TranslationUnit(str1)
    unit.target = str2
    checker = StandardChecker(excludefilters=ignorelist)
    failures = checker.run_filters(unit)
    for testname, message in failures:
        print "failure: %s: %s\n  %r\n  %r" % (testname, message, str1, str2)
    return failures

def batchruntests(pairs):
    """runs test on a batch of string pairs"""
    passed, numpairs = 0, len(pairs)
    for str1, str2 in pairs:
        if runtests(str1, str2):
            passed += 1
    print
    print "total: %d/%d pairs passed" % (passed, numpairs)

if __name__ == '__main__':
    testset = [(r"simple", r"somple"),
            (r"\this equals \that", r"does \this equal \that?"),
            (r"this \'equals\' that", r"this 'equals' that"),
            (r" start and end! they must match.", r"start and end! they must match."),
            (r"check for matching %variables marked like %this", r"%this %variable is marked"),
            (r"check for mismatching %variables marked like %this", r"%that %variable is marked"),
            (r"check for mismatching %variables% too", r"how many %variable% are marked"),
            (r"%% %%", r"%%"),
            (r"Row: %1, Column: %2", r"Mothalo: %1, Kholomo: %2"),
            (r"simple lowercase", r"it is all lowercase"),
            (r"simple lowercase", r"It Is All Lowercase"),
            (r"Simple First Letter Capitals", r"First Letters"),
            (r"SIMPLE CAPITALS", r"First Letters"),
            (r"SIMPLE CAPITALS", r"ALL CAPITALS"),
            (r"forgot to translate", r"  ")
            ]
    batchruntests(testset)

