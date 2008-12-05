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
import gtk
import logging
import re
from translate.tools.pogrep import GrepFilter

from basemode import BaseMode


class SearchMode(BaseMode):
    """Search mode - Includes only units matching the given search term."""

    name = 'Search'
    display_name = _("Search")
    widgets = []

    SEARCH_DELAY = 500

    # INITIALIZERS #
    def __init__(self, controller):
        """Constructor.
            @type  controller: virtaal.controllers.ModeController
            @param controller: The ModeController that managing program modes."""
        self.controller = controller
        self._create_widgets()

        self.filter = self.makefilter()
        self.select_first_match = True
        self._search_timeout = 0

    def _create_widgets(self):
        # Widgets for search functionality (in first row)
        self.ent_search = gtk.Entry()
        self.ent_search.connect('changed', self._on_search_text_changed)
        self.ent_search.connect('activate', self._on_entry_activate)
        self.btn_search = gtk.Button(_('Search'))
        self.btn_search.connect('clicked', self._on_search_clicked)
        self.chk_casesensitive = gtk.CheckButton(_('_Case sensitive'))
        self.chk_casesensitive.connect('toggled', self._refresh_proxy)
        self.chk_regex = gtk.CheckButton(_("_Regular expression"))
        self.chk_regex.connect('toggled', self._refresh_proxy)

        # Widgets for replace (second row)
        self.lbl_replace = gtk.Label(_('Replace with'))
        self.ent_replace = gtk.Entry()
        self.btn_replace = gtk.Button(_('Replace'))
        self.btn_replace.connect('clicked', self._on_replace_clicked)
        self.chk_replace_all = gtk.CheckButton(_('Replace All'))

        self.Widgets = [
            self.ent_search, self.btn_search, self.chk_casesensitive, self.chk_regex,
            self.lbl_replace, self.ent_replace, self.btn_replace, self.chk_replace_all
        ]

        self.default_base = gtk.widget_get_default_style().base[gtk.STATE_NORMAL]
        self.default_text = gtk.widget_get_default_style().text[gtk.STATE_NORMAL]


    # METHODS #
    def makefilter(self):
        searchstring = self.ent_search.get_text()
        searchparts = ('source', 'target')
        ignorecase = not self.chk_casesensitive.get_active()
        useregexp = self.chk_regex.get_active()

        return GrepFilter(searchstring, searchparts, ignorecase, useregexp)

    def selected(self):
        cursor = self.controller.main_controller.store_controller.cursor
        if not cursor or not cursor.store:
            return

        self._add_widgets()
        if not self.ent_search.get_text():
            cursor.indices = cursor.store.stats['total']
            cursor.index = cursor.index # "Reload" cursor position
        else:
            self.update_search()

        def grab_focus():
            self.ent_search.grab_focus()
            return False

        # FIXME: The following line is a VERY UGLY HACK, but at least it works.
        gobject.timeout_add(100, grab_focus)

    def update_search(self):
        cursor = self.controller.main_controller.store_controller.cursor
        self.filter = self.makefilter()

        # Filter stats with text in "self.ent_search"
        filtered = []
        i = 0
        for unit in self.controller.main_controller.store_controller.store.get_units():
            if self.filter.filterunit(unit):
                filtered.append(i)
            i += 1

        logging.debug('Search text: %s (%d matches)' % (self.ent_search.get_text(), len(filtered)))

        if filtered:
            self.ent_search.modify_base(gtk.STATE_NORMAL, self.default_base)
            self.ent_search.modify_text(gtk.STATE_NORMAL, self.default_text)

            searchstr = self.ent_search.get_text().decode('utf-8')
            flags = re.UNICODE | re.MULTILINE
            if not self.chk_casesensitive.get_active():
                flags |= re.IGNORECASE
            if not self.chk_regex.get_active():
                searchstr = re.escape(searchstr)
            self.re_search = re.compile(u'(%s)' % searchstr, flags)
            cursor.indices = filtered
        else:
            self.ent_search.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('#f66'))
            self.ent_search.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#fff'))
            self.re_search = None
            # Act like the "Default" mode...
            cursor = cursor.store.stats['total']

        def grabfocus():
            self.ent_search.grab_focus()
            self.ent_search.set_position(-1)
            return False
        gobject.idle_add(grabfocus)

    def unselected(self):
        # TODO: Unhightlight the previously selected unit
        pass

    def _add_widgets(self):
        table = self.controller.view.mode_box

        table.attach(self.ent_search, 2, 3, 0, 1)
        table.attach(self.btn_search, 3, 4, 0, 1)
        table.attach(self.chk_casesensitive, 4, 5, 0, 1)
        table.attach(self.chk_regex, 5, 6, 0, 1)

        table.attach(self.lbl_replace, 1, 2, 1, 2)
        table.attach(self.ent_replace, 2, 3, 1, 2)
        table.attach(self.btn_replace, 3, 4, 1, 2)
        table.attach(self.chk_replace_all, 4, 5, 1, 2)

        table.show_all()


    # EVENT HANDLERS #
    def _on_entry_activate(self, entry):
        self.update_search()

    def _on_replace_clicked(self, btn):
        cursor = self.controller.main_controller.store_controller.cursor
        if not cursor or not self.ent_search.get_text() or not self.ent_replace.get_text():
            return
        self.update_search()

        for unit in cursor.store.units:
            if not self.filter.filterunit(unit):
                continue
            unit.target = unit.target.replace(self.ent_search.get_text(), self.ent_replace.get_text())
            if not self.chk_replace_all.get_active():
                break

        self.update_search()

    def _on_search_clicked(self, btn):
        self.update_search()

    def _on_search_text_changed(self, entry):
        if self._search_timeout:
            gobject.source_remove(self._search_timeout)
            self._search_timeout = 0

        self._search_timeout = gobject.timeout_add(self.SEARCH_DELAY, self.update_search)

    def _refresh_proxy(self, *args):
        self._on_search_text_changed(self.ent_search)
