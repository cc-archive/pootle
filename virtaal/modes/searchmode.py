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
        self._setup_key_bindings()
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

        self.widgets = [
            self.ent_search, self.btn_search, self.chk_casesensitive, self.chk_regex,
            self.lbl_replace, self.ent_replace, self.btn_replace, self.chk_replace_all
        ]

        self.default_base = gtk.widget_get_default_style().base[gtk.STATE_NORMAL]
        self.default_text = gtk.widget_get_default_style().text[gtk.STATE_NORMAL]

    def _setup_key_bindings(self):
        gtk.accel_map_add_entry("<Virtaal>/Edit/Search", gtk.keysyms.F3, 0)

        self.accel_group = gtk.AccelGroup()
        self.accel_group.connect_by_path("<Virtaal>/Edit/Search", self._on_search_activated)

        self.controller.main_controller.view.add_accel_group(self.accel_group)


    # METHODS #
    def makefilter(self):
        searchstring = self.ent_search.get_text()
        searchparts = ('source', 'target')
        ignorecase = not self.chk_casesensitive.get_active()
        useregexp = self.chk_regex.get_active()

        return GrepFilter(searchstring, searchparts, ignorecase, useregexp)

    def selected(self):
        # XXX: Assumption: This method is called when a new file is loaded and that is
        # why we keep a reference to the store's cursor.
        self.storecursor = self.controller.main_controller.store_controller.cursor
        if not self.storecursor or not self.storecursor.store:
            return

        self._add_widgets()
        self._connect_highlighting()
        if not self.ent_search.get_text():
            self.storecursor.indices = self.storecursor.store.stats['total']
        else:
            self.update_search()

        def grab_focus():
            self.ent_search.grab_focus()
            return False

        # FIXME: The following line is a VERY UGLY HACK, but at least it works.
        gobject.timeout_add(100, grab_focus)

    def update_search(self):
        self.filter = self.makefilter()

        # Filter stats with text in "self.ent_search"
        filtered = []
        i = 0
        for unit in self.storecursor.store.get_units():
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
            self.storecursor.indices = filtered
        else:
            self.ent_search.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('#f66'))
            self.ent_search.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#fff'))
            self.re_search = None
            # Act like the "Default" mode...
            self.storecursor.indices = self.storecursor.store.stats['total']

        def grabfocus():
            self.ent_search.grab_focus()
            self.ent_search.set_position(-1)
            return False
        gobject.idle_add(grabfocus)

    def unselected(self):
        # TODO: Unhightlight the previously selected unit
        if getattr(self, '_signalid_cursor_changed', ''):
            self.storecursor.disconnect(self._signalid_cursor_changed)

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

    def _connect_highlighting(self):
        self._signalid_cursor_changed = self.storecursor.connect('cursor-changed', self._on_cursor_changed)

    def _highlight_matches(self):
        self._unhighlight_previous_matches()

        if self.re_search is None:
            return

        unitview = self.controller.main_controller.store_controller.unit_controller.view
        self._prev_unitview = unitview
        for textview in unitview.sources + unitview.targets:
            buff = textview.get_buffer()
            buffstr = buff.get_text(buff.get_start_iter(), buff.get_end_iter()).decode('utf-8')

            # First make sure that the current buffer contains a highlighting tag.
            # Because a gtk.TextTag can only be associated with one gtk.TagTable,
            # we make copies (created by _make_highlight_tag()) to add to all
            # TagTables. If the tag is already added to a given table, a
            # ValueError is raised which we can safely ignore.
            try:
                buff.get_tag_table().add(self._make_highlight_tag())
            except ValueError:
                pass

            select_iters = []
            for match in self.re_search.finditer(buffstr):
                start_iter, end_iter = buff.get_iter_at_offset(match.start()), buff.get_iter_at_offset(match.end())
                buff.apply_tag_by_name('highlight', start_iter, end_iter)

                if textview in unitview.targets and not select_iters and self.select_first_match:
                    select_iters = [start_iter, end_iter]

            if select_iters:
                def do_selection():
                    buff.move_mark_by_name('selection_bound', select_iters[0])
                    buff.move_mark_by_name('insert', select_iters[1])
                    return False
                gobject.idle_add(do_selection)

    def _make_highlight_tag(self):
        tag = gtk.TextTag(name='highlight')
        tag.set_property('background', 'yellow')
        tag.set_property('foreground', 'black')
        return tag

    def _unhighlight_previous_matches(self):
        if not getattr(self, '_prev_unitview', ''):
            return

        for textview in self._prev_unitview.sources + self._prev_unitview.targets:
            buff = textview.get_buffer()
            buff.remove_all_tags(buff.get_start_iter(), buff.get_end_iter())


    # EVENT HANDLERS #
    def _on_entry_activate(self, entry):
        self.update_search()

    def _on_cursor_changed(self, cursor):
        assert cursor is self.storecursor
        self._highlight_matches()

    def _on_replace_clicked(self, btn):
        if not self.storecursor or not self.ent_search.get_text() or not self.ent_replace.get_text():
            return
        self.update_search()

        for unit in self.storecursor.store.units:
            if not self.filter.filterunit(unit):
                continue
            unit.target = unit.target.replace(self.ent_search.get_text(), self.ent_replace.get_text())
            if not self.chk_replace_all.get_active():
                break

        self.update_search()

    def _on_search_activated(self, _accel_group, _acceleratable, _keyval, _modifier):
        """This is called via the accelerator."""
        self.controller.select_mode(self)

    def _on_search_clicked(self, btn):
        self.update_search()

    def _on_search_text_changed(self, entry):
        if self._search_timeout:
            gobject.source_remove(self._search_timeout)
            self._search_timeout = 0

        self._search_timeout = gobject.timeout_add(self.SEARCH_DELAY, self.update_search)

    def _refresh_proxy(self, *args):
        self._on_search_text_changed(self.ent_search)
