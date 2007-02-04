"""Pootle authentication backend for Django, users are saved in users.prefs 
file, just like with Pootle."""


import md5
import os
from django.conf import settings
from jToolkit import prefs
from Pootle.conf import instance, users


class UsersNotInitialized(Exception): pass

def md5hexdigest(text):
  if isinstance(text, unicode): text = text.encode('utf8')
  return md5.md5(text).hexdigest()

class UserWrapper:
    """A class to wrap user object in just to map different naming 
    between jToolkit and Django"""
    def __init__(self, user, username):
        def get_and_delete_messages():
            return []
        self._user = user
        self._username = username
        self.mapping = {
            'id': username,
            'username': username,
            'get_and_delete_messages': get_and_delete_messages,
            }

    def __repr__(self):
        return "<PootleUser: %s>" % self._username

    def __str__(self):
        return str(self._username)
    
    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
        
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

    def __getattr__(self, key):
        if key in self.mapping:
            return self.mapping[key]
        else:
            try:
                return self.__getattr__(key)
            except:
                return self._user.__getattr__(key)
    
    def set_user(self, kwargs):
        self._user.name = kwargs['name']
        self._user.email = kwargs['email']
        self._user.activated = kwargs['activated']
        if 'activationcode' in kwargs:
            self._user.activationcode = kwargs['activationcode']
        if kwargs.get('password') != None:
            self.set_password(kwargs['password'])
        save_users()
    
    def activate(self):
        self._user.activated = 1
        if hasattr(self._user, 'activationcode'):
            self._user.__delattr__('activationcode')

    def set_password(self, raw_password):
        self._user.passwdhash = md5hexdigest(raw_password)

    def check_password(self, raw_password):
        return self._user.passwdhash == md5hexdigest(raw_password)

    def delete(self):
        if users().__hasattr__(self._username):
            users().removekey(self._username)

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

