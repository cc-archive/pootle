#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of virtaal.
#
# virtaal is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from itertools import chain
import logging
import re

import pango
import gtk
try:
    import gtkspell
except ImportError, e:
    gtkspell = None

from support.partial import partial
import pan_app
from pan_app import _
import markup
from widgets import style
import undo_buffer
from widgets import label_expander

#A regular expression to help us find a meaningful place to position the
#cursor initially.
FIRST_WORD_RE = re.compile("(?m)(?u)^(<[^>]+>|\\\\[nt]|[\W$^\n])*(\\b|\\Z)")

def on_key_press_event(widget, event, *_args):
    if event.keyval == gtk.keysyms.Return or event.keyval == gtk.keysyms.KP_Enter:
        widget.parent.emit('key-press-event', event)
        return True
    return False

class Widget(object):
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self._height = 0
        self._widget = None

    def v_padding(self):
        raise NotImplementedError()

    def h_padding(self):
        raise NotImplementedError()

    def height(self, _widget, _width):
        raise NotImplementedError()
    
    def cache_height(self, height):
        self._height = height
        return height
    
    cached_height = property(lambda self: self._height)

    def make_pango_layout(self, text, widget, width):
        pango_layout = pango.Layout(widget.get_pango_context())
        pango_layout.set_width((width - self.h_padding()) * pango.SCALE)
        pango_layout.set_wrap(pango.WRAP_WORD)
        pango_layout.set_text(text or "")
        return pango_layout
    
    widget = property(lambda self: self._widget)
    
    def post_make_widget(self, widget, names):
        self._widget = widget
        widget._layout = self
        # Skip Enter key processing
        widget.connect('key-press-event', on_key_press_event)
        return widget, names
    
    def make_widget(self):
        raise NotImplementedError()

def get_layout(widget):
    return widget._layout

class Layout(Widget):
    def __init__(self, name, child):
        super(Layout, self).__init__(name)
        self.child = child
        self.children.append(self.child)
        self.child.parent = self
        
    def height(self, widget, width):
        return self.cache_height(self.child.height(widget, width / 2))

    def make_widget(self):
        table = gtk.Table(rows=1, columns=4, homogeneous=True)
        names = {self.name: table}
        child, child_names = self.child.make_widget()
        table.attach(child, 1, 3, 0, 1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL|gtk.EXPAND)
        names.update(child_names)
    
        return self.post_make_widget(table, names)
        
class List(Widget):
    def __init__(self, name, children=None):
        super(List, self).__init__(name)

        if children != None:
            self.children = children

        for child in self.children:
            child.parent = self

    def add(self, widget):
        self.children.append(widget)

    def fill_list(self, box):
        names = {self.name: box}
        for child in self.children:
            child_widget, child_names = child.make_widget()
            box.pack_start(child_widget, fill=True, expand=True)
            names.update(child_names)
        #box.connect('key-press-event', on_key_press_event)
        return box, names

class VList(List):
    def height(self, widget, width):
        h = sum(child.height(widget, width) for child in self.children) + \
            self.v_padding() * (len(self.children) - 1)
        return self.cache_height(h)

    def v_padding(self):
        return 0

    def h_padding(self):
        return 0
    
    def make_widget(self):
        box, names = self.fill_list(gtk.VBox(self.v_padding()))
        return self.post_make_widget(box, names)

class HList(List):
    def height(self, widget, width):
        item_width = (width - len(self.children) * (self.h_padding() + 1)) / len(self.children)
        h = 2*self.v_padding() + max(child.height(widget, item_width) for child in self.children)
        return self.cache_height(h)

    def v_padding(self):
        return 0

    def h_padding(self):
        return 0

    def make_widget(self):
        box, names = self.fill_list(gtk.HBox())
        return self.post_make_widget(box, names)

class TextBox(Widget):
    def __init__(self, name, get_text, set_text, editable):
        super(TextBox, self).__init__(name)
        self.get_text = get_text
        self.set_text = set_text
        self.next     = None
        self.editable = editable

    def v_padding(self):
        return 2*style.style[gtk.Widget]['focus-line-width'] + 2*style.style[gtk.Container]['border-width']

    def h_padding(self):
        # A TextBox in Virtaal is composed of a ScrolledWindow which contains a TextView.
        # See gtkscrolledwindow.c:gtk_scrolled_window_size_request and
        # gtktextview.c:gtk_text_view_size_request in the GTK source for the source of this
        # calculation.
        return style.style[gtk.TextView]['left-margin'] + style.style[gtk.TextView]['right-margin'] + \
               2*style.style[gtk.Container]['border-width']

    def height(self, widget, width):
        # TODO: Look at GTK C Source to get precise height calculations
        _w, h = self.make_pango_layout(markup.escape(self.get_text()), widget, width).get_pixel_size()
    
        return self.cache_height(h + self.v_padding())

