#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Pootle.
#
# Pootle is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pootle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pootle; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""This module defines methods which are useful for bridging the differences
between jToolkit and Django. This makes interfacing with existing code easier."""

def process_django_request_args(request):
    """Django's GET/POST dictionaries return lists for all values. jToolkit doesn't do this, so
    to bridge the gap, we look for single items appearing in lists. We build a new dictionary
    where these items appear directly (not in lists)."""
    request_dict = dict(request.GET.iteritems())
    request_dict.update(request.POST.iteritems())
    return request_dict
