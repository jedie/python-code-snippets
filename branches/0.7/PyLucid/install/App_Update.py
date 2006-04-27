#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

from PyLucid.install.ObjectApp_Base import ObjectApp_Base

class update(ObjectApp_Base):
    "3. update"
    def update_db(self):
        "update DB tables (PyLucid v0.x -> 0.6)"
        self._write_info()

    def convert_markups(self):
        "Convert Markup Names to IDs (PyLucid v0.x -> 0.5)"
        self._write_info()