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

from gobject import GObject, SIGNAL_RUN_FIRST, TYPE_INT, TYPE_NONE, TYPE_PYOBJECT, TYPE_STRING

from virtaal.common import GObjectWrapper
from virtaal.views import UnitView

from basecontroller import BaseController


class UnitController(BaseController):
    """Controller for unit-based operations."""

    __gtype_name__ = "UnitController"
    __gsignals__ = {
        'unit-done':           (SIGNAL_RUN_FIRST, TYPE_NONE, (TYPE_PYOBJECT,)),
        'unit-modified':       (SIGNAL_RUN_FIRST, TYPE_NONE, (TYPE_PYOBJECT,)),
        'unit-delete-text':    (SIGNAL_RUN_FIRST, TYPE_NONE, (TYPE_PYOBJECT, TYPE_STRING, TYPE_INT, TYPE_INT, TYPE_INT, TYPE_INT)),
        'unit-insert-text':    (SIGNAL_RUN_FIRST, TYPE_NONE, (TYPE_PYOBJECT, TYPE_STRING, TYPE_STRING, TYPE_INT, TYPE_INT)),
        'unit-paste-start':    (SIGNAL_RUN_FIRST, TYPE_NONE, (TYPE_PYOBJECT, TYPE_STRING, TYPE_PYOBJECT, TYPE_INT)),
    }

    # INITIALIZERS #
    def __init__(self, store_controller):
        GObjectWrapper.__init__(self)

        self.main_controller = store_controller.main_controller
        self.main_controller.unit_controller = self
        self.store_controller = store_controller
        self.store_controller.unit_controller = self

        self.view = UnitView(self)
        self.view.connect('delete-text', self._unit_delete_text)
        self.view.connect('insert-text', self._unit_insert_text)
        self.view.connect('paste-start', self._unit_paste_start)
        self.view.connect('modified', self._unit_modified)
        self.view.connect('unit-done', self._unit_done)
        self.view.enable_signals()

        self.main_controller.connect('controller-registered', self._on_controller_registered)


    # ACCESSORS #
    def get_unit_target(self, target_index):
        return self.view.get_target_n(target_index)

    def set_unit_target(self, target_index, value, cursor_pos=-1, escape=True):
        self.view.set_target_n(target_index, value, cursor_pos, escape=escape)


    # METHODS #
    def load_unit(self, unit):
        self.current_unit = unit
        self.nplurals = self.store_controller.get_nplurals()

        self.view.load_unit(unit)
        return self.view

    def _unit_delete_text(self, unitview, old_text, start_offset, end_offset, cursor_pos, target_num):
        self.emit('unit-delete-text', self.current_unit, old_text, start_offset, end_offset, cursor_pos, target_num)

    def _unit_insert_text(self, unitview, old_text, ins_text, offset, target_num):
        self.emit('unit-insert-text', self.current_unit, old_text, ins_text, offset, target_num)

    def _unit_paste_start(self, unitview, old_text, offsets, target_num):
        self.emit('unit-paste-start', self.current_unit, old_text, offsets, target_num)

    def _unit_modified(self, *args):
        self.emit('unit-modified', self.current_unit)

    def _unit_done(self, widget, unit):
        self.emit('unit-done', unit)


    # EVENT HANDLERS #
    def _on_controller_registered(self, main_controller, controller):
        if controller is main_controller.lang_controller:
            self.main_controller.lang_controller.connect('source-lang-changed', self._on_language_changed)
            self.main_controller.lang_controller.connect('target-lang-changed', self._on_language_changed)

    def _on_language_changed(self, lang_controller, langcode):
        if hasattr(self, 'view'):
            self.view.update_languages()
