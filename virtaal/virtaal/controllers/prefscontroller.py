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
from virtaal.views import PreferencesView

from basecontroller import BaseController


class PreferencesController(BaseController):
    """Controller for driving the preferences GUI."""

    __gtype_name__ = 'PreferencesController'

    # INITIALIZERS #
    def __init__(self, main_controller):
        GObjectWrapper.__init__(self)

        self.main_controller = main_controller
        self.placeables_controller = main_controller.placeables_controller
        self.plugin_controller = main_controller.plugin_controller
        self.view = PreferencesView(self)


    # METHODS #
    def set_placeable_enabled(self, parser, enabled):
        """Enable or disable a placeable with the given parser function."""
        getattr(self.placeables_controller, enabled and 'add_parsers' or 'remove_parsers')(parser)
        self.update_config_placeables_state(parser=parser, disabled=not enabled)

    def set_plugin_enabled(self, plugin_name, enabled):
        """Enabled or disable a plug-in with the given name."""
        getattr(self.plugin_controller, enabled and 'enable_plugin' or 'disable_plugin')(plugin_name)
        self.update_config_plugin_state(plugin_name=plugin_name, disabled=not enabled)

    def update_config_placeables_state(self, parser, disabled):
        """Make sure that the placeable with the given name is enabled/disabled
            in the main configuration file."""
        classname = parser.im_self.__name__
        pan_app.settings.placeable_state[classname.lower()] = disabled and 'disabled' or 'enabled'

    def update_config_plugin_state(self, plugin_name, disabled):
        """Make sure that the plug-in with the given name is enabled/disabled
            in the main configuration file."""
        # A plug-in is considered "enabled" as long as pan_app.settings.plugin_state[plugin_name].lower() != 'disabled',
        # even if not pan_app.settings.plugin_state.has_key(plugin_name).
        # This method is put here in stead of in PluginController, because it is not safe to assume that the plug-ins
        # being managed my any given PluginController instance is enabled/disabled via the main virtaal.ini's
        # "[plugin_state]" section.
        pan_app.settings.plugin_state[plugin_name] = disabled and 'disabled' or 'enabled'

    def update_prefs_gui_data(self):
        self._update_placeables_gui_data()
        self._update_plugin_gui_data()

    def _update_placeables_gui_data(self):
        items = []
        allparsers = self.placeables_controller.parser_info.items()
        allparsers.sort(key=lambda x: x[1][0])
        for parser, (name, desc) in allparsers:
            items.append({
                'name': name,
                'desc': desc,
                'enabled': parser in self.placeables_controller.parsers,
                'data': parser
            })
        self.view.placeables_data = items

    def _update_plugin_gui_data(self):
        plugin_items = []
        for found_plugin in self.plugin_controller._find_plugin_names():
            if found_plugin in self.plugin_controller.plugins:
                plugin = self.plugin_controller.plugins[found_plugin]
                plugin_items.append({
                    'name': plugin.display_name,
                    'desc': plugin.description,
                    'enabled': True,
                    'data': {'internal_name': found_plugin},
                    'config': plugin.configure_func
                })
            else:
                info = self.plugin_controller.get_plugin_info(found_plugin)
                plugin_items.append({
                    'name': info['display_name'],
                    'desc': info['description'],
                    'enabled': False,
                    'data': {'internal_name': found_plugin},
                    'config': None
                })
        # XXX: Note that we ignore plugin_controller.get_disabled_plugins(), because we need to know
        #      which plug-ins are currently enabled/disabled (not dependant on config).

        self.view.plugin_data = plugin_items
