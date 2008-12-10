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
from bisect import bisect_left

from virtaal.common import GObjectWrapper


class Cursor(GObjectWrapper):
    """
    Manages the current position in an arbitrary model.

    NOTE: Assigning to C{self.pos} causes the "cursor-changed" signal
    to be emitted.
    """

    __gtype_name__ = "Cursor"

    __gsignals__ = {
        "cursor-changed": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
    }


    # INITIALIZERS #
    def __init__(self, model, indices, circular=True):
        GObjectWrapper.__init__(self)

        self.model = model
        self._indices = indices
        self.circular = circular

        self._pos = 0


    # ACCESSORS #
    def _get_pos(self):
        return self._pos
    def _set_pos(self, value):
        if value == self._pos:
            return # Don't unnecessarily move the cursor (or emit 'cursor-changed', more specifically)
        if value >= len(self.indices):
            self._pos = len(self.indices) - 1
        else:
            self._pos = value
        self.emit('cursor-changed')
    pos = property(_get_pos, _set_pos)

    def _get_index(self):
        if len(self._indices) < 1:
            return -1
        return self._indices[self.pos]
    def _set_index(self, index):
        """Move the cursor to the cursor to the position specified by C{index}.
            @type  index: int
            @param index: The index that the cursor should point to."""
        self.pos = bisect_left(self._indices, index)
    index = property(_get_index, _set_index)

    def _get_indices(self):
        return self._indices
    def _set_indices(self, value):
        oldindex = self.index
        #print '%s -> %s' % (self._indices, list(value))
        self._indices = list(value)
        self.index = oldindex
    indices = property(_get_indices, _set_indices)

    # METHODS #
    def move(self, offset):
        """Move the cursor C{offset} positions down.
            The cursor will wrap around to the beginning if C{circular=True}
            was given when the cursor was created."""
        # FIXME: Possibly contains off-by-one bug(s)
        if 0 <= self.pos + offset < len(self._indices):
            self.pos += offset
        elif self.circular:
            if self.pos + offset >= 0:
                self.pos = self.pos + offset - len(self._indices)
            elif self.pos + offset < 0:
                self.pos = self.pos + offset + len(self._indices)
        else:
            raise IndexError()
        return self.pos
