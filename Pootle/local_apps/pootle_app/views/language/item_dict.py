#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Zuza Software Foundation
#
# This file is part of Pootle.
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

"""Helper functions for the rendering of several items on the index views and
similar pages."""

import itertools

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

from translate.storage import versioncontrol
from pootle_app.models.profile         import get_profile
from pootle_app.views.language         import search_forms
from pootle_app.models.store_iteration import get_next_match
from pootle_app.models.permissions     import check_permission
from pootle_store.models               import Store
from pootle_app.views.language         import dispatch

################################################################################

def get_item_summary(request, quick_stats, path_obj):
    translated_words = quick_stats['translatedsourcewords']
    total_words      = quick_stats['totalsourcewords']
    num_stores       = Store.objects.filter(pootle_path__startswith=path_obj.pootle_path).count()
    state            = dispatch.CommonState(request.GET)
    file_stats = ungettext("%d file", "%d files", num_stores, num_stores)
    # The translated word counts
    word_stats = _("%(translated)d/%(total)d words (%(translatedpercent)d%%) translated",
                   {"translated": translated_words,
                    "total": total_words,
                    "translatedpercent": quick_stats['translatedpercentage']}
                   )
    # The translated unit counts
    string_stats_text = _("%(translated)d/%(total)d strings",
                          {"translated": quick_stats['translated'],
                           "total": quick_stats['total']}
                          )
    string_stats = '<span class="string-statistics">[%s]</span>' % string_stats_text
    # The whole string of stats
    return '%s %s %s' % (file_stats, word_stats, string_stats)

def get_item_stats(request, quick_stats, path_obj):
    result = {
        'summary': get_item_summary(request, quick_stats, path_obj),
        'checks':  [],
        }
    if request.GET.get('show_checks', None):
        result['checks'] = getcheckdetails(request, path_obj)       #None  # TBD
    return result

def getcheckdetails(request, path_obj, url_opts={}):
    """return a list of strings describing the results of
    checks"""

    property_stats = path_obj.getcompletestats(request.translation_project.checker)
    total = property_stats['total']
    checklinks = []
    keys = property_stats.keys()
    keys.sort()
    for checkname in keys:
        if not checkname.startswith('check-'):
            continue
        checkcount = property_stats[checkname]
        if total and checkcount:
            stats = ungettext('%(checks)d string (%(checkspercent)d%%) failed',
                              '%(checks)d strings (%(checkspercent)d%%) failed', checkcount,
                              {"checks": checkcount, "checkspercent": (checkcount * 100) / total}
                      )
            #url_opts[str(checkname)] = 1
            checklink = {'href': dispatch.translate(request, path_obj.pootle_path, match_names=[checkname]),
                         'text': checkname.replace('check-', '', 1),
                         'stats': stats}
            #del url_opts[str(checkname)]
            checklinks += [checklink]
    return checklinks

################################################################################

def yield_review_link(request, path_obj, links_required, stats_totals):
    if 'review' in links_required and stats_totals.get('check-hassuggestion', 0):
        if check_permission('translate', request):
            text = _('Review Suggestions')
        else:
            text = _('View Suggestions')
        yield { 
            'href': dispatch.translate(request, path_obj.pootle_path, match_names=['check-hassuggestion']),
            'text': text }

def yield_quick_link(request, path_obj, links_required, stats_totals):
    if check_permission('translate', request):
        text = _('Quick Translate')
    else:
        text = _('View Untranslated')
    if stats_totals['translated'] < stats_totals['total']:
        yield {
            'href': dispatch.translate(request, path_obj.pootle_path, match_names=['fuzzy', 'untranslated']),
            'text': text }

def yield_translate_all_link(request, path_obj, links_required):
    yield {
        'href': dispatch.translate(request, path_obj.pootle_path),
        'text': _('Translate All') }

def yield_zip_link(request, path_obj, links_required):
    if 'zip' in links_required and check_permission('archive', request):
        text = _('ZIP of directory')
        link = dispatch.download_zip(request, path_obj)
        yield {
            'href':  link,
            'text':  text,
            'title': link
            }

