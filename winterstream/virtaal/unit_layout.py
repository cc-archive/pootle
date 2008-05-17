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

import pango
import gtk

from support.partial import partial
from pan_app import _
import markup
from widgets import style

class Widget(object):
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self._height = 0

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

class Layout(Widget):
    def __init__(self, name, child):
        super(Layout, self).__init__(name)
        self.child = child
        self.children.append(self.child)
        self.child.parent = self
        
    def height(self, widget, width):
        return self.cache_height(self.child.height(widget, width / 2))

class List(Widget):
    def __init__(self, name, children=None):
        super(List, self).__init__(name)

        if children != None:
            self.children = children

        for child in self.children:
            child.parent = self

    def add(self, widget):
        self.children.append(widget)

class VList(List):
    def height(self, widget, width):
        h = sum(child.height(widget, width) for child in self.children) + \
            self.v_padding() * (len(self.children) - 1)
        return self.cache_height(h)

    def v_padding(self):
        return 0

    def h_padding(self):
        return 0

class HList(List):
    def height(self, widget, width):
        item_width = (width - len(self.children) * (self.h_padding() + 1)) / len(self.children)
        h = 2*self.v_padding() + max(child.height(widget, item_width) for child in self.children)
        return self.cache_height(h)

    def v_padding(self):
        return 0

    def h_padding(self):
        return 0

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

class SourceTextBox(TextBox):
    def __init__(self, name, get_text, set_text):
        super(SourceTextBox, self).__init__(name, get_text, set_text, False)

class TargetTextBox(TextBox):
    def __init__(self, name, get_text, set_text):
        super(TargetTextBox, self).__init__(name, get_text, set_text, True)

class Comment(TextBox):
    def __init__(self, name, get_text, set_text=lambda value: None):
        super(Comment, self).__init__(name, get_text, set_text, False)

    def v_padding(self):
        return 2

    def height(self, widget, width):
        # TODO: The calculations here yield incorrect results. We'll have to look at this.
        text = self.get_text()
        if text == "":     # If we have an empty string, we squash the self box
            return self.cache_height(0)
        _w, h = self.make_pango_layout(text[0], widget, width).get_pixel_size()
        return self.cache_height(h + self.v_padding())

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

