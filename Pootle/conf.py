"""
This file is meant as a container for global objects that are in use in 
Pootle, eg. Pootle instance, prefs, potree. While instance provides a way
to instantate them, conf.py provides a way to serve these global variables 
to other files.

This file is here because of necessity to be able to import first and set 
variable later.

"""


_instance = None
_potree = None
_users = None

def users():
    return _users

def instance():
    return _instance

def potree():
    return _potree

def saveprefs():
    prefsfile = instance().__root__.__dict__["_setvalue"].im_self
    prefsfile.savefile()

def set_instance(inst, potree, users):
    global _instance, _potree, _users
    _instance = inst
    _potree = potree
    _users = users

