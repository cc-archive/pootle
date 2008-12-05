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
from bisect import bisect_left

from virtaal.models import StoreModel
from virtaal.views import StoreView

from basecontroller import BaseController


# TODO: Move the following cursor-class(es) to an appropriate file
class Cursor(gobject.GObject):
    """Manages the current position in the store."""

    __gtype_name__ = "Cursor"

    __gsignals__ = {
        "cursor-changed": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
    }


    # INITIALIZERS #
    def __init__(self, storemodel, indices=None, circular=True):
        super(Cursor, self).__init__()
        if indices is None:
            indices = range(len(storemodel.get_units()))
        self.store = storemodel
        self.indices = indices
        self.circular = circular

        self._curr_pos = 0


    # ACCESSORS #
    def _get_curr_pos(self):
        return self._curr_pos
    def _set_curr_pos(self, value):
        self._curr_pos = value
        self.emit('cursor-changed')
    curr_pos = property(_get_curr_pos, _set_curr_pos)


    # METHODS #
    def current_index(self):
        if len(self.indices) < 1:
            return -1
        return self.indices[self.curr_pos]

    def move(self, offset):
        """Move the cursor C{offset} positions down.
            The cursor will wrap around to the beginning if C{circular=True}
            was given when the cursor was created."""
        # FIXME: Possibly contains off-by-one bug(s)
        if self.curr_pos + offset < len(self.indices):
            self.curr_pos += offset
        elif self.circular:
            self.curr_pos = self.curr_pos + offset - len(self.indices)
        else:
            raise IndexError()
        return self.curr_pos

    def select_index(self, index):
        """Move the cursor to the cursor to the position specified by C{index}."""
        self.curr_pos = bisect_left(self.indices, index)


# TODO: Create an event that is emitted when a cursor is created
class StoreController(BaseController):
    """The controller for all store-level activities."""

    # INITIALIZERS #
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.main_controller.store_controller = self
        self.unit_controller = None # This is set by UnitController itself when it is created

        self.cursor = None
        self.handler_ids = {}
        self._modified = False
        self.store = None
        self.view = StoreView(self)


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

        self.cursor.select_index(i)

    def open_file(self, filename, uri=''):
        if not self.store:
            self.store = StoreModel(filename)
        else:
            self.store.load_file(filename)

        self._modified = False
        self.main_controller.set_saveable(self._modified)

        self.cursor = Cursor(self.store)
        # The above line should be replaced by these below:
        #self.mode.update_for_store(self.store)

        self.view.load_store(self.store)
        self.view.show()

    def save_file(self, filename=None):
        self.store.save_file(filename)
        self._modified = False
        self.main_controller.set_saveable(False)


    # EVENT HANDLERS #
    def _unit_modified(self, emitter, unit):
        self._modified = True
        self.main_controller.set_saveable(self._modified)
