#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Zuza Software Foundation
#
# This file is part of Pootle.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Utility classes for handling translation files."""

import os

from django.core.files import File
from django.conf import settings
from django.utils.thread_support import currentThread

from translate.storage import statsdb, factory
from translate.misc.lru import LRUCachingDict


class StatsTuple(object):
    """Encapsulates stats in the in memory cache, needed
    since LRUCachingDict is based on a weakref.WeakValueDictionary
    which cannot reference normal tuples"""
    def __init__(self):
        self.quickstats = None
        self.stats = None
        self.completestats = None
        self.unitstats = None


class TranslationStoreFile(File):
    """A mixin for use alongside django.core.files.base.File, which provides
    additional features for dealing with translation files."""
    
    _stats = LRUCachingDict(settings.PARSE_POOL_SIZE * 5, settings.PARSE_POOL_CULL_FREQUENCY)
    __statscache = {}

    def _get_statscache(self):
        """reuse statsdb database connection, keep a pool of one connection per thread"""
        current_thread = currentThread()
        if current_thread not in self.__statscache:
            self.__statscache[current_thread] = statsdb.StatsCache(settings.STATS_DB_PATH)
        return self.__statscache[current_thread]

    _statscache = property(_get_statscache)

    #FIXME: figure out what this checker thing is
    checker = None

    def _get_store(self):
        """parse file and return TranslationStore object"""
        if not hasattr(self, "_store"):
            #FIXME: translate.storage.base.parsefile closes file for
            #some weird reason, so we sprinkle with opens to make sure
            #things workout
            self.open()
            self._store = factory.getobject(self)
            self.open()
        return self._store
    store = property(_get_store)

    def _get_filename(self):
        return os.path.basename(self.name)
    filename = property(_get_filename)

    def savestore(self):
        self.store.save()

    def _guess_path(self):
        """Most TranslationStoreFile objects will correspond to
        TranslationStoreField instances and have a known path, however
        standalone instances of TranslationStoreFile can come from in-memory
        files or already open file descriptors with no sure way of obtaining a
        path."""
        #FIXME: is name the best substitute for path?
        return self.name
    path = property(_guess_path)
    
    def _flush_stats(self):
        """flush cached stats"""
        self._stats[self.path] = StatsTuple()
        
    def getquickstats(self):
        """Returns the quick statistics (totals only)."""
        stats_tuple = self._stats.setdefault(self.path, StatsTuple())
        if stats_tuple.quickstats is None:
            stats_tuple.quickstats = self._statscache.filetotals(self.path, store=self._get_store) # or statsdb.emptyfiletotals()
        return stats_tuple.quickstats

    def getstats(self):
        """Returns the unit states statistics only."""
        stats_tuple = self._stats.setdefault(self.path, StatsTuple())
        if stats_tuple.stats is None:
            stats_tuple.stats = self._statscache.filestatestats(self.path, store=self._get_store)
        return stats_tuple.stats

    def getcompletestats(self, checker):
        """Return complete stats including quality checks."""
        stats_tuple = self._stats.setdefault(self.path, StatsTuple())
        if stats_tuple.completestats is None:
            stats_tuple.completestats =  self._statscache.filestats(self.path, checker, store=self._get_store)
        return stats_tuple.completestats

    def getunitstats(self):
        stats_tuple = self._stats.setdefault(self.path, StatsTuple())
        if stats_tuple.unitstats is None:
            stats_tuple.unitstats = self._statscache.unitstats(self.path, store=self._get_store)
        return stats_tuple.unitstats

    def reclassifyunit(self, item, checker):
        """Reclassifies all the information in the database and self._stats
        about the given unit."""
        unit = self.instance.getitem(item)
        state = self._statscache.recacheunit(self.path, checker, unit)
        #FIXME: can't we use state to update stats cache instead of invalidating it?
        self._stats[self.path] = StatsTuple()
        return state

    def _get_total(self):
        """Returns a list of translatable unit indices, useful for identifying
        translatable units by their place in translation file (item number)."""
        return self.getstats()['total']
    total = property(_get_total)

    def getitemslen(self):
        """The number of items in the file."""
        return self.getquickstats()['total']

    def addunit(self, unit):
        """Wrapper around TranslationStore.addunit that updates sourceindex on
        the fly.

        Useful for avoiding rebuilding the index of pending files when new
        suggestions are added."""
        self.store.addunit(unit)
        if hasattr(self.store, "sourceindex"):
            self.store.add_unit_to_index(unit)

    def removeunit(self, unit):
        """Removes a unit from store, updates sourceindex on the fly.

        Useful for avoiding rebuilding index of pending files when suggestions
        are removed."""
        self.store.units.remove(unit)
        if hasattr(self.store, "sourceindex"):
            self.store.remove_unit_from_index(unit)

    def getpomtime(self):
        return statsdb.get_mod_info(self.path)


    