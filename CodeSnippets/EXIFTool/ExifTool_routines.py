#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    routines for the ExifTool - GPL - copyleft (c) 2007 Jens Diemer

    Note:
        Used the external programm 'exiftool'! (More info in 'ExifTool.py')
"""

import os, sys, datetime, time, shutil, stat, subprocess, pprint


# Possible Keys
EXIF_DATE_KEYS = ("Create Date", "File Modification Date/Time",)

# Must be lower case!
EXT_WHITELIST = (".pef", ".dng", ".jpg")


def timestamp2datetime(timestamp):
    """
    Convert a timestamp (number of seconds since the Epoch) to a datetime
    object.
    """
    assert isinstance(timestamp, int)
    t = time.gmtime(timestamp)
    date = time2datetime(t)
    return date

def time2datetime(date):
    """
    convert a time tuple into a datetime object.
    FIXME: timezone???
    """
    assert isinstance(date, (time.struct_time, tuple, list))
    date = datetime.datetime(*date[:7])
    return date


def debug_file_stat(fn):
    """
    print the current file dates out.
    """
    print "Current file date:"
    st = os.stat(fn)
    print "\ta time:", timestamp2datetime(st[stat.ST_ATIME])
    print "\tm time:", timestamp2datetime(st[stat.ST_MTIME])
    print "\tc time:", timestamp2datetime(st[stat.ST_CTIME])


def get_exif_data(fn, verbose=True):
    """
    run the exiftool for the given filename (>fn<) and returned the raw output
    """
    print
    cmd = ["exiftool", fn]
    print "> %s..." % cmd,

    try:
        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
        process.wait() # warten, bis der gestartete Prozess zu Ende ist
    except KeyboardInterrupt:
        print "\n(KeyboardInterrupt)"
        sys.exit()
    except OSError, e:
        msg = (
            "%s - (cmd: '%s')\n"
            " - Have you install the external programm 'exiftool'?"
        ) % (e, cmd)
        raise OSError(msg)

    print "OK (returncode: %s)" % process.returncode

    output = process.communicate()[0]
    return output

def parse_exif_out(output):
    """
    return a dict from the given exiftool >output<.
    """
    result = {}
    lines = output.split("\n")
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        try:
            key, value = line.split(":", 1)
        except ValueError, e:
            print "Error: %s" % e
            print "> %s" % line
            continue

        key = key.strip()
        value = value.strip()
        result[key] = value
    return result


def rdelete(txt, s):
    """
    >>> rdelete("12345+01", "+")
    '12345'
    >>> rdelete("12.345.678.90", ".")
    '12.345.678'
    """
    if s in txt:
        return txt.rsplit(s, 1)[0]
    return txt


def get_create_date(exif_data, debug=False):
    """
    return the create date as a time object. Used the EXIF_DATE_KEYS to find the
    date.
    """
    date = None
    for key in EXIF_DATE_KEYS:
        if  key in exif_data:
            date = exif_data[key]
            break
    if date == None:
        return

    print date

    # FIXME: Find a better way to handle a timezone offset:
    date = rdelete(date, "+")
    date = rdelete(date, "-")

    # Strip millisecond
    date = rdelete(date, ".")

    t = time.strptime(date, "%Y:%m:%d %H:%M:%S")
    if debug:
        print t

    return t


def set_file_date(fn, create_date, simulate_only):
    """
    Set the file date to >create_date<.
    """
    print "set file date to %s..." % time2datetime(create_date),
    create_date = time.mktime(create_date)
    atime = create_date
    mtime = create_date
    if simulate_only:
        print "(simulate only. File date not modified)\n"
    else:
        try:
            os.utime(fn, (atime, mtime))
        except OSError, e:
            print "Error:", e
        else:
            print "OK"


def get_pics_fn(path):
    """
    Retuns a list of all files recusive from the start >path<.
    Filter the files with EXT_WHITELIST.
    """
    for dirpath, dirnames, filenames in os.walk(path):
#        print dirpath
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.isfile(filepath):
                continue
            for ext in EXT_WHITELIST:
                if filename.lower().endswith(ext):
                    yield dirpath, filepath, filename



def get_file_info(path):
    """
    The main function. Set the file date from all files to the create date from the
    exif information.
    """
    if not os.path.isdir(path):
        raise WrongPathError("Given path is not valid: '%s'." % path)

    for dirpath, filepath, filename in get_pics_fn(path):
        output = get_exif_data(filepath, verbose=False)
        data = parse_exif_out(output)

    #    pprint.pprint(data)
    #    for k,v in data.iteritems():
    #        if "date" in k.lower():
    #            print k,v

        create_date = get_create_date(data)#, debug=True)
        if create_date == None:
            print "No date information found in exif data!"
            print "current file: %s skip." % filepath
            continue

        yield dirpath, filepath, filename, create_date

def get_first_existing_path(path):
    """
    returns the first existing part of the given path.
    """
    path = os.path.normpath(path)
    if os.path.isdir(path) or path == "/":
        return path
    else:
        next_path = os.path.dirname(path)
        assert next_path != path
        return get_first_existing_path(next_path)


def delete_empty(filepath, out):
    """
    Delete recusivly the given path. Stops if files/subdirectory exists.
    """
    out.write("Delete source path '%s'..." % filepath)
    if len(os.listdir(filepath)) != 0:
        out.write("not empty")
        return

    try:
        os.rmdir(filepath)
    except IOError, e:
        out.write("Error: %s" % e)
    else:
        out.write("OK")
        # the first half of the pair returned by os.path.split(path)
        next_path = os.path.dirname(filepath)
        delete_empty(next_path, out)



def process(source_path, destination, out, simulate_only, move_files,
                                                                    copy_files):
    counter = 0

    def simulate():
        if simulate_only:
            msg = "(simulate only.)"
            print msg
            out.write(msg)
            return True
        return False

    for dirpath, filepath, filename, create_date in get_file_info(source_path):
        out.write("")
        out.write("_" * 30)
        out.write("source file: %s" % filepath)
#        debug_file_stat(fn)
        out.write("create date from EXIF: %r" % create_date)

        year, month, day = ["%02i" % i for i in create_date[:3]]
        dest_path = os.path.join(destination, year, month, day)
        dest_path = os.path.abspath(dest_path)
        dest_path = dest_path.rstrip("/") + "/"

        out.write("file destination: %s" % dest_path)

        out.write("%s - %s" % (dirpath, dest_path))
        if dirpath.strip("/") == dest_path.strip("/"):
            msg = "No moving needed."
            print msg
            out.write(msg)
            continue

        if not os.path.isdir(dest_path):
            msg = "Create destination path..."
            print msg,
            out.write(msg)
            if not simulate():
                os.makedirs(dest_path, mode=0764)
                print "OK"

        if move_files:
            print "move %s to %s..." % (filepath, dest_path),
            if simulate():
                continue

#                try:
#                    shutil.move(filepath, dest_path)
#                except OSError, e:
#                    print "Error:", e
#                else:
#                    print "OK"

            process = subprocess.Popen(
                ['mv', filepath, dest_path],
                stdout=subprocess.PIPE
            )
            process.wait()
            print process.stdout.read()


        elif copy_files:
            print "copy %s to %s..." % (filepath, dest_path),
            if simulate():
                continue
            shutil.copy(filepath, dest_path)
            print "OK"
        else:
            # Should never be appear
            out.write("ERROR: copy or move only!")
            return

        if simulate():
            continue

        # Delete the source path, if it's empty
        delete_empty(dirpath, out)

        fn_dest = os.path.join(dest_path, filename)
        if not os.path.isfile(fn_dest):
            out.write(
                "ERROR: File not found, after copy or moveing! (%s)" % fn_dest
            )
            return

        set_file_date(fn_dest, create_date, simulate_only)

        counter += 1

    out.write("%s file(s) processed." % counter)


class WrongPathError(Exception):
    pass


if __name__ == '__main__':
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
    sys.exit()


    class Out(object):
        def write(self, txt):
            print txt

    source_path = "."
    dest_path = "."
#    source_path = "/home/jens/workspace/CodeSnippets/EXIFTool/2003/3/16"
#    source_path = "/home/jens/photos/2007_20GB_USB/08/17"
    out = Out()
    simulate_only = True
    move_files = True
    copy_files = False

    process(source_path, dest_path, out, simulate_only, move_files, copy_files)




