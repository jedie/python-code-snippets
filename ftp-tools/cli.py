#!/usr/bin/python
# coding: ISO-8859-1

"""
    CLI for the ftp tools
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2013 by Jens Diemer
    :license: GNU GPL v3 or above
"""

import argparse
import sys

__version__ = (0, 1, 1)
VERSION_STRING = '.'.join(str(part) for part in __version__)

TITLE_LINE = "ftp-tools v%s copyleft 2013 by htfx.de - Jens Diemer, GNU GPL v3 or above" % VERSION_STRING

class BaseCLI(object):
    def __init__(self, description):
        self.parser = argparse.ArgumentParser(
            description=description,
            epilog=TITLE_LINE,
            version=VERSION_STRING
        )
        self.parser.add_argument("host", help="FTP server address, e.g.: ftp.domain.tld")
        self.parser.add_argument("username", help="FTP user name")
        self.parser.add_argument("password", help="FTP password")
        self.parser.add_argument("-p", "--path", help="root path to start the tree walk", default="/")
        self.parser.add_argument(
            "--verbosity", type=int, choices=[0, 1, 2], default=1,
            help="increase output verbosity"
        )
        self.parser.add_argument(
            "--dryrun", action="store_true",
            help="run but don't make any changes"
        )
        self.parser.add_argument(
            "--info", action="store_true",
            help="Display only information about the files on the FTP (Don't delete anything)"
        )

    def parse_args(self):
        print
        print TITLE_LINE
        print "-"*79
        print

        args = self.parser.parse_args()
        return args
