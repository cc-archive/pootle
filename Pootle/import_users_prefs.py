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

def set_up_db_then_import_users(instance, parsed_users):
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

    import_users(alchemysession, parsed_users)

def _get_user_attribute(data, user_name, attribute, unicode_me = True, default = ''):
    raw_value = data.get(user_name + '.' + attribute, default)
    if unicode_me:
        assert type(raw_value) in types.StringTypes
        value = unicode(raw_value)
    else:
        value = raw_value
    return value

def try_type(try_me, value):
    '''This gentle type-converter should work fine for int and bool.    It would not work for unicode, though.'''
    if try_me == bool:
        assert type(value) == int
        return bool(value)
    if try_me == int:
        if type(value) == int:
                return value
        if value.isnumeric():
                return int(value)
    assert type(value) == try_me
    return value
        
def import_users(alchemysession, parsed_users):
    data = parsed_users.__root__._assignments # Is this really the
                                              # right way?

    # Groan - figure out the usernames
    user_names = set([key.split('.')[0] for key in data])
    
    for user_name in user_names:
        if type(user_name) == unicode:
            pass
        else:
            user_name = unicode(user_name, 'utf-8')
        # id for free, obviously.

        # username
        user = User(user_name)

        # name
        user.name = _get_user_attribute(data, user_name, 'name')

        # email
        user.email =    _get_user_attribute(data, user_name, 'email')

        # activated
        user.activated = try_type(bool,
                                  _get_user_attribute(data, user_name, 'activated', unicode_me=False, default=0))

        # activationcode
        user.activationcode = _get_user_attribute(data, user_name, 'activationcode', unicode_me = False, default=0)

        # passwdhash
        user.passwdhash = _get_user_attribute(data, user_name, 'passwdhash', unicode_me = False)

        # logintype
        # "hash" is the login type that indicates "hash" the user's submitted password into MD5 and check against
        # a local file/DB.
        user.logintype = _get_user_attribute(data, user_name, 'logintype', unicode_me = False, default = 'hash')

        # siteadmin
        user.siteadmin = try_type(bool,
                                                _get_user_attribute(data, user_name, 'siteadmin', unicode_me=False, default=0))

        # viewrows
        user.viewrows = try_type(int,
                                                _get_user_attribute(data, user_name, 'viewrows', unicode_me=False, default=10))

        # translaterows
        user.translaterows = try_type(int,
                                      _get_user_attribute(data, user_name, 'translaterows', unicode_me=False, default=10))

        # uilanguage
        raw_uilanguage = _get_user_attribute(data, user_name, 'uilanguages')
        assert ',' not in raw_uilanguage # just one value here
        if raw_uilanguage:
            db_uilanguage = alchemysession.query(Language).filter_by(code=raw_uilanguage).one()
            user.uilanguage = db_uilanguage
        else:
            pass # leave it NULL

        # altsrclanguage
        raw_altsrclanguage = _get_user_attribute(data, user_name, 'altsrclanguage')
        assert ',' not in raw_altsrclanguage # just one value here
        if raw_altsrclanguage:
            db_altsrclanguage = alchemysession.query(Language).filter_by(code=raw_altsrclanguage).one()
            user.altsrclanguage = db_altsrclanguage
        else:
            pass # leave it NULL

        # ASSUMPTION: Someone has already created all the necessary projects
        #             and languages in the web UI or through some other importer

        # Fill in the user_projects table
        # (projects in the users.prefs file)
        raw_projects = try_type(unicode, _get_user_attribute(data, user_name, 'projects'))
        projects_list = raw_projects.split(',')
        for project_name in projects_list:
            try:
                db_project = alchemysession.query(Project).filter_by(code=project_name).one()
            except object: # wrong exception name
                print >> sys.stderr, "Failed to add", user, "to project ID", project_name, "; you probably need to create it."
            if db_project not in user.projects:
                user.projects.append(db_project) # Is it really this easy?

        # Fill in the user_languages table
        # (languages in users.prefs)
        raw_languages = try_type(unicode, _get_user_attribute(data, user_name, 'languages'))
        languages_list = raw_languages.split(',')
        for language_name in languages_list:
            try:
                db_language = alchemysession.query(Language).filter_by(code=language_name).one()
            except object: # wrong exception name
                print >> sys.stderr, "Failed to add", user, "to language ID", language_name, "; you probably need to create it."
            if language_name not in user.languages:
                user.languages.append(language_name)

        # Commit the user.
        attempt(alchemysession, user)
        
if __name__ == '__main__':
    main()
