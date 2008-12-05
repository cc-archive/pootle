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

from basemodel import BaseModel


class UndoModel(BaseModel):
    """Simple model representing an undo history."""

    # INITIALIZERS #
    def __init__(self, controller):
        self.controller = controller

        super(UndoModel, self).__init__()
        self.undo_stack = []
        self.index = 0


    # METHODS #
    def head(self):
        """Get the undo info currently pointed to by C{self.index}."""
        return self.undo_stack[self.index]

    def move(self, offset=1):
        """Move the cursor (C{self.index}) by C{offset}."""
        newindex = self.index + offset
        if not (0 < newindex < len(self.undo_stack)):
            raise IndexError

        self.index = newindex
        return self.undo_stack[self.index]

    def pop(self):
        if self.undo_stack and self.index > len(self.undo_stack):
            self.index -= 1
            return self.undo_stack[self.index+1]

    def push(self, undo_dict):
        """Push an undo-action onto the undo stack.
            @type  undo_dict: dict
            @param undo_dict: A dictionary containing undo information with the
                following keys:
                - "unit": Value is the unit on which the undo-action is applicable.
                - "action": Value is a callable that is called (with the "unit"
                  value, to effect the undo."""
        if not ('unit' in undo_dict and 'action' in undo_dict):
            raise ValueError('Invalid undo dictionary!')

        self.undo_stack = self.undo_stack[:self.index]
        self.undo_stack.append(undo_dict)
        self.index = len(self.undo_stack) - 1
