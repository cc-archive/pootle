# Useful functions used throughout Pootle

import sre
import os

def shortdescription(descr):
    """Returns a short description by removing markup and only including up
    to the first br-tag"""
    stopsign = descr.find("<br")
    if stopsign >= 0:
        descr = descr[:stopsign]
    return sre.sub("<[^>]*>", "", descr).strip()

def next_to_this_file(this_file, additional_path):
    return os.path.join(os.path.dirname(os.path.abspath(this_file)), additional_path)

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

