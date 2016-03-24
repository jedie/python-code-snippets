#!/usr/bin/python
# coding: ISO-8859-1

"""
    CLI for the ftp tools
    ~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2013 by Jens Diemer
    :license: GNU GPL v3 or above
"""


import argparse
import logging


__version__ = (0, 1, 1)
VERSION_STRING = '.'.join(str(part) for part in __version__)

TITLE_LINE = "ftp-tools v%s copyleft 2013 by htfx.de - Jens Diemer, GNU GPL v3 or above" % VERSION_STRING


log = logging.getLogger("ftp-tools")

LOG_FORMATTER = logging.Formatter("%(asctime)s %(message)s")
LOG_LEVEL_DICT = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG
}


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
            "--verbosity", type=int, choices=[0, 1, 2, 3], default=1,
            help="increase output verbosity"
        )
        self.parser.add_argument("-log", "--logfile", help="log into file (UTF8)")
        self.parser.add_argument(
            "--stdout_log", action="store_true",
            help="log to stdout"
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

        log_level = LOG_LEVEL_DICT[args.verbosity]
        log.setLevel(log_level)

        logfilename = args.logfile
        if logfilename:
            handler = logging.FileHandler(logfilename, encoding="utf8")
            handler.setFormatter(LOG_FORMATTER)
            log.addHandler(handler)

        if args.stdout_log:
            handler = logging.StreamHandler()
            handler.setFormatter(LOG_FORMATTER)
            log.addHandler(handler)

        for arg, value in sorted(vars(args).items()):
            logging.debug("argument %s: %r", arg, value)
        return args
