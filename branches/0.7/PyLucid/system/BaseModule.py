#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Basis Modul von den andere Module erben können
"""

__version__="0.1"

__history__="""
v0.1
    - erste Version
"""

__todo__="""
"""


from PyLucid.system.exceptions import *


class PyLucidBaseModule:

    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        # shorthands
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences
        self.URLs           = request.URLs
        self.page_msg       = request.page_msg
        self.log            = request.log
        self.module_manager = request.module_manager
