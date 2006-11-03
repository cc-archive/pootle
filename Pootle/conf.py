# This file is meant as a container for global objects that are in use in 
# Pootle, eg. Pootle instance, prefs, potree.
#

_instance = None
_potree = None

def instance():
    return _instance

def potree():
    return _potree

def set_instance(inst, potree):
    global _instance, _potree

    _instance = inst
    _potree = potree

