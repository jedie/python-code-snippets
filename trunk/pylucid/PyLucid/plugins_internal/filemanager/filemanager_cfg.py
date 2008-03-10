#!/usr/bin/python
# -*- coding: UTF-8 -*-

#_____________________________________________________________________________
# meta information

__author__      = "Ibon, Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "Media file list"
__long_description__ = """
List files in yor media dir (MEDIA_ROOT), create and delete files and
directories

Settings.py

MEDIA_ROOT = "/home/userjk/pylucid/PyLucid_v0.8RC2_full/pylucid/media"

Need Page Internals: file_form.html
"""

#_____________________________________________________________________________
# plugin administration data

global_rights = {
    "must_login"    : True,
    "must_admin"    : True,
}
plugin_manager_data = {
    "lucidTag" : global_rights,
    "filelist" : global_rights,
    "select_basepath": global_rights,
    "edit": global_rights,
    "userinfo": global_rights,
}
