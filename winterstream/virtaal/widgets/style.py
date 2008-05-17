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

import gtk

def properties_generator(widget, *prop_list):
    for prop in prop_list:
        try:
            yield (prop, widget.get_property(prop))
        except TypeError:
            try:
                yield (prop, widget.style_get_property(prop))
            except TypeError:
                yield (prop, getattr(widget, prop))

def properties(*spec):
    return dict(properties_generator(*spec))

def make_style():
    return {
        gtk.TextView:       properties(gtk.TextView(),       'left-margin', 'right-margin'),
        gtk.ScrolledWindow: properties(gtk.ScrolledWindow(), 'scrollbar-spacing'),
        gtk.Container:      properties(gtk.TextView(),       'border-width'),
        gtk.CheckButton:    properties(gtk.CheckButton(),    'indicator-size', 'indicator-spacing'),
        gtk.Widget:         properties(gtk.Button(),         'focus-line-width', 'focus-padding')
    }

style = make_style()
