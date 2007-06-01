#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Delete dump_db files not needed for a first-time-installation.
"""

import os, sys
os.chdir("../../") # go into PyLucid App root folder
#print os.getcwd()
sys.path[0] = os.getcwd()

from PyLucid import settings



SIMULATE = True
APP_NAME = "PyLucid"


# DB data files not needed for installation
UNNEEDED_FILES = (
    "archive", "md5user", "object_cache", "pages_internal", "plugin",
    "plugindata",
)




def delete_file(path):
        print "delete '%s'" % filename,
        if SIMULATE:
            print "[simulate only]",
        else:
            os.remove(abs_path)
        print "OK\n"

filelist = os.listdir(settings.INSTALL_DATA_DIR)

prefix_len = len(APP_NAME)
filelist.sort()
for filename in filelist:
    if filename.startswith("."):
        # e.g. .svn
        continue

    abs_path = os.path.join(settings.INSTALL_DATA_DIR, filename)

    if not filename.startswith(APP_NAME):
        # django tables
        delete_file(abs_path)
        continue

    # Cut prefix and externsion out
    fn_cut = filename[prefix_len:-3]
#    print fn_cut
    if fn_cut in UNNEEDED_FILES:
        delete_file(abs_path)
        continue

    print "needed file:", filename
    print
