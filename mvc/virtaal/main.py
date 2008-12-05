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


from virtaal.controllers import MainController, StoreController, UnitController


def Virtaal(object):
    """The main Virtaal program entry point."""

    def __init__(self):
        self.store_controller = StoreController()
        self.unit_controller = UnitController(self.store_controller)
        self.main_controller = MainController(self.store_controller)


    # METHODS #
    def run(self):
        self.main_controller.run()


if __name__ == '__main__':
    virtaal = Virtaal()
    virtaal.run()
