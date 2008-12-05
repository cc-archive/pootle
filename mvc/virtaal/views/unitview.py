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

from virtaal import unit_editor

from baseview import BaseView


class UnitView(BaseView):
    """View for translation units and its actions."""

    # INITIALIZERS #
    def __init__(self, controller):
        self.controller = controller
        self.editor = None


    # METHODS #
    def load_unit(self, unit):
        if not unit:
            self.editor = None
            return None

        nplurals = self.controller.store_controller.get_nplurals()
        targetlang = self.controller.store_controller.get_target_language()
        self.editor = unit_editor.UnitEditor(unit, nplurals, targetlang)
        self.unit = unit

        return self.editor

    def show(self):
        if self.editor:
            self.editor.show()
