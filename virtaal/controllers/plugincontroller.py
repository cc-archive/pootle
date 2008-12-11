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

import logging
import os

from virtaal.common import GObjectWrapper

from basecontroller import BaseController
from baseplugin import BasePlugin


class PluginController(BaseController):
    """This controller is responsible for all plug-in management."""

    __gtype_name__ = 'PluginController'

    PLUGIN_DIR = os.path.join('virtaal', 'plugins') # FIXME: This should be replaced with a generic location

    # INITIALIZERS #
    def __init__(self, main_controller):
        GObjectWrapper.__init__(self)

        self.main_controller = main_controller
        self.main_controller.plugin_controller = self


    # METHODS #
    def load_plugins(self):
        """Load plugins from the "plugins" directory."""
        self.plugin        = {}
        self.pluginmodules = {}

        for name in self._find_plugin_names():
            module = __import__(
                'virtaal.plugins.' + name,
                globals=globals(),
                fromlist=['Plugin']
            )
            if not getattr(module, 'Plugin', None):
                raise Exception('Plugin "%s" has no class called "Plugin"' % (name))
            if getattr(module.Plugin, '__bases__', None) is None or BasePlugin not in module.Plugin.__bases__:
                raise Exception('Plugin "%s" contains a member called "Plugin" which is not a valid plug-in class.' % (name))

            self.pluginmodules[name] = module
            try:
                self.plugin[name] = module.Plugin(self.main_controller)
            except Exception, exc:
                logging.warning('Failed to load plugin "%s": %s' % (name, exc))

    def _find_plugin_names(self):
        plugin_names = []

        for name in os.listdir(self.PLUGIN_DIR):
            if name.startswith('.'):
                continue
            fullpath = os.path.join(self.PLUGIN_DIR, name)
            if os.path.isdir(fullpath):
                # XXX: The plug-in system assumes that a plug-in in a directory makes the Plugin class accessible via it's __init__.py
                plugin_names.append(name)
            elif os.path.isfile(fullpath) and not name.startswith('__init__.py'):
                plugname = '.'.join(name.split('.')[:-1]) # Effectively removes extension, preserving other .'s int he name
                plugin_names.append(plugname)

        plugin_names = list(set(plugin_names))
        logging.debug('Found plugins: %s' % (plugin_names))
        return plugin_names
