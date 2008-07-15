#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2007 Zuza Software Foundation
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

"""Module to provide a cache of statistics in a database.

@organization: Zuza Software Foundation
@copyright: 2007 Zuza Software Foundation
@license: U{GPL <http://www.fsf.org/licensing/licenses/gpl.html>}
"""

from translate import __version__ as toolkitversion
from translate.storage import factory, base
from translate.misc.multistring import multistring
from translate.lang.common import Common

import MySQLdb as dbapi2
import os.path
import re
import sys
import stat

from statsdb import *

class StatsCache(object):
    """An object instantiated as a singleton for each statsfile that provides 
    access to the database cache from a pool of StatsCache objects."""
    _caches = {}
    defaultfile = None
    con = None
    """This cache's connection"""
    cur = None
    """The current cursor"""

    def __new__(cls, conndict):
        # First see if a cache for this file already exists:
        if str(conndict) in cls._caches:
            return cls._caches[str(conndict)]
        # No existing cache. Let's build a new one and keep a copy
        cache = cls._caches[str(conndict)] = object.__new__(cls)
        cache.con = dbapi2.connect(host=conndict['host'], user=conndict['user'], passwd=conndict['passwd'], db=conndict['db'])
        cache.cur = cache.con.cursor()
        cache.create()
        return cache

    def allowErrors(self, cmd, errlist):
        """Execute a simple SQL query, allowing errors of any type in errlist"""
        try:
            self.cur.execute(cmd)
        except dbapi2.OperationalError, (errid, errstr):
            if errid not in errlist:
                raise

    def create(self):
        """Create all tables and indexes."""
        self.cur.execute("""CREATE TABLE IF NOT EXISTS files(
            fileid INTEGER PRIMARY KEY AUTO_INCREMENT,
            path LONGTEXT NOT NULL,
            mod_info CHAR(50) NOT NULL,
            toolkitbuild INTEGER NOT NULL);""")
        # mod_info should never be larger than about 138 bits as computed by
        # get_mod_info. This is because st_mtime is at most 64 bits, multiplying
        # by 1000 adds at most 10 bits and file_stat.st_size is at most 64 bits.
        # Therefore, we should get away with 50 decimal digits (actually, we need
        # math.log((1 << 139) - 1, 10) = 41.8 characters, but whatever).

        self.allowErrors("""CREATE UNIQUE INDEX filepathindex
            ON files (path(500));""", [1061])

        self.cur.execute("""CREATE TABLE IF NOT EXISTS units(
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            unitid LONGTEXT NOT NULL,
            fileid INTEGER NOT NULL,
            unitindex INTEGER NOT NULL,
            source LONGTEXT NOT NULL,
            target LONGTEXT,
            state INTEGER,
            sourcewords INTEGER,
            targetwords INTEGER);""")
        
        self.allowErrors("""CREATE INDEX fileidindex
            ON units(fileid);""", [1061])

        self.cur.execute("""CREATE TABLE IF NOT EXISTS checkerconfigs(
            configid INTEGER PRIMARY KEY AUTO_INCREMENT,
            config LONGTEXT);""")

        self.allowErrors("""CREATE INDEX configindex
            ON checkerconfigs(config(500));""", [1061])

        self.cur.execute("""CREATE TABLE IF NOT EXISTS uniterrors(
            errorid INTEGER PRIMARY KEY AUTO_INCREMENT,
            unitindex INTEGER NOT NULL,
            fileid INTEGER NOT NULL,
            configid INTEGER NOT NULL,
            name LONGTEXT NOT NULL,
            message LONGTEXT);""")

        self.allowErrors("""CREATE INDEX uniterrorindex
            ON uniterrors(fileid, configid);""", [1061])
        
        self.con.commit()

    def _getfileid(self, filename, opt_mod_info=(-1, -1), check_mod_info=True, store=None, errors_return_empty=False):
        """Attempt to find the fileid of the given file, if it hasn't been
        updated since the last record update.

        None is returned if either the file's record is not found, or if it is
        not up to date.

        @param filename: the filename to retrieve the id for
        @param opt_mod_info: an optional mod_info to consider in addition 
        to the actual mod_info of the given file
        @rtype: String or None
        """
        realpath = os.path.realpath(filename)
        self.cur.execute("""SELECT fileid, mod_info FROM files
                WHERE path=%s;""", (realpath,))
        filerow = self.cur.fetchone()
        try:
            mod_info = max(opt_mod_info, get_mod_info(realpath))        
            if filerow:
                fileid = filerow[0]
                if not check_mod_info:
                    # Update the mod_info of the file
                    self.cur.execute("""UPDATE files 
                            SET mod_info=%s 
                            WHERE fileid=%s;""", (dump_mod_info(mod_info), fileid))
                    return fileid
                if parse_mod_info(filerow[1]) == mod_info:
                    return fileid
            # We can only ignore the mod_info if the row already exists:
            assert check_mod_info
            store = store or factory.getobject(filename)
            return self._cachestore(store, mod_info)
        except (base.ParseError, IOError, OSError, AssertionError):
            if errors_return_empty:
                return -1
            else:
                raise

    def _getstoredcheckerconfig(self, checker):
        """See if this checker configuration has been used before."""
        config = str(checker.config.__dict__)
        self.cur.execute("""SELECT configid, config FROM checkerconfigs WHERE 
            config=%s;""", (config,))
        configrow = self.cur.fetchone()
        if not configrow or configrow[1] != config:
            return None
        else:
            return configrow[0]

    def _cacheunitstats(self, units, fileid, unitindex=None):
        """Cache the statistics for the supplied unit(s)."""
        unitvalues = []
        for index, unit in enumerate(units):
            if unit.istranslatable():
                sourcewords, targetwords = wordsinunit(unit)
                if unitindex:
                    index = unitindex
                # what about plurals in .source and .target?
                unitvalues.append((unit.getid(), fileid, index, \
                                unit.source, unit.target, \
                                sourcewords, targetwords, \
                                statefordb(unit)))
        for v in unitvalues:
            self.cur.execute("""INSERT INTO units
                (unitid, fileid, unitindex, source, target, sourcewords, targetwords, state) 
                values (%s, %s, %s, %s, %s, %s, %s, %s);""",
                v)
        self.con.commit()
        if unitindex:
            return state_strings[statefordb(units[0])]
        return ""

    def _cachestore(self, store, mod_info):
        """Calculates and caches the statistics of the given store 
        unconditionally."""
        realpath = os.path.realpath(store.filename)
        # TODO Figure out when this system call fails
        try:
            os.utime(realpath, (mod_info[0], mod_info[0]))
        except Exception, e:
            print "utime failed: %s" % (str(e))
            pass 
        self.cur.execute("""DELETE FROM files WHERE
            path=%s;""", (realpath,))
        self.cur.execute("""INSERT INTO files 
            (fileid, path, mod_info, toolkitbuild) values (NULL, %s, %s, %s);""", 
            (realpath, dump_mod_info(mod_info), toolkitversion.build))
        fileid = self.cur.lastrowid
        self.cur.execute("""DELETE FROM units WHERE
            fileid=%s""", (fileid,))
        self._cacheunitstats(store.units, fileid)
        return fileid

    def directorytotals(self, dirname):
        """Retrieves the stored statistics for a given directory, all summed.
        
        Note that this does not check for mod_infos or the presence of files."""
        realpath = os.path.realpath(dirname)
        self.cur.execute("""SELECT
            state,
            count(unitid) as total,
            sum(sourcewords) as sourcewords,
            sum(targetwords) as targetwords
            FROM units WHERE fileid IN
                (SELECT fileid from files
                WHERE substr(path, 0, %s)=%s)
            GROUP BY state;""", (len(realpath), realpath))
        totals = emptystats()
        return self.cur.fetchall()

    def filetotals(self, filename, **kwargs):
        """Retrieves the statistics for the given file if possible, otherwise 
        delegates to cachestore()."""
        fileid = None
        if not fileid:
            try:
                fileid = self._getfileid(filename, **kwargs)
            except ValueError, e:
                print >> sys.stderr, str(e)
                return {}


        self.cur.execute("""SELECT 
            state,
            count(unitid) as total,
            sum(sourcewords) as sourcewords,
            sum(targetwords) as targetwords
            FROM units WHERE fileid=%s
            GROUP BY state;""", (fileid,))
        values = self.cur.fetchall()


        totals = emptystats()
        for stateset in values:
            state = state_strings[stateset[0]]          # state
            totals[state] = stateset[1] or 0            # total
            totals[state + "sourcewords"] = stateset[2] # sourcewords
            totals[state + "targetwords"] = stateset[3] # targetwords
        totals["total"] = totals["untranslated"] + totals["translated"] + totals["fuzzy"]
        totals["totalsourcewords"] = totals["untranslatedsourcewords"] + \
                totals["translatedsourcewords"] + \
                totals["fuzzysourcewords"]
        return totals

    def _cacheunitschecks(self, units, fileid, configid, checker, unitindex=None):
        """Helper method for cachestorechecks() and recacheunit()"""
        # We always want to store one dummy error to know that we have actually
        # run the checks on this file with the current checker configuration
        dummy = (-1, fileid, configid, "noerror", "")
        unitvalues = [dummy]
        # if we are doing a single unit, we want to return the checknames
        errornames = []
        for index, unit in enumerate(units):
            if unit.istranslatable():
                # Correctly assign the unitindex
                if unitindex:
                    index = unitindex
                failures = checker.run_filters(unit)
                for checkname, checkmessage in failures.iteritems():
                    unitvalues.append((index, fileid, configid, checkname, checkmessage))
                    errornames.append("check-" + checkname)
        checker.setsuggestionstore(None)

        if unitindex:
            # We are only updating a single unit, so we don't want to add an 
            # extra noerror-entry
            unitvalues.remove(dummy)
            errornames.append("total")

        for v in unitvalues:
            self.cur.execute("""INSERT INTO uniterrors
                (unitindex, fileid, configid, name, message) 
                values (%s, %s, %s, %s, %s);""",
                v)
        self.con.commit()
        return errornames

    def cachestorechecks(self, fileid, store, checker, configid):
        """Calculates and caches the error statistics of the given store 
        unconditionally."""
        # Let's purge all previous failures because they will probably just
        # fill up the database without much use.
        self.cur.execute("""DELETE FROM uniterrors WHERE
            fileid=%s;""", (fileid,))
        self._cacheunitschecks(store.units, fileid, configid, checker)
        return fileid

    def recacheunit(self, filename, checker, unit):
        """Recalculate all information for a specific unit. This is necessary
        for updating all statistics when a translation of a unit took place, 
        for example.
        
        This method assumes that everything was up to date before (file totals,
        checks, checker config, etc."""
        suggestion_filename, suggestion_mod_info = suggestioninfo(filename)
        fileid = self._getfileid(filename, suggestion_mod_info, check_mod_info=False)
        configid = self._getstoredcheckerconfig(checker)
        unitid = unit.getid()
        # get the unit index
        self.cur.execute("""SELECT unitindex FROM units WHERE
            fileid=%s AND unitid=%s;""", (fileid, unitid))
        unitindex = self.cur.fetchone()[0]
        self.cur.execute("""DELETE FROM units WHERE
            fileid=%s AND unitid=%s;""", (fileid, unitid))
        state = [self._cacheunitstats([unit], fileid, unitindex)]
        # remove the current errors
        self.cur.execute("""DELETE FROM uniterrors WHERE
            fileid=%s AND unitindex=%s;""", (fileid, unitindex))
        if suggestion_filename:
            checker.setsuggestionstore(factory.getobject(suggestion_filename, ignore=os.path.extsep+ 'pending'))
        state.extend(self._cacheunitschecks([unit], fileid, configid, checker, unitindex))
        return state
    
    def filechecks(self, filename, checker, store=None, **kwargs):
        """Retrieves the error statistics for the given file if possible, 
        otherwise delegates to cachestorechecks()."""
        suggestion_filename, suggestion_mod_info = suggestioninfo(filename, **kwargs)
        fileid = None
        configid = self._getstoredcheckerconfig(checker)
        try:
            fileid = self._getfileid(filename, suggestion_mod_info, store=store, **kwargs)
            if not configid:
                self.cur.execute("""INSERT INTO checkerconfigs
                    (configid, config) values (NULL, %s);""", 
                    (str(checker.config.__dict__),))
                configid = self.cur.lastrowid
        except ValueError, e:
            print >> sys.stderr, str(e)
            return {}

        def geterrors():
            self.cur.execute("""SELECT 
                name,
                unitindex
                FROM uniterrors WHERE fileid=%s and configid=%s
                ORDER BY unitindex;""", (fileid, configid))
            return self.cur.fetchall()

        values = geterrors()
        if not values:
            # This could happen if we haven't done the checks before, or the
            # file changed, or we are using a different configuration
            store = store or factory.getobject(filename)
            if suggestion_filename:
                checker.setsuggestionstore(factory.getobject(suggestion_filename, ignore=os.path.extsep+ 'pending'))
            self.cachestorechecks(fileid, store, checker, configid)
            values = geterrors()

        errors = {}
        for value in values:
            if value[1] == -1:
                continue
            checkkey = 'check-' + value[0]      #value[0] is the error name
            if not checkkey in errors:
                errors[checkkey] = []
            errors[checkkey].append(value[1])   #value[1] is the unitindex

        return errors

    def filestats(self, filename, checker, store=None, **kwargs):
        """Return a dictionary of property names mapping sets of unit 
        indices with those properties."""
        stats = {"total": [], "translated": [], "fuzzy": [], "untranslated": []}

        stats.update(self.filechecks(filename, checker, store, **kwargs))
        fileid = self._getfileid(filename, store=store, **kwargs)

        self.cur.execute("""SELECT 
            state,
            unitindex
            FROM units WHERE fileid=%s
            ORDER BY unitindex;""", (fileid,))

        values = self.cur.fetchall()
        for value in values:
            stats[state_strings[value[0]]].append(value[1])
            stats["total"].append(value[1])

        return stats
      
    def unitstats(self, filename, _lang=None, store=None, **kwargs):
        # For now, lang and store are unused. lang will allow the user to
        # base stats information on the given language. See the commented
        # line containing stats.update below. 
        """Return a dictionary of property names mapping to arrays which
        map unit indices to property values.
        
        Please note that this is different from filestats, since filestats
        supplies sets of unit indices with a given property, whereas this
        method supplies arrays which map unit indices to given values."""
        stats = {"sourcewordcount": [], "targetwordcount": []}
        
        #stats.update(self.unitchecks(filename, lang, store))
        fileid = self._getfileid(filename, store=store, **kwargs)
        
        self.cur.execute("""SELECT
          sourcewords, targetwords
          FROM units WHERE fileid=%s
          ORDER BY unitindex;""", (fileid,))

        for sourcecount, targetcount in self.cur.fetchall():
            stats["sourcewordcount"].append(sourcecount)
            stats["targetwordcount"].append(targetcount)
        
        return stats
