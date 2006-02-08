# -*- coding: utf-8 -*-
"""
    Colubrid Response Objects
    -------------------------
"""

from __future__ import generators


class HttpResponse(object):
    
    def __init__(self, data):
        self._next = iter([data]).next
        self._length = len(data)
        
    def __iter__(self):
        return self
        
    def next(self):
        return self._next()
        
    def header_modify(self):
        yield 'Content-Length', str(self._length), False
