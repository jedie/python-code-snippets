#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" sync svn:keywords

Used svn_keyword.py from:

http://trac.pylucid.net/browser/CodeSnippets/svn_keywords.py
or
http://svn.pylucid.net/pylucid/CodeSnippets/svn_keywords.py

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$
$HeadURL$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import sys, os

sys.path.insert(0,"../../CodeSnippets/")

try:
    from svn_keywords import Config, cleanup, print_status, sync_keywords
except ImportError, e:
    print "Error, can't import svn_keywords.py:"
    print e
    print
    print "(More Information in Doc-String)"
    print
    sys.exit()

config = Config
config.repository = "."
config.simulation = False
#~ config.simulation = True
config.no_keyword_file_ext = (".zip",".mzp")


if __name__ == "__main__":
    cleanup(config)
    sync_keywords(config)
    print_status(config)