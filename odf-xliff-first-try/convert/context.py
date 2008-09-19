#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2006 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import sys

def with_(context, body):
    """A function to mimic the with statement introduced in Python 2.5"""
    try:
      retval = body(context.__enter__())
      context.__exit__(None, None, None)
      return retval
    except:
      if not context.__exit__(*sys.exc_info()):
        raise

class SimpleContext(object):
    def __init__(self, enter, exit):
        self.enter = enter
        self.exit = exit
        
    def __enter__(self):
        return self.enter()
      
    def __exit__(self, last_type, last_value, last_traceback):
        self.exit()
        return True

def with_context(enter, exit, body):
    return with_(SimpleContext(enter, exit), body)
