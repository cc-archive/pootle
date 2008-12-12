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

import gtk
import gobject

from virtaal.common import GObjectWrapper
from virtaal.views import BaseView

from tmwidgets import *


class TMView(BaseView, GObjectWrapper):
    """The fake drop-down menu in which the TM matches are displayed."""

    __gtype_name__ = 'TMView'
    __gsignals__ = {
        'tm-match-selected': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }

    # INITIALIZERS #
    def __init__(self, controller):
        GObjectWrapper.__init__(self)

        self.controller = controller
        self.isvisible = False
        self.tmwindow = TMWindow(self)


    # METHODS #
    def display_matches(self, matches):
        liststore = self.tmwindow.liststore

        # Get the currently selected target TextView
        selected = self.controller.main_controller.unit_controller.view.targets[0]
        if selected:
            self.tmwindow.update_geometry(selected.parent)

        for match in matches:
            liststore.append([match])

        if len(liststore) > 0 and not self.isvisible:
            self.show()

    def hide(self):
        """Hide the TM window."""
        self.tmwindow.hide()
        self.isvisible = False

    def show(self):
        """Show the TM window."""
        self.tmwindow.show_all()
        # TODO: Scroll to top
        self.isvisible = True
