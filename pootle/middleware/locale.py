#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2009 Zuza Software Foundation
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

from django.utils import translation
from django.utils.translation import trans_real
from django.conf import settings

from pootle.i18n import gettext
from pootle.i18n import gettext_live

def translation_dummy(language):
    """return dumy translation object to please django's l10n while
    Live Translation is enabled"""
    
    t = trans_real._translations.get(language, None)
    if t is not None:
        return t

    dummytrans = trans_real.DjangoTranslation()
    dummytrans.set_language(language)
    #FIXME: the need for the _catalog attribute means we
    # are not hijacking gettext early enough
    dummytrans._catalog = {}
    dummytrans.plural = lambda x: x
    trans_real._translations[language] = dummytrans
    return dummytrans
            
            
class LocaleMiddleware(object):
    """
    Hijack Django's localization functions to support arbitrary user
    defined languages and live translation.
    """

    def __init__(self):
        """sabotage django's fascist linguistical regime"""
        # override functions that check if language if language is
        # known to Django
        translation.check_for_language = lambda lang_code: True
        trans_real.check_for_language = lambda lang_code: True

        # override django's inadequate bidi detection
        translation.get_language_bidi = gettext.get_language_bidi

        if settings.LIVE_TRANSLATION:
            # hijack language activation code to avoid unnessecary
            # loading of mo files
            trans_real.translation = translation_dummy
            gettext.override_gettext(gettext_live)
        else:
            # even when live translation is not enabled we hijack
            # gettext functions to install the safe variable
            # formatting override
            gettext.override_gettext(translation)
            

    def process_request(self, request):
        """
        Load user specified locale from profile and inject it in
        session for django's locale middle ware to find.
        """
        if request.user.is_authenticated() and 'django_language' not in request.session:
            language = request.user.get_profile().ui_lang
            if language is not None:
                request.session['django_language'] = language.code
            else:
                request.session['django_language'] = None