def add_spell_checking(text_view, language):
    global gtkspell
    if gtkspell:
        try:
            spell = gtkspell.Spell(text_view)
            spell.set_language(language)
        except:
            logging.info(_("Could not initialize spell checking"))
            gtkspell = None

class SourceTextBox(TextBox):
    def __init__(self, name, get_text, set_text):
        super(SourceTextBox, self).__init__(name, get_text, set_text, False)

    def make_widget(self):
        text_view = gtk.TextView()
    
        add_spell_checking(text_view, pan_app.settings.language["sourcelang"])
    
        text_view.get_buffer().set_text(markup.escape(self.get_text()))
        text_view.set_editable(self.editable)
        text_view.set_wrap_mode(gtk.WRAP_WORD)
        text_view.set_border_window_size(gtk.TEXT_WINDOW_TOP, 1)
    
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scrolled_window.add(text_view)
    
        return self.post_make_widget(scrolled_window, {self.name: scrolled_window})

def focus_text_view(text_view):
    text_view.grab_focus()

    buf = text_view.get_buffer()
    text = buf.get_text(buf.get_start_iter(), buf.get_end_iter())

    translation_start = FIRST_WORD_RE.match(text).span()[1]
    buf.place_cursor(buf.get_iter_at_offset(translation_start))

class TargetTextBox(TextBox):
    def __init__(self, name, get_text, set_text):
        super(TargetTextBox, self).__init__(name, get_text, set_text, True)

    def make_widget(self):
        text_view = gtk.TextView()
    
        add_spell_checking(text_view, pan_app.settings.language["contentlang"])
    
        def get_range(buf, left_offset, right_offset):
            return buf.get_text(buf.get_iter_at_offset(left_offset),
                                buf.get_iter_at_offset(right_offset))
    
        def on_text_view_key_press_event(text_view, event):
            """Handle special keypresses in the textarea."""
            # Automatically move to the next line if \n is entered
    
            if event.keyval == gtk.keysyms.n:
                buf = text_view.get_buffer()
                if get_range(buf, buf.props.cursor_position-1, buf.props.cursor_position) == "\\":
                    buf.insert_at_cursor('n\n')
                    text_view.scroll_mark_onscreen(buf.get_insert())
                    return True
            return False
    
        def on_text_view_n_press_event(text_view, event, *_args):
            if event.keyval == gtk.keysyms.Return or event.keyval == gtk.keysyms.KP_Enter:
                self = get_layout(text_view.parent)
                if self.next != None:
                    next_text_view = self.next.widget.child
                    focus_text_view(next_text_view)
    
                else:
                    #self.must_advance = True
                    text_view.parent.emit('key-press-event', event)
                return True
            return False
    
        def on_change(buf):
            self.set_text(markup.unescape(buf.get_text(buf.get_start_iter(), buf.get_end_iter())))
    
        buf = undo_buffer.add_undo_to_buffer(text_view.get_buffer())
        undo_buffer.execute_without_signals(buf, lambda: buf.set_text(markup.escape(self.get_text())))
        buf.connect('changed', on_change)
    
        text_view.set_editable(self.editable)
        text_view.set_wrap_mode(gtk.WRAP_WORD)
        text_view.set_border_window_size(gtk.TEXT_WINDOW_TOP, 1)
        text_view.connect('key-press-event', on_text_view_n_press_event)
        text_view.connect('key-press-event', on_text_view_key_press_event)
    
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(text_view)
    
        return self.post_make_widget(scrolled_window, {self.name: scrolled_window})

class Comment(SourceTextBox):
    def __init__(self, name, get_text, set_text=lambda value: None):
        super(Comment, self).__init__(name, get_text, set_text)

    def v_padding(self):
        return 2

    def height(self, widget, width):
        # TODO: The calculations here yield incorrect results. We'll have to look at this.
        text = self.get_text()
        if text == "":     # If we have an empty string, we squash the self box
            return self.cache_height(0)
        _w, h = self.make_pango_layout(text[0], widget, width).get_pixel_size()
        return self.cache_height(h + self.v_padding())

    def make_widget(self):
        text_box, names = SourceTextBox.make_widget(self)
        expander = label_expander.LabelExpander(text_box, self.get_text)
        return self.post_make_widget(expander, names)

