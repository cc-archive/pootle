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

from virtaal.common import GObjectWrapper
from virtaal.models import StoreModel
from virtaal.views import StoreView

from basecontroller import BaseController
from storecursor import StoreCursor


# TODO: Create an event that is emitted when a cursor is created
class StoreController(BaseController):
    """The controller for all store-level activities."""

    __gtype_name__ = 'StoreController'
    __gsignals__ = {
        'store-loaded': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
    }

    # INITIALIZERS #
    def __init__(self, main_controller):
        GObjectWrapper.__init__(self)

        self.main_controller = main_controller
        self.main_controller.store_controller = self
        self.unit_controller = None # This is set by UnitController itself when it is created

        self.cursor = None
        self.handler_ids = {}
        self._modified = False
        self.store = None
        self.view = StoreView(self)

        self._add_extensions()

    def _add_extensions(self):
        """This method adds auto-correction and -completion.
            This should be moved to its own MVC-classes/plugins."""
        # FIXME: Move this stuff to a more appropriate place.
        def on_store_loaded(storecontroller):
            self.autocomp.add_words_from_units(self.store.get_units())
            self.autocorr.load_dictionary(lang=pan_app.settings.language['contentlang'])
            self.cursor.connect('cursor-changed', on_cursor_change)

        def on_cursor_change(cursor):
            for textview in self.autocomp.widgets:
                buffer = textview.get_buffer()
                bufftext = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter()).decode('utf-8')
                self.autocomp.add_words(self.autocomp.wordsep_re.split(bufftext))

            self.autocomp.clear_widgets()
            self.autocorr.clear_widgets()
            for target in self.unit_controller.view.targets:
                self.autocomp.add_widget(target)
                self.autocorr.add_widget(target)

        from virtaal.common import pan_app
        from virtaal.plugins import AutoCompletor, AutoCorrector
        self.autocomp = AutoCompletor(self.main_controller)
        self.autocorr = AutoCorrector(self.main_controller, acorpath=pan_app.get_abs_data_filename(['virtaal', 'autocorr']))

        self.connect('store-loaded', on_store_loaded)


    # ACCESSORS #
    def get_store(self):
        return self.store

    def is_modified(self):
        return self._modified

    def register_unitcontroller(self, unitcont):
        """@type unitcont: UnitController"""
        if self.unit_controller and 'unitview.unit-modified' in self.handler_ids:
            self.unit_controller.disconnect(self.handler_ids['unitview.unit-modified'])
        self.unit_controller = unitcont
        self.handler_ids['unitview.unit-modified'] = self.unit_controller.connect('unit-modified', self._unit_modified)


    # METHODS #
    def get_nplurals(self, store=None):
        if not store:
            store = self.store
        return store and store.nplurals or 0

    def get_target_language(self, store=None):
        if not store:
            store = self.store
        return store and store.get_target_language() or 'und'

    def get_unit_celleditor(self, unit):
        """Load the given unit in via the C{UnitController} and return
            the C{gtk.CellEditable} it creates."""
        return self.unit_controller.load_unit(unit)

    def select_unit(self, unit):
        """Select the specified unit and scroll to it."""
        i = 0
        for storeunit in self.get_store().get_units():
            if storeunit == unit:
                break
            i += 1

        if not i < len(self.get_store().get_units()):
            raise ValueError('Unit not found.')

        self.cursor.index = i

    def open_file(self, filename, uri=''):
        if not self.store:
            self.store = StoreModel(filename)
        else:
            self.store.load_file(filename)

        self._modified = False
        self.main_controller.set_saveable(self._modified)

        self.cursor = StoreCursor(self.store)

        self.view.load_store(self.store)
        self.view.show()

        self.emit('store-loaded')

    def save_file(self, filename=None):
        self.store.save_file(filename) # store.save_file() will raise an appropriate exception if necessary
        self._modified = False
        self.main_controller.set_saveable(False)


    # EVENT HANDLERS #
    def _unit_modified(self, emitter, unit):
        self._modified = True
        self.main_controller.set_saveable(self._modified)
