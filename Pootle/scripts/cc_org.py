#!/usr/bin/python
'''Verbatim script for managing the translate.creativecommons.org project.
This is a modification to amodemo.py. 
More information at https://wiki.mozilla.org/Verbatim'''

# Author: Wil Clouser <clouserw@mozilla.com>
# Author: Dan Schafer <dschafer@andrew.cmu.edu>
# Author: Asheesh Laroia <asheesh@creativecommons.org>

import os
## HACK
BASE_DIR = os.path.join(os.getenv('HOME'), 'checkouts', 'cc_org')
CC_CHECKOUT = os.path.join(BASE_DIR, 'cc-i18n-trunk')

import glob
from subprocess import Popen, PIPE

def initialize(projectdir, languagecode):
    '''This does nothing because for now I expect the CC Pootle maintainers to manually symlink in each language directory'''
    pass

def silent_success_call(argv, cwd = None):
    '''Give me an argv list, and I will pass it Popen, assert that it
    exit(0)'d, and assert it had no output.'''
    pipe = Popen(argv, stdout=PIPE, cwd = cwd)
    output = pipe.communicate()
    assert pipe.returncode == 0
    assert not output[0]

def committed2real_sub_cc(committedfile):
    '''Given a filesystem path to a cc_org PO file, verify that it
    really is a symlink to a file in CC_CHECKOUT, and then provide the
    alternate path to it and to its CC-style counterpart.'''
    realpath = os.path.realpath(committedfile)
    assert realpath != committedfile # it better be a symlink to the hidden cc_checkout path
    assert CC_CHECKOUT in realpath

    # Grab the relative path from CC_CHECKOUT
    subpath = realpath.split(CC_CHECKOUT, 1)[1]

    assert 'po' in subpath

    cc_style = subpath.replace('po', 'i18n', 1) # just replace the first 'po'

    return (realpath, subpath, cc_style)

def precommit(committedfile, author, message):
    '''cc_org precommit: Before we commit the PO-style PO file,
    let's merge these changes into the CC-style PO file, and then
    ask Pootle to commit both files.'''
    # Later: Optimize this by pulling the language out of the filename
    
    # run po2cc, and also be sure to commit the cc version
    silent_success_call(['./bin/po2cc'], cwd=CC_CHECKOUT) # needs no arguments

    realpath, subpath, cc_style = committed2real_sub_cc(committedfile)

    ret = [CC_CHECKOUT + subpath, CC_CHECKOUT + cc_style]

    # See if suggestion files and other gunk exists
    rest = glob.glob(committedfile.replace('.po', '') + '.pending')
    if rest:
        ret.extend(rest)

    # Look for .prefs and .stats, too
    ret.extend(committed2prefs_and_stats(committedfile))

    return ret

def committed2prefs_and_stats(committedfile):
    '''Input: a full path name
    Output: The matching *.prefs and *.stats'''
    realpath = os.path.realpath(committedfile)
    dir, base = os.path.split(realpath)
    
    globme = os.path.join(dir, 'pootle-cc_org-*')
    prefs_and_stats = glob.glob(globme)
    return prefs_and_stats

def postcommit(committedfile, success):
    '''I can't think of anything we need to do post commit.'''
    pass

def preupdate(updatedfile): 
    '''cc_org preupdate: When one updates the PO-style po file,
    one should update the CC-style one also.'''

    realpath, subpath, cc_style = committed2real_sub_cc(updatedfile)

    return [CC_CHECKOUT + subpath, CC_CHECKOUT + cc_style]

def postupdate(updatedfile):
    '''cc_org postupdate: After a new version of a file is grabbed from svn,
    ...be smart about mergng with cc2po?'''
    pass
