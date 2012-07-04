#!/usr/bin/python
# coding: ISO-8859-1

"""
    CLI for the ftp tools
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
"""

import argparse

from __init__ import VERSION_STRING


class BaseCLI(object):
    def __init__(self, description):
        self.parser = argparse.ArgumentParser(
            description=description,
            epilog="ftp-tools v%s copyleft by Jens Diemer, GNU GPL v3 or above" % VERSION_STRING
        )
        self.parser.add_argument("host", help="FTP server address, e.g.: ftp.domain.tld")
        self.parser.add_argument("username", help="FTP user name")
        self.parser.add_argument("password", help="FTP password")
        self.parser.add_argument("-p", "--path", help="root path to start the tree walk", default="/")
        self.parser.add_argument(
            "-v", "--verbosity", type=int, choices=[0, 1, 2], default=1,
            help="increase output verbosity"
        )
