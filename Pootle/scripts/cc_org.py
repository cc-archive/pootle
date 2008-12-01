#!/usr/bin/python

# Verbatim script for managing the translate.creativecommons.org project.
# This is a modification to amodemo.py. 
# More information at https://wiki.mozilla.org/Verbatim
#
# Author: Wil Clouser <clouserw@mozilla.com>
# Author: Dan Schafer <dschafer@andrew.cmu.edu>
# Author: Asheesh Laroia <asheesh@creativecommons.org>

import os
## HACK
base_dir=os.path.join(os.getenv('HOME'), 'checkouts', 'cc_org')
cc_checkout = os.path.join(base_dir, 'cc-i18n-trunk')
cc_style = os.path.join(cc_checkout, 'i18n')
po_style = os.path.join(cc_checkout, 'po')

import sys
import os
import os.path
import subprocess
from subprocess import Popen, PIPE
from Pootle.scripts.convert import monopo2po, po2monopo

def initialize(projectdir, languagecode):
    # This does nothing because for now I expect the CC Pootle maintainers to manually symlink in each language directory
    pass

def silent_success_call(argv, cwd = None):
    pipe = Popen(argv, stdout=PIPE, cwd = cwd)
    output = pipe.communicate()
    assert pipe.returncode == 0
    assert not output[0]

def committed2real_and_sub_and_ccstyle(committedfile):
    realpath = os.path.realpath(committedfile)
    assert realpath != committedfile # it better be a symlink to the hidden cc_checkout path
    assert cc_checkout in realpath

    # Grab the relative path from cc_checkout
    subpath = realpath.split(cc_checkout, 1)[1]

    assert 'po' in subpath

    cc_style = subpath.replace('po', 'i18n', 1) # just replace the first 'po'

    return (realpath, subpath, cc_style)

def precommit(committedfile, author, message):
    '''cc_org precommit: Before we commit the PO-style PO file,
    let's merge these changes into the CC-style PO file, and then
    ask Pootle to commit both files.'''
    # Later: Optimize this by pulling the language out of the filename
    
    # run po2cc, and also be sure to commit the cc version
    silent_success_call(['./bin/po2cc'], cwd=cc_checkout) # needs no arguments

    realpath, subpath, cc_style = committed2real_and_sub(committedfile)

    ret = [cc_checkout + subpath, cc_checkout + cc_style]

    # See if suggestion files and other gunk exists
    rest = glob.glob(committedfile.replace('.po', '') + '.pending')
    if rest:
        ret.extend(rest)

    # Look for .prefs and .stats, too
    base = os.path.join(os.path.split(committedfile)[:-1])
    prefs_and_stats = glob.glob(os.path.join(base, 'pootle-cc_org-*'))
    ret.extend(prefs_and_stats)

    return ret

def postcommit(committedfile, success):
    # I can't think of anything we need to do post commit.
    pass

def preupdate(updatedfile): 
    '''cc_org preupdate: When one updates the PO-style po file,
    one should update the CC-style one also.'''

    realpath, subpath, cc_style = committed2real_and_sub(updatedfile)

    return [cc_checkout + subpath, cc_checkout + cc_style]

def postupdate(updatedfile):
    '''cc_org postupdate: After a new version of a file is grabbed from svn,
    ...be smart about mergng with cc2po?'''
    pass
