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
    set_up_db_then_import_languages_then_users(parsed_prefs, parsed_oldprefs, parsed_users)

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
    import_projects(alchemysession, oldprefs)
    import_users(alchemysession, parsed_users)

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

def import_projects(alchemysession, parsed_data):
    # This could prompt the user, asking:
    # "Want us to import projects? Say no if you have already added the projects to the new Pootle DB in the web UI."
        
    data = parsed_data.__root__._assignments # Is this really the right way?
    prefix = 'Pootle.projects.'

    # Filter out unrelated keys
    keys = [key for key in data if key.startswith(prefix)]

    # Clean up 'pootle.fullname' into 'pootle'
    projs = set([key[len(prefix):].split('.')[0] for key in keys]) 

    for proj in map(lambda s: unicode(s, 'utf-8'), projs):
        # id, for free
        # code:
        db_proj = Project(proj)

        # fullname
        db_proj.fullname = _get_attribute(data, proj, 'fullname')

        # description
        db_proj.description = _get_attribute(data, proj, 'description')

        # checkstyle
        db_proj.checkstyle = _get_attribute(data, proj, 'checkstyle', unicode_me = False)

        # localfiletype
        db_proj.localfiletype = _get_attribute(data, proj, 'localfiletype')

        # createmofiles?
        db_proj.createmofiles = try_type(bool,
                                    _get_attribute(data, proj, 'createmofiles', unicode_me=False, default=0))

        # treestyle
        db_proj.treestyle = _get_attribute(data, proj, 'treestyle', unicode_me = False)

        # ignoredfiles
        db_proj.ignoredfiles = _get_attribute(data, proj, 'ignoredfiles', default=u'')

        attempt(alchemysession, db_proj)

def _get_user_attribute(data, user_name, attribute, unicode_me = True, default = ''):
    return _get_attribute(data, user_name, attribute, unicode_me, default, prefix='')

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
        raw_projects = _get_user_attribute(data, user_name, 'projects')
        projects_list = raw_projects.split(',')
        # remove the empty string from our list of "projects"
        projects_list = filter(lambda thing: thing, projects_list)
        for project_name in projects_list:
            try:
                db_project = alchemysession.query(Project).filter_by(code=project_name).one()
            except object: # wrong exception name
                print >> sys.stderr, "Failed to add", user, "to project ID", project_name, "; you probably need to create it."
            if db_project not in user.projects:
                user.projects.append(db_project) # Is it really this easy?

        # Fill in the user_languages table
        # (languages in users.prefs)
        raw_languages = _get_user_attribute(data, user_name, 'languages')
        languages_list = raw_languages.split(',')
        # remove the empty string from our list of "languages"
        languages_list = filter(lambda thing: thing, languages_list)
        for language_name in languages_list:
            try:
                db_language = alchemysession.query(Language).filter_by(code=language_name).one()
            except object: # wrong exception name
                print >> sys.stderr, "Failed to add", user, "to language ID", language_name, "; you probably need to create it."
            if db_language not in user.languages:
                user.languages.append(db_language)

        # Commit the user.
        attempt(alchemysession, user)

if __name__ == '__main__':
  main()
