#!/usr/bin/python
# coding: ISO-8859-1

"""
    shared ftp objects
    ~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2013 by htFX.de - Jens Diemer
    :license: GNU GPL v3 or above
"""


import sys
import datetime
import ftplib
import posixpath

from utils import human_filesize, stdout_encoding, out


DIRECTORY = "DIR"
FILE = "FILE"
DATE_FORMAT = "%m-%d-%y %I:%M%p" # e.g.: 02-14-12 11:44AM


class FtpFileItem(object):
    def __init__(self, ftp, name, dir, filepath, date_string, time_string, size=0):
        self.ftp = ftp
        self.name = name
        self.dir = dir
        self.filepath = filepath

        datetime_string = "%s %s" % (date_string, time_string) # e.g.: 02-16-12 01:11PM
        self.mtime = datetime.datetime.strptime(datetime_string, DATE_FORMAT)
        #~ print datetime_string, self.mtime

        self.size = size

    def delete(self, dryrun=True):
        if dryrun:
            out(u"dry run: delete %s" % self.filepath)
        else:
            path = self.filepath.encode("utf-8")
            try:
                self.ftp.delete(path)
            except Exception, err:
                out(u"Error deleting %s: %s" % (repr(path), err))

    def __unicode__(self):
        return u"%s %s" % (human_filesize(self.size), posixpath.join(self.dir, self.name))

    def __repr__(self):
        o = self.__unicode__()
        return o.encode(stdout_encoding)



class FTP2(object):
    def __init__(self, url, user, passwd):
        sys.stderr.write("Connect to '%s'..." % url)
        self.ftp = ftplib.FTP(url)
        self.ftp.login(user=user, passwd=passwd)
        welcome = self.ftp.getwelcome()
        sys.stderr.write("OK\n%s\n" % welcome)
        print welcome
        print self.ftp.sendcmd("OPTS UTF8 ON")
        #~ print self.ftp.sendcmd("FEAT")
        #~ sys.exit()
        sys.stderr.write("Waiting for file listing...")

    def walk(self, dir):
        #~ print "list dir", dir.encode(stdout_encoding)

        if isinstance(dir, unicode):
            dir2 = dir.encode("utf-8")
        else:
            dir2 = dir

        # It doesnt work to put unicode/utf-8 directoryname to ftp.dir(), but
        # it works in ftp.cwd()
        try:
            self.ftp.cwd(dir2)
        except ftplib.error_perm, err:
            print " *** Error on %s: %s" % (dir, err)
            return

        listing = []
        try:
            self.ftp.dir(".", listing.append)
        except Exception, err:
            print " *** Error on %s: %s" % (dir, err)

        #~ print listing

        file_entries = []
        for line in listing:
            #~ print repr(line)
            line = line.decode("utf-8")

            cols = line.split(None, 3)
            #~ print cols
            item_date, item_time, item_type, item_name = cols

            path = posixpath.join(dir, item_name)
            if item_type == "<DIR>":
                for x in self.walk(path):
                    yield x
            else:
                size = int(item_type)
                file_entries.append(
                    FtpFileItem(self.ftp, item_name, dir, path, item_date, item_time, size)
                )

        yield dir, file_entries
