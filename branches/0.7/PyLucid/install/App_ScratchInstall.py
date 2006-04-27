#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Information und Tests
"""

from PyLucid.install.ObjectApp_Base import ObjectApp_Base

class install(ObjectApp_Base):
    "1. install PyLucid from scratch"
    def init_DB(self):
        "1. init Database tables"
        self._write_info()

    def init_modules(self):
        "2. init basic Modules"
        self._write_info()

    def add_admin(self):
        "3. add a admin user"
        self._write_info()