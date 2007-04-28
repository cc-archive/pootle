# Useful functions used throughout Pootle

import sre
import os

class NotImplementedException(Exception):
    pass

def shortdescription(descr):
    """Returns a short description by removing markup and only including up
    to the first br-tag"""
    stopsign = descr.find("<br")
    if stopsign >= 0:
        descr = descr[:stopsign]
    return sre.sub("<[^>]*>", "", descr).strip()

class CallableValidatorWrapper:
    """
    This is needed here to make the validator an object,
    that has an attribute 'always_test' set to true.
    """
    def __init__(self, check):
        self._callable = check
        self.always_test = True

    def __call__(self, field_data, all_data):
        return self._callable(field_data, all_data)


def flatten(l, ltypes=(list, tuple)):
    """Flattens a list, eg.:
    >>> flatten([1,[2,[3],[4,5]]])
    [1, 2, 3, 4, 5]

    It is not recursive and returns a list, not an iterator.
    """
    i = 0
    while i < len(l):
        if not l[i]:
            l.pop(i)
            continue
        while isinstance(l[i], ltypes):
            l[i:i+1] = list(l[i])
        i += 1
    return l
