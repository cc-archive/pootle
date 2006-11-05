"""Pootle authentication backend for Django, users are saved in users.prefs 
file, just like with Pootle."""


import md5
from Pootle.instance import users

def md5hexdigest(text):
  if isinstance(text, unicode): text = text.encode('utf8')
  return md5.md5(text).hexdigest()

class UserWrapper:
    """A class to wrap user object in just to map different naming 
    between jToolkit and Django"""
    def __init__(self, user, username):
        def istrue():
            return True
        self.user = user
        self.mapping = {
            'is_active': user.activated,
            'is_authenticated': istrue,
            'is_anonymous': False,
            'id': username,
            'is_superuser': user.rights.siteadmin
            }
    def __getattr__(self, key):
        if key in self.mapping:
            return self.mapping[key]
        else:
            return self.user.__getattr__(key)

class PootleAuth:
    "Authenticate against Pootle's users.prefs file"
    def authenticate(self, username=None, password=None):
        if users.__hasattr__(username):
            user = users.__getattr__(username)
            if md5hexdigest(password) == user.passwdhash:
                return UserWrapper(user, username)
        return None

    def get_user(self, username):
        if users.__hasattr__(username):
            return UserWrapper(users.__getattr__(username), username)
        return None
