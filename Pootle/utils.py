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
