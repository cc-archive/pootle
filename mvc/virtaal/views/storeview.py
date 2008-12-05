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

from baseview import BaseView
from storeviewwidgets import *


# XXX: ASSUMPTION: The model to display is self.controller.store
class StoreView(BaseView):
    """The view of the store and interface to store-level actions."""

    # INITIALIZERS #
    def __init__(self, controller):
        self.controller = controller
        # XXX: While I can't think of a better way to do this, the following line would have to do :/
        self.parent_widget = self.controller.main_controller.view.gui.get_widget('scrolledwindow1')

        self._init_treeview()
        self.load_store(self.controller.store)

    def _init_treeview(self):
        self._treeview = StoreTreeView(self)

    # METHODS #
    def get_current_cursor_pos(self):
        # TODO: This should get the current cursor position from self.controller
        return getattr(self, 'cursor_pos', 0)

    def get_store(self):
        return self.store

    def get_unit_celleditor(self, unit):
        return self.controller.get_unit_celleditor(unit)

    def load_store(self, store):
        self.store = store
        if store:
            self._treeview.set_model(store.store)

    def set_cursor_pos(self, pos):
        # TODO: This should pass "pos" to self.controller.set_cursor_pos()
        self.cursor_pos = pos

    def show(self):
        child = self.parent_widget.get_child()
        self.parent_widget.remove(child)
        child.destroy()
        self.parent_widget.add(self._treeview)
        self._treeview.show()

        if self._treeview.get_model():
            selection = self._treeview.get_selection()
            selection.select_iter(self._treeview.get_model().get_iter_first())