class Option(Widget):
    def __init__(self, name, label, get_option, set_option):
        super(Option, self).__init__(name)
        self.label = label
        self.get_option = get_option
        self.set_option = set_option

    def v_padding(self):
        return 2

    def h_padding(self):
        # See gtkcheckbutton.c
        # requisition->width += (indicator_size + indicator_spacing * 3 + 2 * (focus_width + focus_pad));
        return style.style[gtk.CheckButton]['indicator-size'] + style.style[gtk.CheckButton]['indicator-spacing'] * 3 + \
               2 * (style.style[gtk.Widget]['focus-line-width'] + style.style[gtk.Widget]['focus-padding'])

    def height(self, widget, width):
        _w, h = self.make_pango_layout(self.label, widget, width).get_pixel_size()
        return self.cache_height(h + self.v_padding())

    def make_widget(self):
        def on_toggled(widget, *_args):
            if widget.get_active():
                self.set_option(True)
            else:
                self.set_option(False)
    
        check_button = gtk.CheckButton(label=self.label)
        check_button.connect('toggled', on_toggled)
        if self.get_option():
            check_button.set_active(True)
        return self.post_make_widget(check_button, {'self-%s' % self.name: check_button})

def get_source(unit, index):
    if unit.hasplural():
        return unit.source.strings[index]
    elif index == 0:
        return unit.source
    else:
        raise IndexError()

def get_target(unit, nplurals, index):
    if unit.hasplural():
        if nplurals != len(unit.target.strings):
            targets = nplurals * [u""]
            targets[:len(unit.target.strings)] = unit.target.strings
            unit.target = targets

        return unit.target.strings[index]
    elif index == 0:
        return unit.target
    else:
        raise IndexError()

def set(unit, attr, index, value):
    if unit.hasplural():
        str_list = list(getattr(unit, attr).strings)
        str_list[index] = value
        setattr(unit, attr, str_list)
    elif index == 0:
        setattr(unit, attr, value)
    else:
        raise IndexError()

def set_source(unit, index, value):
    set(unit, 'source', index, value)

def set_target(unit, index, value):
    set(unit, 'target', index, value)

def num_sources(unit):
    if unit.hasplural():
        return len(unit.source.strings)
    else:
        return 1

def num_targets(unit, nplurals):
    if unit.hasplural():
        return nplurals
    else:
        return 1

def get_options(unit):
    return [Option('option-fuzzy', _('F_uzzy'), lambda: unit.isfuzzy(), lambda value: unit.markfuzzy(value))]

def build_layout(unit, nplurals):
    """Construct a blueprint which can be used to build editor widgets
    or to compute the height required to display editor widgets; this
    latter operation is required by the TreeView.

    @param unit: A translation unit used by the translate toolkit.
    @param nplurals: The number of plurals in the
    """

    sources = [SourceTextBox('source-%d' % i,
                       partial(get_source, unit, i),
                       partial(set_source, unit, i))
               for i in xrange(num_sources(unit))]

    targets = [TargetTextBox('target-%d' % i,
                       partial(get_target, unit, nplurals, i),
                       partial(set_target, unit, i))
               for i in xrange(num_targets(unit, nplurals))]

    all_text = list(chain(sources, targets))
    for first, second in zip(all_text, all_text[1:]):
        first.next = second

    layout = Layout('layout',
                  VList('main_list', list(chain(
                        [Comment('programmer',
                                 partial(unit.getnotes, 'programmer'))],
                        sources,
                        [Comment('context', unit.getcontext)],
                        targets,
                        [Comment('translator',
                                 partial(unit.getnotes, 'translator'))],
                        get_options(unit)))))

    # This is somewhat ugly. These private variables will be used by get_sources
    # and get_targets (both defined elsewhere in this file).
    layout.__sources = sources
    layout.__targets = targets

    return layout

def get_sources(layout):
    return layout.__sources

def get_targets(layout):
    return layout.__targets

def get_blueprints(unit, nplurals):
    """Return a layout description used to construct UnitEditors

    @param unit: A translation unit (from the translate toolkit)
    """
    if not hasattr(unit, '__blueprints'):
        unit.__blueprints = build_layout(unit, nplurals)
    return unit.__blueprints

