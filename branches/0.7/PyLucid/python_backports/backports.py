#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""

Backport for some features

Some things taken from:
http://aima.cs.berkeley.edu/python/utils.html
"""

from __future__ import generators
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


def strip(chars):
    raise

import string
string.strip = strip