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

class FileTotals(object):
    keys = ['translatedsourcewords',
            'fuzzysourcewords',
            'untranslatedsourcewords',
            'translated',
            'fuzzy',
            'untranslated',
            'translatedtargetwords']

    def db_keys(self):
      return ",".join(self.keys)

    def __init__(self, cur):
        self.cur = cur
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS filetotals(
                fileid                  INTEGER PRIMARY KEY AUTO_INCREMENT,
                translatedsourcewords   INTEGER NOT NULL,
                fuzzysourcewords        INTEGER NOT NULL,
                untranslatedsourcewords INTEGER NOT NULL,
                translated              INTEGER NOT NULL,
                fuzzy                   INTEGER NOT NULL,
                untranslated            INTEGER NOT NULL,
                translatedtargetwords   INTEGER NOT NULL);""")

    def new_record(cls, state_for_db=None, sourcewords=None, targetwords=None):
        record = Record(cls.keys, compute_derived_values = cls._compute_derived_values)
        if state_for_db is not None:
            if state_for_db is UNTRANSLATED:
                record['untranslated'] = 1
                record['untranslatedsourcewords'] = sourcewords
            if state_for_db is TRANSLATED:
                record['translated'] = 1
                record['translatedsourcewords'] = sourcewords
                record['translatedtargetwords'] = targetwords                
            elif state_for_db is FUZZY:
                record['fuzzy'] = 1
                record['fuzzysourcewords'] = sourcewords
        return record
        
    new_record = classmethod(new_record)

    def _compute_derived_values(cls, record):
        record["total"]            = record["untranslated"] + \
                                     record["translated"] + \
                                     record["fuzzy"]
        record["totalsourcewords"] = record["untranslatedsourcewords"] + \
                                     record["translatedsourcewords"] + \
                                     record["fuzzysourcewords"]
        record["review"]           = 0
    _compute_derived_values = classmethod(_compute_derived_values)

    def __getitem__(self, fileid):
      self.cur.execute("""
          SELECT %(keys)s
          FROM   filetotals
          WHERE  fileid=%(id)s;""" % {'keys': self.db_keys(), 'id': fileid})
      # These come back as longs...
      result = map(int, self.cur.fetchone())
      return Record(FileTotals.keys, result, self._compute_derived_values)

    def __setitem__(self, fileid, record):
        self.cur.execute("""
            REPLACE into filetotals
            VALUES (%(fileid)d, %(vals)s);
            """ % {'fileid': fileid, 'vals': record.as_string_for_db()})

    def __delitem__(self, fileid):
        self.cur.execute("""
            DELETE FROM filetotals
            WHERE fileid=%s;
        """,  (fileid,))

class StatsCache(object):
    """An object instantiated as a singleton for each statsfile that provides 
    access to the database cache from a pool of StatsCache objects."""
    _caches = {}
    defaultfile = None
    con = None
    """This cache's connection"""
    cur = None
    """The current cursor"""

    def __new__(cls, statsdict={}):
        # First see if a cache for this file already exists:
        if str(statsdict) in cls._caches:
            return cls._caches[str(statsdict)]
        # No existing cache. Let's build a new one and keep a copy
        cache = cls._caches[str(statsdict)] = object.__new__(cls)
        cache.con = dbapi2.connect(**statsdict)
        cache.cur = cache.con.cursor()
        cache.create()
        return cache

    def create(self):
        """Create all tables and indexes."""
        self.file_totals = FileTotals(self.cur)

        self.cur.execute("""CREATE TABLE IF NOT EXISTS files(
            fileid INTEGER PRIMARY KEY AUTO_INCREMENT,
            path LONGTEXT NOT NULL,
            st_mtime INTEGER NOT NULL,
            st_size INTEGER NOT NULL,
            toolkitbuild INTEGER NOT NULL);""")

        try:
          self.cur.execute("""CREATE UNIQUE INDEX filepathindex
            ON files (path(500));""")
        except:
          pass

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
        try:
          self.cur.execute("""CREATE INDEX fileidindex
            ON units(fileid);""")
        except:
          pass

        self.cur.execute("""CREATE TABLE IF NOT EXISTS checkerconfigs(
            configid INTEGER PRIMARY KEY AUTO_INCREMENT,
            config LONGTEXT);""")

        try:
          self.cur.execute("""CREATE INDEX configindex
            ON checkerconfigs(config(500));""")
        except:
          pass

        self.cur.execute("""CREATE TABLE IF NOT EXISTS uniterrors(
            errorid INTEGER PRIMARY KEY AUTO_INCREMENT,
            unitindex INTEGER NOT NULL,
            fileid INTEGER NOT NULL,
            configid INTEGER NOT NULL,
            name LONGTEXT NOT NULL,
            message LONGTEXT);""")

        try:
          self.cur.execute("""CREATE INDEX uniterrorindex
            ON uniterrors(fileid, configid);""")
        except:
          pass
        
        self.con.commit()

    def _getfileid(self, filename, check_mod_info=True, store=None, errors_return_empty=False):
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
        self.cur.execute("""SELECT fileid, st_mtime, st_size FROM files WHERE path=%s;""", (realpath,))
        filerow = self.cur.fetchone()
        try:
            mod_info = get_mod_info(realpath)
            if filerow:
                fileid = filerow[0]
                if not check_mod_info:
                    # Update the mod_info of the file
                    self.cur.execute("""UPDATE files 
                            SET st_mtime=%s, st_size=%s 
                            WHERE fileid=%s;""", (mod_info[0], mod_info[1], fileid))
                    return fileid
                if (filerow[1], filerow[2]) == mod_info:
                    return fileid
            # We can only ignore the mod_info if the row already exists:
            assert check_mod_info        
            store = store or factory.getobject(realpath)
            return self._cachestore(store, realpath, mod_info)
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

    def _cacheunitstats(self, units, fileid, unitindex=None, file_totals_record=FileTotals.new_record()):
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
                file_totals_record = file_totals_record + FileTotals.new_record(statefordb(unit), sourcewords, targetwords)
        # XXX: executemany is non-standard
        for v in unitvalues:
          self.cur.execute("""INSERT INTO units
            (unitid, fileid, unitindex, source, target, sourcewords, targetwords, state) 
            values (%s, %s, %s, %s, %s, %s, %s, %s);""",
            v)
        self.file_totals[fileid] = file_totals_record
        self.con.commit()
        if unitindex:
            return state_strings[statefordb(units[0])]
        return ""

    def _cachestore(self, store, realpath, mod_info):
        """Calculates and caches the statistics of the given store 
        unconditionally."""
        self.cur.execute("""DELETE FROM files WHERE
            path=%s;""", (realpath,))
        self.cur.execute("""INSERT INTO files 
            (fileid, path, st_mtime, st_size, toolkitbuild) values (NULL, %s, %s, %s, %s);""", 
            (realpath, mod_info[0], mod_info[1], toolkitversion.build))
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

    def filetotals(self, filename):
        """Retrieves the statistics for the given file if possible, otherwise 
        delegates to cachestore()."""
        try:
            fileid = self._getfileid(filename)
        except ValueError, e:
            print >> sys.stderr, str(e)
            return {}
        return self.file_totals[fileid]

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

        # XXX: executemany is non-standard
        for u in unitvalues:
          self.cur.execute("""INSERT INTO uniterrors
            (unitindex, fileid, configid, name, message) 
            values (%s, %s, %s, %s, %s);""",
            u)
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

    def get_unit_stats(self, fileid, unitid):
        values = self.cur.execute("""
            SELECT   state, sourcewords, targetwords
            FROM     units
            WHERE    fileid=%s AND unitid=%s
        """, (fileid, unitid))
        return self.cur.fetchone()

    def recacheunit(self, filename, checker, unit):
        """Recalculate all information for a specific unit. This is necessary
        for updating all statistics when a translation of a unit took place, 
        for example.
        
        This method assumes that everything was up to date before (file totals,
        checks, checker config, etc."""
        fileid = self._getfileid(filename, check_mod_info=False)
        configid = self._getstoredcheckerconfig(checker)
        unitid = unit.getid()
        # get the unit index
        totals_without_unit = self.file_totals[fileid] - \
                                   FileTotals.new_record(*self.get_unit_stats(fileid, unitid))
        self.cur.execute("""SELECT unitindex FROM units WHERE
            fileid=%s AND unitid=%s;""", (fileid, unitid))
        unitindex = self.cur.fetchone()[0]
        self.cur.execute("""DELETE FROM units WHERE
            fileid=%s AND unitid=%s;""", (fileid, unitid))
        state = [self._cacheunitstats([unit], fileid, unitindex, totals_without_unit)]
        # remove the current errors
        self.cur.execute("""DELETE FROM uniterrors WHERE
            fileid=%s AND unitindex=%s;""", (fileid, unitindex))
        if os.path.exists(suggestion_filename(filename)):
            checker.setsuggestionstore(factory.getobject(suggestion_filename(filename), ignore=suggestion_extension()))
        state.extend(self._cacheunitschecks([unit], fileid, configid, checker, unitindex))
        return state
    
    def _checkerrors(self, filename, fileid, configid, checker, store):
        def geterrors():
            self.cur.execute("""SELECT 
                name,
                unitindex
                FROM uniterrors WHERE fileid=%s and configid=%s
                ORDER BY unitindex;""", (fileid, configid))
            return self.cur.fetchone(), self.cur

        first, cur = geterrors()
        if first is not None:
            return first, cur

        # This could happen if we haven't done the checks before, or the
        # file changed, or we are using a different configuration
        store = store or factory.getobject(filename)
        if os.path.exists(suggestion_filename(filename)):
            checker.setsuggestionstore(factory.getobject(suggestion_filename(filename), ignore=suggestion_extension()))
        self.cachestorechecks(fileid, store, checker, configid)
        values = geterrors()

    def _geterrors(self, filename, fileid, configid, checker, store):
        result = []
        first, cur = self._checkerrors(filename, fileid, configid, checker, store)
        result.append(first)
        result.extend(cur.fetchall())
        return result

    def _get_config_id(self, fileid, checker):
        configid = self._getstoredcheckerconfig(checker)
        if configid:
            return configid
        self.cur.execute("""INSERT INTO checkerconfigs
            (configid, config) values (NULL, %s);""",
            (str(checker.config.__dict__),))
        return self.cur.lastrowid

    def filechecks(self, filename, checker, store=None):
        """Retrieves the error statistics for the given file if possible,
        otherwise delegates to cachestorechecks()."""
        fileid = None
        configid = None
        try:
            fileid = self._getfileid(filename, store=store)
            configid = self._get_config_id(fileid, checker)
        except ValueError, e:
            print >> sys.stderr, str(e)
            return emptyfilechecks()

        values = self._geterrors(filename, fileid, configid, checker, store)

        errors = emptyfilechecks()
        for value in values:
            if value[1] == -1:
                continue
            checkkey = 'check-' + value[0]      #value[0] is the error name
            if not checkkey in errors:
                errors[checkkey] = []
            errors[checkkey].append(value[1])   #value[1] is the unitindex

        return errors

    def file_fails_test(self, filename, checker, name):
        fileid = self._getfileid(filename)
        configid = self._get_config_id(fileid, checker) 
        self._checkerrors(filename, fileid, configid, checker, None)
        self.cur.execute("""SELECT
            name,
            unitindex
            FROM uniterrors 
            WHERE fileid=%s and configid=%s and name=%s;""", (fileid, configid, name))
        return self.cur.fetchone() is not None

    def filestats(self, filename, checker, store=None):
        """Return a dictionary of property names mapping sets of unit 
        indices with those properties."""
        stats = emptyfilestats()
        stats.update(self.filechecks(filename, checker, store))
        fileid = self._getfileid(filename, store=store)

        self.cur.execute("""SELECT 
            state,
            unitindex
            FROM units WHERE fileid=%s
            ORDER BY unitindex;""", (fileid,))

        values = self.cur.fetchall()
        for value in values:
            stats[state_strings[value[0]]].append(int(value[1]))
            stats["total"].append(int(value[1]))

        return stats
      
    def unitstats(self, filename, _lang=None, store=None):
        # For now, lang and store are unused. lang will allow the user to
        # base stats information on the given language. See the commented
        # line containing stats.update below. 
        """Return a dictionary of property names mapping to arrays which
        map unit indices to property values.
        
        Please note that this is different from filestats, since filestats
        supplies sets of unit indices with a given property, whereas this
        method supplies arrays which map unit indices to given values."""
        stats = emptyunitstats()
        
        #stats.update(self.unitchecks(filename, lang, store))
        fileid = self._getfileid(filename, store=store)
        
        self.cur.execute("""SELECT
          sourcewords, targetwords
          FROM units WHERE fileid=%s
          ORDER BY unitindex;""", (fileid,))

        for sourcecount, targetcount in self.cur.fetchall():
            stats["sourcewordcount"].append(int(sourcecount))
            stats["targetwordcount"].append(int(targetcount))
        
        return stats
