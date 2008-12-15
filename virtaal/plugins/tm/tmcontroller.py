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

from virtaal.common import GObjectWrapper
from virtaal.controllers import BaseController

from tmmodel import TMModel
from tmview import TMView


class TMController(BaseController):
    """The logic-filled glue between the TM view and -model."""

    __gtype_name__ = 'TMController'

    # INITIALIZERS #
    def __init__(self, main_controller):
        GObjectWrapper.__init__(self)

        self.main_controller = main_controller
        self.view = TMView(self)
        self.model = TMModel(self)

        self._connect_plugin()

    def _connect_plugin(self):
        self._store_loaded_id = self.main_controller.store_controller.connect('store-loaded', self._on_store_loaded)


    # METHODS #
    def accept_response(self, query_str, matches):
        if query_str == self.current_query:
            self.view.display_matches(matches)

    def send_tm_query(self, unit=None):
        if unit is not None:
            self.unit = unit

        self.current_query = unicode(self.unit.source.strings[0])
        self.model.query(self.current_query)


    # EVENT HANDLERS #
    def _on_cursor_changed(self, cursor):
        self.view.hide()
        self.unit = cursor.model[cursor.index]
        self.send_tm_query()

    def _on_store_loaded(self, storecontroller):
        if getattr(self, '_cursor_changed_id', None):
            storecontroller.disconnect(self._cursor_changed_id)
        self._cursor_changed_id = storecontroller.cursor.connect('cursor-changed', self._on_cursor_changed)