def yield_export_links(request, path_obj, links_required):
    for type, format, text in [('po',    'po',  _('Download PO')),
                               ('xliff', 'xlf', _('Download XLIFF'))]:
        if type in links_required:
            href = dispatch.export(request, path_obj.pootle_path, format)
            yield {
                'href':  href,
                'text':  text,
                'title': href
                }

def yield_sdf_link(request, path_obj, links_required):
    if 'sdf' in links_required and \
            check_permission('pocompile', request) and \
            request.translation_project.ootemplate() and \
            path_obj == request.translation_project.directory:
        link = dispatch.download_sdf(request, path_obj)
        yield {
            'href':  link,
            'text':  _('Generate SDF'),
            'title': link
            }

def yield_commit_link(request, path_obj, links_required):
    if 'commit' in links_required and check_permission('commit', request) and \
           versioncontrol.hasversioning(path_obj.abs_real_path):
        link = dispatch.commit(request, path_obj)
        text = _('Commit to VCS')
        yield {
            'href': link,
            'text': text,
            'link': link,
        }

def yield_update_link(request, path_obj, links_required):
    if 'commit' in links_required and check_permission('commit', request):
        link = dispatch.update(request, path_obj)
        text = _('Update from VCS')
        yield {
            'href': link,
            'text': text,
            'link': link,
        }

def get_store_extended_links(request, path_obj, links_required):
    stats_totals = path_obj.getcompletestats(request.translation_project.checker)
    return list(itertools.chain(
            yield_review_link(       request, path_obj, links_required, stats_totals),
            yield_quick_link(        request, path_obj, links_required, stats_totals),
            yield_translate_all_link(request, path_obj, links_required),
            yield_export_links(      request, path_obj, links_required),
            yield_zip_link(          request, path_obj, links_required),
            yield_sdf_link(          request, path_obj, links_required),
            yield_commit_link(request, path_obj, links_required),
            yield_update_link(request, path_obj, links_required),
            ))


def get_default_links_required(links_required):
    if links_required is None:
        return ["mine", "review", "quick", "all"]
    else:
        return links_required

def get_action_links(request, path_obj, links_required):
    return {
        'basic': [],
        'extended': get_store_extended_links(request, path_obj, get_default_links_required(links_required)),
        }

################################################################################

def add_percentages(quick_stats):
    quick_stats['translatedpercentage']   = int(100.0 * quick_stats['translatedsourcewords']   / max(quick_stats['totalsourcewords'], 1))
    quick_stats['fuzzypercentage'] = int(100.0 * quick_stats['fuzzysourcewords'] / max(quick_stats['totalsourcewords'], 1))
    quick_stats['untranslatedpercentage'] = 100 - quick_stats['translatedpercentage'] - quick_stats['fuzzypercentage']
    return quick_stats

def make_generic_item(request, path_obj, action, links_required):
    quick_stats = add_percentages(path_obj.getquickstats())
    return {
        'href':    action,
        'data':    quick_stats,
        'title':   path_obj.name,
        'stats':   get_item_stats(request, quick_stats, path_obj),
        'actions': get_action_links(request, path_obj, links_required) }

def make_directory_item(request, directory, links_required=None):
    action = dispatch.show_directory(request, directory.pootle_path)
    item = make_generic_item(request, directory, action, links_required)
    item.update({
            'icon':   'folder',
            'isdir':  True })
    return item

def default_store_links_required(store, links_required):
    if links_required is None:
        if store.name.endswith('.po'):
            return ["mine", "review", "quick", "all", "po", "xliff",
                    "ts", "csv", "mo", "update", "commit"]
        else:
            return ["mine", "review", "quick", "all", "po", "xliff",
                    "update", "commit"]
    else:
        return links_required

def make_store_item(request, store, links_required=None):
    action = dispatch.translate(request, store.pootle_path)
    item = make_generic_item(request, store, action,
                             default_store_links_required(store, links_required))
    item.update({
            'icon':   'file',
            'isfile': True })
    return item
