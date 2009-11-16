#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
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

import os

from django.conf import settings

def add_trailing_slash(path):
    """If path does not end with /, add it and return."""

    if path[-1] == os.sep:
        return path
    else:
        return path + os.sep


def relative_real_path(p):
    if p.startswith(settings.PODIRECTORY):
        return p[len(add_trailing_slash(settings.PODIRECTORY)):]
    else:
        return p


def absolute_real_path(p):
    if not p.startswith(settings.PODIRECTORY):
        return os.path.join(settings.PODIRECTORY, p)
    else:
        return p

def dictsum(x, y):
    return dict( (n, x.get(n, 0)+y.get(n, 0)) for n in set(x)|set(y) )

def statssum(queryset, empty_stats=None):
    if empty_stats is None:
        empty_stats = {'fuzzy': 0,
                       'fuzzysourcewords': 0,
                       'review': 0,
                       'total': 0,
                       'totalsourcewords': 0,
                       'translated': 0,
                       'translatedsourcewords': 0,
                       'translatedtargetwords': 0,
                       'untranslated': 0,
                       'untranslatedsourcewords': 0,
                       'errors': 0}
    totals = empty_stats
    for item in queryset:
        try:
            totals = dictsum(totals, item.getquickstats())
        except:
            totals['errors'] += 1
    return totals

def completestatssum(queryset, checker, empty_stats=None):
    if empty_stats is None:
        empty_stats = {u'check-hassuggestion': 0,
                       u'check-isfuzzy': 0,
                       'fuzzy': 0,
                       'total': 0,
                       'translated': 0,
                       'untranslated': 0,
                       'errors': 0}
    for item in queryset:
        try:
            totals = dictsum(totals, item.getcompletestats(checker))
        except:
            totals['errors'] += 1
    return totals
