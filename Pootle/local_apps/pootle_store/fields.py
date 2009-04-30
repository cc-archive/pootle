#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2009 Zuza Software Foundation
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


"""
Utility functions for handling translation files.
"""
import logging
import os

from django.conf import settings
from django.core.files import File
from django.db.models.fields.files import FieldFile, FileField

from translate.storage import factory, statsdb, po
from translate.filters import checks


class TranslationStoreFile(File):
    """
    A mixin for use alongside django.core.files.base.File, which provides
    additional features for dealing with translation files.
    """
    _statscache = statsdb.StatsCache(settings.STATS_DB_PATH)

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

    def savestore(self):
        self.store.save()

    def _guess_path(self):
        """
        most TranslationStoreFile objects will deal with will
        correspond to TranslationStoreField instances and have a known
        path, however standalone instances of TranslationStoreFile can
        come from in memory files or already open file descriptors
        with no sure way of obtaining a path
        """
        #FIXME: is name the best substitute for path?
        return self.name
    path = property(_guess_path)

    def getquickstats(self):
        """returns the quick statistics (totals only)
        """
        return self._statscache.filetotals(self.path, store=self.store) #or statsdb.emptyfiletotals()

    def getstats(self):
        """returns the unit states statistics only"""
        return self._statscache.filestatestats(self.path, store=self.store)
    
    def getcompletestats(self, checker):
        """return complete stats including quality checks
        """
        return self._statscache.filestats(self.path, checker, store=self.store)

    def getunitstats(self):
        return self._statscache.unitstats(self.path, store=self.store)

    def reclassifyunit(self, item, checker=checks.StandardUnitChecker()):
        """Reclassifies all the information in the database and
        self._stats about the given unit
        """
        unit = self.getitem(item)
        self._statscache.recacheunit(self.path, checker, unit)

    def _get_total(self):
        """returns list of translatable unit indeces, useful for
        identifying translatable units by their place in translation
        file (item number)
        """
        return self.getstats()['total']
    total = property(_get_total)
    
    def getitem(self, item):
        """Returns a single unit based on the item number."""
        return self.store.units[self.total[item]]

    def getitemslen(self):
        """gets the number of items in the file
        """
        return self.getquickstats()['total']

    def updateunit(self, item, newvalues, userprefs, languageprefs):
        """updates a translation with a new target value"""

        unit = self.getitem(item)
        
        if newvalues.has_key('target'):
            unit.target = newvalues['target']
        if newvalues.has_key('fuzzy'):
            unit.markfuzzy(newvalues['fuzzy'])
        if newvalues.has_key('translator_comments'):
            unit.removenotes()
            if newvalues['translator_comments']:
                unit.addnote(newvalues['translator_comments'])

        if isinstance(self, po.pofile):
            po_revision_date = time.strftime('%Y-%m-%d %H:%M') + tzstring()
            headerupdates = {'PO_Revision_Date': po_revision_date,
                             'Language': self.languagecode,
                             'X_Generator': self.x_generator}
            if userprefs:
                if getattr(userprefs, 'name', None) and getattr(userprefs, 'email', None):
                    headerupdates['Last_Translator'] = '%s <%s>' % (userprefs.name, userprefs.email)
            self.store.updateheader(add=True, **headerupdates)
            if languageprefs:
                nplurals = getattr(languageprefs, 'nplurals', None)
                pluralequation = getattr(languageprefs, 'pluralequation', None)
                if nplurals and pluralequation:
                    self.store.updateheaderplural(nplurals, pluralequation)
        # If we didn't add a header, savepofile doesn't have to
        # reset the stats, since reclassifyunit will do. This
        # gives us a little speed boost for the common case.
        self.savestore()
        self.reclassifyunit(item)


class TranslationStoreFieldFile(FieldFile, TranslationStoreFile):
    _store_cache = {}

    # redundant redefinition of path to be the same as defined in
    # FieldFile, added here for clarity since TranslationStoreFile
    # uses a different method
    path = property(FieldFile._get_path)
    
    def _get_store(self):
        """ get translation store from dictionary cache, populate if
        store not already cached. """
        #if self.path not in self._store_cache:
        #FIXME: is it possible to not test mod_info on every access?
        self._update_store_cache()
        return self._store_cache[self.path][0]

    def _update_store_cache(self):
        """ add translation store to dictionary cache, replace old
        cached version if needed."""
        mod_info = statsdb.get_mod_info(self.path)

        if self.path not in self._store_cache or self._store_cache[self.path][1] != mod_info:
            logging.debug("cache miss for %s", self.path)
            self._store_cache[self.path] = (factory.getobject(self.path), mod_info)

    def _delete_store_cache(self):
        """ remove traslation store from dictionary cache."""
        if self.path in self._store_cache:
            del(self._store_cache[self.path])

    store = property(_get_store)

    def savestore(self):
        self.store.save()
        self._update_store_cache()
        
    def save(self, name, content, save=True):
        #FIXME: implement save to tmp file then move instead of directly saving
        super(TranslationStoreFieldFile, self).save(name, content, save)
        self._update_store_cache()
        
    def delete(self, save=True):
        self._delete_store_cache()
        super(TranslationStoreFieldFile, self).delete(save)

class TranslationStoreField(FileField):
    attr_class = TranslationStoreFieldFile

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.FileField}
        defaults.update(kwargs)
        return super(TranslationStoreField, self).formfield(**defaults)

