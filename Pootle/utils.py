# Useful functions used throughout Pootle

import sre


def shortdescription(descr):
    """Returns a short description by removing markup and only including up
    to the first br-tag"""
    stopsign = descr.find("<br")
    if stopsign >= 0:
        descr = descr[:stopsign]
    return sre.sub("<[^>]*>", "", descr).strip()


# Useful functions used throughout Pootle

import sre


def shortdescription(descr):
    """Returns a short description by removing markup and only including up
    to the first br-tag"""
    stopsign = descr.find("<br")
    if stopsign >= 0:
        descr = descr[:stopsign]
    return sre.sub("<[^>]*>", "", descr).strip()


