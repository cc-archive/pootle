"""Pootle authentication backend for Django, users are saved in users.prefs 
file, just like with Pootle."""


import md5
import os
from django.conf import settings
from Pootle.compat import prefs
from Pootle.conf import instance, users, potree


class UsersNotInitialized(Exception): pass

def md5hexdigest(text):
  if isinstance(text, unicode): text = text.encode('utf8')
  return md5.md5(text).hexdigest()

class UserWrapper(object):
    """A class to wrap user object in just to map different naming 
    between jToolkit and Django"""
    def __init__(self, user, username):
        self._user = user
        self.id = username
        self.username = username

    def __repr__(self):
        return "<PootleUser: %s>" % self.username

    def __str__(self):
        return str(self.username)
   
    # properties
    def __getattr__(self, key):
        if key in ['name', 'email', 'uilanguage', 'inputheight', 'inputwidth', 'viewrows', 'translaterows']:
            return getattr(self._user, key, None)

    def _get_projects(self):
        return getattr(self._user, 'projects', '').split(',')

    def _set_projects(self, project_list):
        setattr(self._user, 'projects', ",".join(list(project_list)))
    projects = property(_get_projects, _set_projects)

    def _get_languages(self):
        return getattr(self._user, 'languages', '').split(',')
    
    def _set_languages(self, language_list):
        setattr(self._user, 'languages', ",".join(list(language_list)))
    languages = property(_get_languages, _set_languages)
    # end properties

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
        
    def get_and_delete_messages(self):
        return []

    def is_superuser(self):
        try:
            return self._user.rights.siteadmin
        except AttributeError:
            return False

    def is_active(self):
        try:
            return self._user.activated
        except AttributeError:
            return False

    def set_user(self, kwargs):
        for i in ['name', 'email', 'uilanguage', 'inputheight', 'inputwidth', 'viewrows', 'translaterows']:
            if i in kwargs:
                setattr(self._user, i, kwargs[i])
        if 'activated' in kwargs:
            self._user.activated = kwargs['activated']
        if 'activationcode' in kwargs:
            self._user.activationcode = kwargs['activationcode']
        if kwargs['password']:
            self.set_password(kwargs['password'])
    
    def activate(self):
        self._user.activated = 1
        if hasattr(self._user, 'activationcode'):
            self._user.__delattr__('activationcode')

    def set_password(self, raw_password):
        self._user.passwdhash = md5hexdigest(raw_password)

    def check_password(self, raw_password):
        return self._user.passwdhash == md5hexdigest(raw_password)

    def save(self):
        save_users()

    def delete(self):
        if users().__hasattr__(self.username):
            users().removekey(self.username)

    def is_project_member(self, project):
        return project in [i.strip() for i in getattr(self._user, 'projects', '').split(',')]

    def project_list(self):
        for p in getattr(self._user, 'projects', '').split(','):
            if p.strip():
                yield potree().get_project(p)

    def is_language_member(self, language):
        return language in [i.strip() for i in getattr(self._user, 'projects', '').split(',')]

    def language_list(self):
        for p in getattr(self._user, 'languages', '').split(','):
            if p.strip():
                yield potree().get_language(p)

class PootleAuth:
    "Authenticate against Pootle's users.prefs file"
    def authenticate(self, username=None, password=None):
        if users().__hasattr__(username):
            user = users().__getattr__(username)
            if md5hexdigest(password) == user.passwdhash:
                return UserWrapper(user, username)
        return None

    def get_user(self, username):
        if users().__hasattr__(username):
            return UserWrapper(users().__getattr__(username), username)
        return None

def get_user(username):
    """
    Returns jToolkit user object if user found, 
    else returns None
    """

    if not users():
        raise UsersNotInitialized
    try:
        return users().__getattr__(username)
    except AttributeError:
        return None

def get_users():
    """
    Returns an iterable over all Pootle users.
    """
    if not users():
        raise UsersNotInitialized
    for u in users().iteritems(sorted=True):
        yield UserWrapper(u[1], u[0])

def create_usernode(username, email):
    """
    Creates a new user out of a username and email
    """
    usernode = prefs.PrefNode(users(), username)
    users().__setattr__(username, usernode)
    usernode.name = ""
    usernode.email = email
    usernode.passwdhash = ""
    save_users()
    return usernode

def create_user(username, email):
    """
    Creates and returns user wrapped in UserWrapper
    """
    user = create_usernode(username,email)
    if user:
        return UserWrapper(user, username)

def save_users():
    prefsfile = users().__root__.__dict__["_setvalue"].im_self
    prefsfile.savefile()

