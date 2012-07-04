#!/usr/bin/python
# coding: ISO-8859-1

"""
    ftp info
    ~~~~~~~~
    
    List information about the biggest files on a FTP server.

    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
"""

import os
import sys
import time
import datetime
import posixpath

import ftplib

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding()

DIRECTORY = "DIR"
FILE = "FILE"
DATE_FORMAT = "%m-%d-%y %I:%M%p" # e.g.: 02-14-12 11:44AM

def human_filesize(i):
    """
    'human-readable' file size (i.e. 13 KB, 4.1 MB, 102 bytes, etc).
    """
    bytes = float(i)
    if bytes < 1024:
        return u"%d Byte%s" % (bytes, bytes != 1 and u's' or u'')
    if bytes < 1024 * 1024:
        return u"%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return u"%.1f MB" % (bytes / (1024 * 1024))
    return u"%.1f GB" % (bytes / (1024 * 1024 * 1024))


class FileItem(object):
    def __init__(self, name, dir, date_string, time_string, size=0):
        self.name = name
        self.dir = dir

        datetime_string = "%s %s" % (date_string, time_string) # e.g.: 02-16-12 01:11PM
        self.mtime = datetime.datetime.strptime(datetime_string, DATE_FORMAT)
        #~ print datetime_string, self.mtime

        self.size = size

    def __str__(self):
        return u"%s %s" % (human_filesize(self.size), posixpath.join(self.dir, self.name))

    def __repr__(self):
        o = self.__str__()
        return o.encode(stdout_encoding)


class FTP2(object):
    def __init__(self, url, user, passwd):
        self.ftp = ftplib.FTP(url)
        self.ftp.login(user=user, passwd=passwd)
        print self.ftp.getwelcome()
        print self.ftp.sendcmd("OPTS UTF8 ON")
        #~ print self.ftp.sendcmd("FEAT")
        #~ sys.exit()

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

            if item_type == "<DIR>":
                path = posixpath.join(dir, item_name)
                for x in self.walk(path):
                    yield x
            else:
                size = int(item_type)
                file_entries.append(
                    FileItem(item_name, dir, item_date, item_time, size)
                )

        yield dir, file_entries


if __name__ == "__main__":
    ftp = FTP2('ftp.domain.tld', user="the ftp username", passwd="ftp user password")
    path = "/"
    
    
    size_info = {}
    date_info = {}
    total_size = 0
    dir_count = 0
    file_count = 0
    
    start_time = time.time()
    next_update = start_time + 1
    
    for root, file_entries in ftp.walk(path):
        dir_count += 1
        file_count += len(file_entries)
    
        if time.time()>next_update:
            next_update = time.time() + 1
            print "%i files in %i dirs readed (filesize: %s)..." % (
                file_count, dir_count, human_filesize(total_size)
            )
    
        for file_entry in file_entries:
            #print "***", repr(file_entry)
            size = file_entry.size
            total_size += size
            if size not in size_info:
                size_info[size] = [file_entry]
            else:
                size_info[size].append(file_entry)
    
            mtime = file_entry.mtime
            if mtime not in date_info:
                date_info[mtime] = [file_entry]
            else:
                date_info[mtime].append(file_entry)
    
    
    print
    print
    print "**** total size:", human_filesize(total_size)
    print
    
    print "** Die größten Dateien:"
    sizes = size_info.keys()
    sizes.sort(reverse=True)
    count = 0
    for size in sizes[:20]:
        for file_entry in size_info[size]:
            count += 1
            if count >= 20:
                break
            print repr(file_entry)
        if count >= 30:
            break
    
    
    print
    print "** Die ältesten Dateien:"
    mtimes = date_info.keys()
    mtimes.sort()
    count = 0
    for mtime in mtimes[:30]:
        for file_entry in date_info[mtime]:
            count += 1
            if count >= 30:
                break
            mtime = file_entry.mtime.strftime("%d.%m.%y %H:%M")
            print "%s - %s" % (mtime, repr(file_entry))
        if count >= 30:
            break