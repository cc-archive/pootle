# Author: Asheesh Laroia <asheesh@creativecommons.org>
# Copyright: (C) 2008 Creative Commons
# Permission is granted to redistribute this file under the GPLv2 or later, at your option.   See COPYING for details.

# coding: utf-8
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from dbclasses import *
import sys
from jToolkit import prefs
import md5
import types

from initdb import attempt

def main():
    if len(sys.argv) != 4:
        print "Usage: %s pootle.prefs old_pootle.prefs users.prefs" % sys.argv[0]
        return

    prefsfile = sys.argv[1]
    parsed_prefs = prefs.PrefsParser(prefsfile).Pootle
    oldprefsfile = sys.argv[2]
    parsed_oldprefs = prefs.PrefsParser(oldprefsfile)
    usersfile = sys.argv[3]
    parsed_users = prefs.PrefsParser(usersfile)
    set_up_db_then_import_languages(parsed_prefs, parsed_oldprefs)

def set_up_db_then_import_languages_then_users(instance, oldprefs, parsed_users):
    # Set up the connection options
    STATS_OPTIONS = {}
    for k,v in instance.stats.connect.iteritems():
        STATS_OPTIONS[k] = v

    #metadata = Base.metadata
    engine = create_engine('sqlite:///%s' % STATS_OPTIONS['database'])
    conn = engine.connect()

    Session = sessionmaker(bind=engine, autoflush=True)
    alchemysession = Session()

    metadata.create_all(engine)

    import_languages(alchemysession, oldprefs)
    import import_users_prefs
    import_users_prefs.import_users(alchemysession, parsed_users)

def _get_attribute(data, name, attribute, unicode_me = True, default = '', prefix='Pootle.languages.'):
    raw_value = data.get(prefix + name + '.' + attribute, default)
    if unicode_me:
        assert type(raw_value) in types.StringTypes
        if type(raw_value) == unicode:
            value = raw_value
        else:
            value = unicode(raw_value, 'utf-8')
    else:
        if raw_value == '':
            value = default
        else:
            value = raw_value
    return value

def try_type(try_me, value):
    '''This gentle type-converter should work fine for int and bool.    It would not work for unicode, though.'''
    assert try_me is not unicode
    if try_me == bool:
        assert type(value) == int
        return bool(value)
    if try_me == int:
        if type(value) == int:
                return value
        if value.isdigit():
                return int(value)
    assert type(value) == try_me
    return value

def import_languages(alchemysession, parsed_data):
    data = parsed_data.__root__._assignments # Is this really the right way?
    prefix = 'Pootle.languages.'

    # Filter out unrelated keys
    keys = [key for key in data if key.startswith(prefix)]

    # Clean up 'sv_SE.pluralequation' into 'sv_SE'
    langs = set([key[len(prefix):].split('.')[0] for key in keys]) 

    for lang in map(lambda s: unicode(s, 'utf-8'), langs):
        # id, for free
        # code:
        db_lang = Language(lang)

        # fullname
        db_lang.fullname = _get_attribute(data, lang, 'fullname')

        # nplurals
        db_lang.nplurals = try_type(int,
                                    _get_attribute(data, lang, 'nplurals', unicode_me = False, default=1))

        # pluralequation
        db_lang.pluralequation = _get_attribute(data, lang, 'pluralequation', unicode_me = False)

        # specialchars
        db_lang.specialchars = _get_attribute(data, lang, 'specialchars')

        attempt(alchemysession, db_lang)

if __name__ == '__main__':
  main()
