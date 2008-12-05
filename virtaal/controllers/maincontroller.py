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

from virtaal.common import GObjectWrapper, pan_app
from virtaal.views import MainView

from basecontroller import BaseController


class MainController(BaseController):
    """The main controller that initializes the others and contains the main
        program loop."""

    __gtype_name__ = 'MainController'

    # INITIALIZERS #
    def __init__(self):
        GObjectWrapper.__init__(self)
        self.store_controller = None # This is set by StoreController itself when it is created
        self.view = MainView(self)


    # ACCESSORS #
    def get_store(self):
        """Returns the store model of the current open translation store or C{None}."""
        return self.store_controller.get_store()

    def get_store_filename(self):
        """Shortcut for C{get_store().get_filename()}, but checks if the store exists."""
        store = self.store_controller.get_store()
        return store and store.get_filename() or None

    def set_saveable(self, value):
        self.view.set_saveable(value)

    # METHODS #
    def select_unit(self, unit):
        """Select the specified unit in the store view."""
        self.store_controller.select_unit(unit)

    def show_error(self, msg):
        """Shortcut for C{self.view.show_error_dialog()}"""
        return self.view.show_error_dialog(message=msg)

    def show_input(self, title='', msg=''):
        """Shortcut for C{self.view.show_input_dialog()}"""
        return self.view.show_input_dialog(title=title, message=msg)

    def show_prompt(self, title='', msg=''):
        """Shortcut for C{self.view.show_prompt_dialog()}"""
        return self.view.show_prompt_dialog(title=title, message=msg)

    def open_file(self, filename, uri=''):
        """Open the file given by C{filename}.
            @returns: The filename opened, or C{None} if an error has occurred."""
        if self.store_controller.is_modified():
            response = self.view.show_save_confirm_dialog()
            if response == 'save':
                self.store_controller.save_file()
            elif response == 'cancel':
                return
            # Unnecessary to test for 'discard'

        if self.store_controller.store and self.store_controller.store.get_filename() == filename:
            promptmsg = 'You selected the currently open file for opening. Do you want to reload the file?'
            if not self.show_prompt(msg=promptmsg):
                return False

        try:
            result = self.store_controller.open_file(filename, uri)
            return result
        except IOError, exc:
            self.show_error(
                message=_("Could not open file.\n\n%(error_message)s\n\nTry saving at a different location." % {error_message: str(exc)})
            )
            return None
        #except Exception, exc:
        #    print 'Error opening file: ', exc
        #    raise exc
        #    return None

    def save_file(self, filename=None):
        try:
            self.store_controller.save_file(filename)
        except IOError, exc:
            self.show_error(
                message=_("Could not save file.\n\n%(error_message)s\n\nTry saving at a different location." % {error_message: str(exc)})
            )

    def quit(self):
        if self.store_controller.is_modified():
            response = self.view.show_save_confirm_dialog()
            if response == 'save':
                self.store_controller.save_file()
            elif response == 'cancel':
                return

        self.view.quit()

    def run(self):
        self.view.show()
