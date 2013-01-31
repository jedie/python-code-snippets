#!/usr/bin/python
# coding: ISO-8859-1

"""
    delete old files
    ~~~~~~~~~~~~~~~~
    
    Cleanup a FTP Server by deleting the files which are older than X days.

    :copyleft: 2012-2013 by htFX.de - Jens Diemer
    :license: GNU GPL v3 or above
"""

import sys
import time
import datetime

from cli import BaseCLI
from utils import human_filesize, out, human_timedelta
from ftp_base import FTP2


now = datetime.datetime.now()

timedelta2 = datetime.timedelta(days=365) # nur zum validieren


class CLI(BaseCLI):
    def __init__(self, description):
        super(CLI, self).__init__(description)
        self.parser.add_argument(
            "-d", "--days", type=int, choices=xrange(7, 20), default=14,
            help="how many days must a file be old for delete?"
        )


if __name__ == "__main__":
    cli = CLI(description="Cleanup a FTP Server by deleting the files which are older than X days.")
    args = cli.parse_args()
    if args.verbosity >= 2:
        print args

    if args.verbosity:
        print "Delete all files which are older than %s days from %s%s" % (
            args.days, args.host, args.path
        )

    if args.dryrun:
        sys.stderr.write("\ndry run, active.\n")
    elif args.info:
        sys.stderr.write("\nrun in information mode (don't cleanup FTP)\n")
    else:
        sys.stderr.write("\ncontinue cleanup ftp server (yes/no) ?\n")
        try:
            use_input = raw_input()
        except KeyboardInterrupt:
            print "Abort, ok."
            sys.exit(1)
        use_input = use_input.lower()
        if not (use_input.startswith("y") or use_input.startswith("j")):
            print "Abort, ok."
            sys.exit(2)

    ftp = FTP2(args.host, user=args.username, passwd=args.password)

    path = args.path
    timedelta1 = datetime.timedelta(days=args.days)

    size_info = {}
    date_info = {}
    total_size = 0
    dir_count = 0
    file_count = 0
    delete_info = {}
    deleted_files_count = 0
    cleared_size = 0

    start_time = time.time()
    next_update = start_time

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

            if time.time() > next_update:
                next_update = time.time() + 1
                if args.info:
                    # information only mode
                    msg = (
                        "\r%i files/%i dirs readed"
                        " - filesize: %s...   "
                    ) % (
                        file_count, dir_count, human_filesize(total_size)
                    )
                else:
                    # cleanup mode
                    msg = (
                        "\r%i files/%i dirs readed"
                        " - filesize: %s deleted: %i (%s)...   "
                    ) % (
                        file_count, dir_count, human_filesize(total_size),
                        deleted_files_count, human_filesize(cleared_size),
                    )
                sys.stderr.write(msg)

            size = file_entry.size
            mtime = file_entry.mtime

            if not args.info:
                delta = now - mtime
                assert delta < timedelta2, "Error!!! Filedate is older than %s ?!?!" % timedelta2
                if delta > timedelta1:
                    #~ out(
                        #~ " *** %r is older than %s days: %s" % (
                            #~ file_entry.filepath, timedelta1.days, mtime
                        #~ )
                    #~ )
                    _add_to_dict_list(delete_info, size, file_entry)
                    cleared_size += file_entry.size
                    file_entry.delete(dryrun=args.dryrun)
                    deleted_files_count += 1
                    continue

            total_size += size

            _add_to_dict_list(size_info, size, file_entry)
            _add_to_dict_list(date_info, mtime, file_entry)


    print
    print
    out(
        u"**** total size: %s - %s files in %s folders" % (
            human_filesize(total_size), file_count, dir_count
        )
    )

    if not args.info:
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
    print " Die größten Dateien:"
    print "======================"
    sizes = size_info.keys()
    sizes.sort(reverse=True)
    count = 0
    for size in sizes[:20]:
        for file_entry in size_info[size]:
            count += 1
            if count >= 20:
                break
            delta = now - file_entry.mtime
            out(u"%-23s - %s" % (human_timedelta(delta), unicode(file_entry)))
        if count >= 30:
            break


    print
    print " Die ältesten Dateien:"
    print "======================="
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
            out(u"%-23s - %s" % (human_timedelta(delta), unicode(file_entry)))
        if count >= 30:
            break

    print
    print "-END-"
