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

from translate.storage import factory

import gtk

rf = gtk.RecentFilter()
for name, extensions, mimetypes in factory.supported_files():
    if extensions:
        for extension in extensions:
            rf.add_pattern("*.%s" % extension)
            for compress_extension in factory.decompressclass.keys():
                rf.add_pattern("*.%s.%s" % (extension, compress_extension))
    if mimetypes:
        for mimetype in mimetypes:
            rf.add_mime_type(mimetype)
    rf.add_application("VirTaal")
    rf.add_application("poedit")
    rf.add_application("kbabel")
    rf.add_application("gtranslator")

rc = gtk.RecentChooserMenu()
rc.set_show_not_found(False)
rc.set_show_numbers(True)
rc.add_filter(rf)
rc.set_limit(-1)
