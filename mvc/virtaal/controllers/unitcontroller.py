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

from virtaal.views import UnitView

from basecontroller import BaseController


class UnitController(BaseController):
    """Controller for unit-based operations."""

    __gtype_name__ = "UnitController"
    __gsignals__ = {
        'unit_editor_created': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
    }

    # INITIALIZERS #
    def __init__(self, store_controller):
        gobject.GObject.__init__(self)
        self.main_controller = store_controller.main_controller
        self.store_controller = store_controller
        self.store_controller.unit_controller = self

        self.unit_views = {}


    # METHODS #
    def load_unit(self, unit):
        self.current_unit = unit
        self.nplurals = self.store_controller.get_nplurals()
        self.targetlang = self.store_controller.get_target_language()

        if unit in self.unit_views:
            return self.unit_views[unit]

        self.unit_views[unit] = self.view = UnitView(self, unit)
        #self.emit('unit_editor_created', self.view)
        return self.view
