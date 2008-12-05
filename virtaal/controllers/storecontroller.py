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

from virtaal.models import StoreModel
from virtaal.views import StoreView

from basecontroller import BaseController


class StoreController(BaseController):
    """The controller for all store-level activities."""

    # INITIALIZERS #
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.main_controller.store_controller = self
        self.unit_controller = None # This is set by UnitController itself when it is created

        self.cursor = None
        self.store = None
        self.view = StoreView(self)


    # ACCESSORS #
    def get_store(self):
        return self.store

    def store_is_modified(self):
        if not self.store:
            return False
        return self.store.is_modified()


    # METHODS #
    def get_nplurals(self):
        return self.store and self.store.nplurals or 0

    def get_target_language(self):
        return self.store and self.store.get_target_language() or 'und'

    def get_unit_celleditor(self, unit):
        return self.unit_controller.get_unit_celleditor(unit)

    def open_file(self, filename, uri=''):
        if not self.store:
            self.store = StoreModel(filename)
        else:
            self.store.load_file(filename)
        self.view.load_store(self.store)
        self.view.show()

    def save_file(self, filename=None):
        self.store.save_file(filename)
