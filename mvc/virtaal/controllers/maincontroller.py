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

from virtaal.controllers import BaseController
from virtaal.settings import Settings
from virtaal.views import MainView


class MainController(BaseController):
    """The main controller that initializes the others and contains the main
        program loop."""

    # INITIALIZERS #
    def __init__(self, store_controller):
        self.store_controller = store_controller
        self.view = MainView(self)


    # ACCESSORS #
    def get_store(self):
        """Returns the store model of the current open translation store or C{None}."""
        return self.store_controller.get_store()

    def get_store_filename(self):
        """Shortcut for C{get_store().get_filename()}, but checks if the store exists."""
        store = self.store_controller.get_store()
        return store and store.get_filename() or None


    # METHODS #
    def open_file(self, filename, uri='', reload=False):
        """Open the file given by C{filename}.
            @returns: The filename opened, or C{None} if an error has occurred."""
        if self.store_controller.store_is_modified():
            response = self.view.show_save_confirm_dialog()
            if response == 'save':
                self.store_controller.save_file()
            elif response == 'cancel':
                return
            # Unnecessary to test for 'discard'

        try:
            self.store_controller.open_file(filename, uri)
            return filename
        except Exception, exc:
            print 'Error opening file: ', exc
            return None

    def save_file(self, filename=''):
        try:
            self.store_controller.save_file(filename)
        except IOError, exc:
            self.view.show_error_dialog(
                message=_("Could not save file.\n\n%(error_message)s\n\nTry saving at a different location." % {error_message: str(e)})
            )

    def quit(self):
        gtk.main_quit()

    def run(self):
        self.main_view.show()
