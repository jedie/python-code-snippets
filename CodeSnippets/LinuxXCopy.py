#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
xcopy for Linux...

Use:
______________________________________________________________________________
import sys, os

sys.path.insert(0,r"/path/to/LinuxXCopy")

from LinuxXCopy import XCopy

filters = ["*.py"]

xc = XCopy(os.getcwd(), "/tmp/test", filters)
______________________________________________________________________________
"""

__author__  = "Jens Diemer"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__     = "http://www.jensdiemer.de"

__info__    = ""

__version__="0.1"

__history__="""
v0.1
    - erste Version
"""


import os, shutil, fnmatch

class XCopy:
    def __init__(self, src, dst, filters=[]):
        self.filters = filters

        self.copytree(src, dst)

    def copytree(self, src, dst):
        """
        Based in shutil.copytree()
        """
        names = os.listdir(src)
        if not os.path.isdir(dst):
            os.makedirs(dst)
        errors = []
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)

            if os.path.isdir(srcname):
                self.copytree(srcname, dstname)
            elif os.path.isfile(srcname):
                if self.filterName(name):
                    print "copy:", name, dstname
                    shutil.copy2(srcname, dstname)

        shutil.copystat(src, dst)

    def filterName(self, fileName):
        for filter in self.filters:
            if fnmatch.fnmatch(fileName, filter):
                return True
        return False



