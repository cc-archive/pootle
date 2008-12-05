#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Virtaal.
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

import gobject
from translate.filters import checks
from translate.storage import factory, statsdb
from translate.storage import ts2 as ts
from translate.storage.poheader import poheader

from virtaal import pan_app

from basemodel import BaseModel


class StoreModel(BaseModel):
    """
    This model represents a translation store/file. It is basically a wrapper
    for the C{translate.storage.store} class. It is mostly based on the old
    C{Document} class from Virtaal's pre-MVC days.
    """

    __gtype_name__ = "StoreModel"

    # INITIALIZERS #
    def __init__(self, filename):
        super(StoreModel, self).__init__()
        self.load_file(filename)


    # SPECIAL METHODS #
    def __getitem__(self, index):
        """Alias for C{get_unit}."""
        return self.get_unit(index)

    def __len__(self):
        if not self._trans_store:
            return -1
        return len(self._valid_units)


    # ACCESSORS #
    def get_filename(self):
        return self._trans_store and self._trans_store.filename or None

    def get_source_language(self):
        """Return the current store's source language."""
        # Copied as-is from Document.get_source_language()
        candidate = self._trans_store.getsourcelanguage()
        if candidate and not candidate in ['und', 'en', 'en_US']:
            return candidate
        else:
            return pan_app.settings.language["sourcelang"]

    def get_target_language(self):
        """Return the current store's target language."""
        # Copied as-is from Document.get_target_language()
        candidate = self._trans_store.gettargetlanguage()
        if candidate and candidate != 'und':
            return candidate
        else:
            return pan_app.settings.language["contentlang"]

    def get_unit(self, index):
        """Get a specific unit by index."""
        return self._trans_store.units[self._valid_units[index]]

    def get_units(self):
        # TODO: Add caching
        """Return the current store's (filtered) units."""
        return [self._trans_store.units[i] for i in self._valid_units]

    # METHODS #
    def load_file(self, filename):
        # Adapted from Document.__init__()
        print 'Loading file', filename
        self._trans_store = factory.getobject(filename)
        self._get_valid_units()
        self.filename = filename
        self.stats = statsdb.StatsCache().filestats(filename, checks.UnitChecker(), self._trans_store)
        self._correct_header(self._trans_store)
        self.nplurals = self._compute_nplurals(self._trans_store)

    def save_file(self, filename=None):
        if filename is None or filename == self.filename:
            self._trans_store.save()
        else:
            self._trans_store.savefile(filename)

    def _compute_nplurals(self, store):
        # FIXME this needs to be pushed back into the stores, we don't want to import each format
        # Copied as-is from Document._compute_nplurals()
        if isinstance(store, poheader):
            nplurals, _pluralequation = store.getheaderplural()
            if nplurals is None:
                # Nothing in the header, so let's use the global settings
                settings = pan_app.settings
                nplurals = settings.language["nplurals"]
                pluralequation = settings.language["plural"]
                if not (int(nplurals) > 0 and pluralequation):
                    # TODO: If we get here, we have to ask the user for "nplurals" and "plural"
                    pass
                store.updateheaderplural(nplurals, pluralequation)
                # If we actually updated something significant, of course the file
                # won't appear changed yet, which is probably what we want.
            return int(nplurals)
        elif isinstance(store, ts.tsfile):
            return store.nplural()
        else:
            return 1

    def _correct_header(self, store):
        """This ensures that the file has a header if it is a poheader type of
        file, and fixes the statistics if we had to add a header."""
        # Copied as-is from Document._correct_header()
        if isinstance(store, poheader) and not store.header():
            store.updateheader(add=True)
            new_stats = {}
            for key, values in stats.iteritems():
                new_stats[key] = [value+1 for value in values]
            stats = new_stats

    def _get_valid_units(self):
        self._valid_units = range(1, len(self._trans_store.units))
