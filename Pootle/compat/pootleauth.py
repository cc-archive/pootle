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
        def istrue():
            return True
        def get_and_delete_messages():
            return []
        self._user = user
        self._username = username
        self.mapping = {
            'is_active': user.activated,
            'is_authenticated': istrue,
            'is_anonymous': False,
            'id': username,
            'username': username,
            'is_superuser': user.rights.siteadmin,
            'get_and_delete_messages': get_and_delete_messages,
            }

    def __repr__(self):
        return "<PootleUser: %s>" % self._username

    def __str__(self):
        return str(self._username)

    def __getattr__(self, key):
        if key in self.mapping:
            return self.mapping[key]
        else:
            try:
                return self.__getattr__(key)
            except:
                return self._user.__getattr__(key)

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


def check_password(usernode, password):
    return usernode.passwdhash == md5hexdigest(password)

def set_password(usernode, password):
    usernode.passwdhash = md5hexdigest(password)

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

def create_user(username, email):
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

def save_users():
    prefsfile = users().__root__.__dict__["_setvalue"].im_self
    prefsfile.savefile()

