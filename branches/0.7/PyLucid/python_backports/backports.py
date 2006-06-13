#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""

Backport for some features

Some things taken from:
http://aima.cs.berkeley.edu/python/utils.html
"""

from __future__ import generators


import sys

# Damit subprocess.py usw. gefunden werden:
sys.path.insert(0,"PyLucid/python_backports")



import __builtin__



try: basestring  ## Introduced in 2.3
except NameError:
    import types
    basestring = (types.StringType, types.UnicodeType)

    __builtin__.basestring = basestring


try: enumerate  ## Introduced in 2.3
except NameError:
    def enumerate(collection):
        """Return an iterator that enumerates pairs of (i, c[i]). PEP 279.
        >>> list(enumerate('abc'))
        [(0, 'a'), (1, 'b'), (2, 'c')]
        """
        ## Copied from PEP 279
        i = 0
        it = iter(collection)
        while 1:
            yield (i, it.next())
            i += 1

    __builtin__.enumerate = enumerate


#~ def strip(chars):
    #~ raise

#~ import string
#~ string.strip = strip

"""
time.strptime()

http://mail.zope.org/pipermail/zope3-dev/2003-January/004824.html

The problem is that strptime isn't an ANSI C function, so its availability
is platform-dependent. Python 2.3 adds a Python implementation of strptime
so that the function is available everywhere, but before 2.3 (incluing
2.2.2) strptime is only available under most (not all) flavors of Unix.

http://www.python.org/doc/2.2/lib/module-time.html#l2h-1379
    Availability: Most modern Unix systems.

Nutzt _strptime.py aus Python 2.3:
http://svn.python.org/view/python/branches/release23-maint/Lib/_strptime.py
die Version ist kompatibel mit Python 2.2!
"""
import time
if not hasattr(time, "strptime"):
    from _strptime import strptime
    time.strptime = strptime