#!/usr/bin/python
# coding: UTF-8

"""
    Simple tools for remove non-DNG files, if .DNG exist.
"""

import os
import sys
import time
from pprint import pprint


KEEP_EXT = (".dng",) # lowcase!
REMOVEABLE = (".pef",) # lowcase!
MIN_FILE_SIZE_PERCENT=80.0 # the dng file must be at least x-% of the original file


def filesizeformat(i):
    """
    Taken from jinja
    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    bytes = float(i)
    if bytes < 1024:
        return u"%d Byte%s" % (bytes, bytes != 1 and u's' or u'')
    if bytes < 1024 * 1024:
        return u"%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return u"%.1f MB" % (bytes / (1024 * 1024))
    return u"%.1f GB" % (bytes / (1024 * 1024 * 1024))


def build_dupes_dict(files):
    """
    >>> build_dupes_dict(["file.PEF", "file.dng"])
    {'file': ['.PEF', '.dng']}

    >>> build_dupes_dict(["file1.PEF", "file2.dng"])
    {'file2': ['.dng'], 'file1': ['.PEF']}
    """
    dupes_dict = {}
    for filename in files:
        name, ext = os.path.splitext(filename)
        if name not in dupes_dict:
            dupes_dict[name] = [ext,]
        else:
            dupes_dict[name].append(ext)
    return dupes_dict


def build_remove_list(dupes_dict):
    """
    >>> KEEP_EXT = (".dng",) # lowcase!
    >>> REMOVEABLE = (".pef",) # lowcase!

    >>> build_remove_list({"filename": set(['.PEF', '.dng'])})
    ['filename.PEF']

    >>> build_remove_list({"filename": set(['.PEF', '.DNG', '.jpg'])})
    ['filename.PEF']

    >>> build_remove_list({"filename": set(['.PEF'])})
    []
    >>> build_remove_list({"filename": set(['.PEF', '.jpg'])})
    []
    """
    remove_list = []
    for filename, ext_list in dupes_dict.iteritems():
        if len(ext_list)<2:
            continue

        can_cleanup = False
        to_clean = []
        for exist_ext in ext_list:

            if exist_ext.lower() in KEEP_EXT:
                can_cleanup = True
            elif exist_ext.lower() in REMOVEABLE:
                to_clean.append(filename + exist_ext)

        if to_clean and can_cleanup:
            remove_list += to_clean

    return remove_list


def remove_non_dng(dir, dry_run=True, verbose=1):
    print "remove non-DNGs from %r" % dir

    if not os.path.exists(dir):
        print "Error: Directory %r doesn't exist." % dir
        return

    last_status = time.time()
    remove_count = 0
    file_count = 0
    dir_count = 0
    for root, dirs, files in os.walk(dir):
        dir_count += 1
        file_count += len(files)
        if verbose and time.time()-last_status>1:
            last_status=time.time()
            print "%i dirs and %i files processed (%i dupes removed)..." % (
                dir_count, file_count, remove_count
            )

        dupes_dict = build_dupes_dict(files)

        if verbose>=2:
            pprint(dupes_dict)

        remove_list = build_remove_list(dupes_dict)
        dir_info_printed = False
        for filename in remove_list:
            if not dir_info_printed:
                dir_info_printed = True
                print "_"*79
                print "%s - %s" % (dir_count, root)
                print " -"*40

            abs_path = os.path.join(root, filename)

            test_passed = False
            for ext in KEEP_EXT:
                test_filename = os.path.splitext(filename)[0] + ext
                test_path = os.path.join(root, test_filename)
                if os.path.isfile(test_path):
                    if verbose>=1:
                        print "File %r exists." % test_path

                    source_filesize = os.path.getsize(abs_path)
                    keep_filesize = os.path.getsize(test_path)
                    percent=100.0*keep_filesize/source_filesize
                    filesize_msg = "%.1f%% (%s/%s)" % (
                        percent,
                        filesizeformat(keep_filesize),
                        filesizeformat(source_filesize)
                    )
                    if percent<MIN_FILE_SIZE_PERCENT:
                        print ">>> Error: Filesize to low: %s and not min. %.1f%%" % (
                            filesize_msg, MIN_FILE_SIZE_PERCENT
                        )
                    else:
                        if verbose:
                            print "Filesize: %s, ok." % filesize_msg
                        test_passed = True
                        break
            if not test_passed:
                print "No valid %s found. Skip removing." % ", ".join(KEEP_EXT)
                print
                continue

            print "remove %r..." % abs_path,
            if dry_run:
                print "(Dry run only, do nothing)"
            else:
                os.remove(abs_path)
                remove_count += 1
                print "OK"
            print

    print "%i dupe files removed." % remove_count


if __name__ == "__main__":
    import doctest
    doctest.testmod()


    remove_non_dng(
        os.getcwd(),
        #~ dry_run=False,
        dry_run=True,
        verbose=1,
    )
