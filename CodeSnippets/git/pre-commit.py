#!/usr/bin/env python
# coding:utf-8

"""
    a git pre-commit hook to update a date in __version__
    
    more info in README:
    https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/#readme
    
    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
    :homepage: https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/
"""


import os
import re
import datetime


#DEBUG = True
DEBUG = False

FILENAMES = ("__init__.py",)
VERSION_PREFIX = "__version__"
VERSION_REGEX = re.compile(r'^__version__ = \((.*,\s*)(\d{6}\s*)\)$', re.MULTILINE)
NEW_VERSION = '__version__ = (%(ver)s%(date)s)'

NEW_DATE = datetime.datetime.utcnow().strftime("%y%m%d")


class DateChanger(object):
    def __init__(self):
        self.changed = False
        self.matched = False

    def sub(self, matchobj):
        self.matched = True

        old_date = matchobj.group(2)

        if old_date == NEW_DATE:
            if DEBUG:
                print "date %r is up to date" % old_date
            return matchobj.group(0)

        if DEBUG:
            print "change date from %r to %r" % (old_date, NEW_DATE)
        self.changed = True

        version = matchobj.group(1)
        new_date = NEW_VERSION % {"ver": version, "date": NEW_DATE}

        return new_date


def update_file(filepath):
    with file(filepath, "r") as f:
        old_content = f.read()
    if not VERSION_PREFIX in old_content:
        return

    if DEBUG:
        print "VERSION_PREFIX found in %r" % filepath

    date_changer = DateChanger()

    new_content = VERSION_REGEX.sub(date_changer.sub, old_content)
    if not date_changer.matched:
        print "Error: date not found in %s" % filepath
        return
    if not date_changer.changed:
        print "No updated needed in %r" % filepath
        return

    print "update __version__ with %r in file %r" % (NEW_DATE, filepath)
    with file(filepath, "w") as f:
        f.write(new_content)


def update_version_number(path):
    count = 0
    for root, dirlist, filelist in os.walk(path, followlinks=True):
        for filename in FILENAMES:
            if filename in filelist:
                count += 1
                update_file(os.path.join(root, filename))
    print "(%i files checked.)" % count


if __name__ == '__main__':
    print "*** START %r ***" % __file__
    update_version_number(".")
    print "*** END %r ***" % __file__
