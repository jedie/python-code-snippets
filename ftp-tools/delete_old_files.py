#!/usr/bin/python
# coding: ISO-8859-1

"""
    delete old files
    ~~~~~~~~~~~~~~~~
    
    Cleanup a FTP Server by deleting the files which are older than X days.

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

DRY_RUN = True
#DRY_RUN = False

now = datetime.datetime.now()

timedelta1 = datetime.timedelta(days=14)
#~ timedelta1 = datetime.timedelta(days=7)

timedelta2 = datetime.timedelta(days=365) # nur zum validieren


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


def out(*txt):
    for i in txt:
        assert isinstance(i, unicode), "%s is not unicode!" % repr(i)
    txt = u" ".join([i for i in txt])
    print txt.encode(stdout_encoding)


class FileItem(object):
    def __init__(self, ftp, name, dir, filepath, date_string, time_string, size=0):
        self.ftp = ftp
        self.name = name
        self.dir = dir
        self.filepath = filepath

        datetime_string = "%s %s" % (date_string, time_string) # e.g.: 02-16-12 01:11PM
        self.mtime = datetime.datetime.strptime(datetime_string, DATE_FORMAT)
        #~ print datetime_string, self.mtime

        self.size = size

    def delete(self):
        if DRY_RUN:
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

            path = posixpath.join(dir, item_name)
            if item_type == "<DIR>":
                for x in self.walk(path):
                    yield x
            else:
                size = int(item_type)
                file_entries.append(
                    FileItem(self.ftp, item_name, dir, path, item_date, item_time, size)
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
    delete_info = {}
    deleted_files_count = 0
    cleared_size = 0
    
    start_time = time.time()
    next_update = start_time + 1
    
    
    def _add_to_dict_list(d, key, value):
        if key not in d:
            d[key] = [value]
        else:
            d[key].append(value)
    
    
    for root, file_entries in ftp.walk(path):
        dir_count += 1
    
        for file_entry in file_entries:
            file_count += 1
            #~ print "***", repr(file_entry),
    
            if time.time()>next_update:
                next_update = time.time() + 1
                print (
                    "%i files in %i dirs readed"
                    " - filesize: %s - deleted: %i - cleared: %s..."
                ) % (
                    file_count, dir_count, human_filesize(total_size),
                    deleted_files_count, human_filesize(cleared_size),
                )
    
            size = file_entry.size
            mtime = file_entry.mtime
    
            delta = now - mtime
            assert delta<timedelta2, "Error!!! Filedate is older than %s ?!?!" % timedelta2
            if delta>timedelta1:
                #~ out(
                    #~ " *** %r is older than %s days: %s" % (
                        #~ file_entry.filepath, timedelta1.days, mtime
                    #~ )
                #~ )
                _add_to_dict_list(delete_info, size, file_entry)
                cleared_size += file_entry.size
                file_entry.delete()
                deleted_files_count += 1
                continue
    
            total_size += size
    
            _add_to_dict_list(size_info, size, file_entry)
            _add_to_dict_list(date_info, mtime, file_entry)
    
    
    print
    print
    out(u"**** total size:", human_filesize(total_size))
    
    print
    out(
        u"** Ingesammt %i Dateien gelöscht und %s freigemacht:" % (
            deleted_files_count, human_filesize(cleared_size)
        )
    )
    sizes = delete_info.keys()
    sizes.sort(reverse=True)
    count = 0
    for size in sizes:
        for file_entry in delete_info[size]:
            out(
                u"%s - %s" % (file_entry.mtime, unicode(file_entry))
            )
    
    
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
            out(unicode(file_entry))
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
            #~ mtime = file_entry.mtime.strftime("%d.%m.%y %H:%M")
            #~ print "%s - %s" % (mtime, repr(file_entry))
            delta = now - file_entry.mtime
            out(u"%s - %s" % (delta, unicode(file_entry)))
        if count >= 30:
            break