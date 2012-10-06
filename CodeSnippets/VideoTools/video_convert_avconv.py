#!/usr/bin/env python
# coding: utf-8

"""
    video converter
    ~~~~~~~~~~~~~~~

    Convert video files to h264 + MP3 in a .mkv container.
    Used 'avconv' with 'libx264' for video and 'libmp3lame' for audio.

    Create a log file and add 'mediainfo' output.

    Needs under ubuntu the packages e.g.:
        libavcodec-extra
        mediainfo
        python-kaa-metadata

    * works only under linux.
    * convert all files (with SOURCE_EXT extension) in the current directory
    * add date string to output filename

    :copyleft: 2011-2012 by Jens Diemer
    :license: GNU GPL v3 or above
"""

import os
import sys
import time
import subprocess
import stat
from datetime import datetime
from pprint import pprint, pformat
import stat

try:
    import kaa.metadata
except ImportError, err:
    print "Error:", err
    print "Have you installed 'python-kaa-metadata'?"
    print "Homepage: http://freevo.org/kaa"
    sys.exit()

#~ SOURCE_EXT = (".avi",)
SOURCE_EXT = (".avi", ".mov", ".mp4")

AVCONV_OPTIONS = [
#    "-v 47",
#    "-er", "explode",
#    "-err_detect", "crccheck,bitstream,buffer",

#    "-vcodec", "copy",
    "-vcodec", "libx264",
        "-crf", "22",
        "-profile:v", "high",
#        "-preset", "ultrafast",
        "-preset", "slow",
        "-tune", "film",

    "-acodec", "libmp3lame", "-b:a", "128k",
#    "-acodec", "flac"
#    "-acodec", "copy"
]
FILENAME_SUFFIX = "_x264_mp3"
#FILENAME_SUFFIX = "_x264_mp3_ultrafast"
#FILENAME_SUFFIX="_x264_flac"

#CONVERT_ONLY_ONE_FILE = True
CONVERT_ONLY_ONE_FILE = False

#~ SIMULATE_ONLY = True
SIMULATE_ONLY = False

STARTWITH_TEST = range(1990, 2020)

MONTH_MAP = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

SKIP_FIELDS = ("audio", "url",)


def pformat_info(kaa_info):
    #~ import pickle
    #~ print pickle.dumps(kaa_info)
    result = "kaa_info = {\n"
    for attr in dir(kaa_info):
        if attr.startswith("_") or attr in SKIP_FIELDS:
            continue

        data = getattr(kaa_info, attr, "---")
        if isinstance(data, (list, dict)):
            result += "'%s': %s,\n" % (attr, pformat(data))
        elif isinstance(data, (basestring, bool, int, long, float)):
            result += "'%s': %s,\n" % (attr, data)
        #~ else:
            #~ print "***", attr, data, type(data)
    result += "}"
    return result


def get_date(kaa_info):
    try:
        date_string = kaa_info.date
    except AttributeError, err:
        #~ print "No date:", err
        timestamp = kaa_info["timestamp"]
        if timestamp is not None:
            print "Use timestamp: %r" % timestamp
            dt = datetime.fromtimestamp(timestamp)
            return dt
        else:
            # Pentax ?
            try:
                date_string = kaa_info["header"]["hdrl"]["IDIT"]
            except KeyError, err:
                print "KeyError: %s" % err
                print " -"*40
                print pformat_info(kaa_info)
                print "="*80
                return
            print "use date string %r" % date_string
            dt = datetime.strptime(date_string, "%Y/%m/%d %H:%M:%S")
            return dt
    else:
        print "Use date: %r" % date_string
        dt = datetime.strptime(date_string, "%y.%m.%d %H:%M:%S")
        return dt


def change_title(txt):
    sys.stdout.write("\x1b]2;%s\x07" % txt)


class VideoFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.name, self.ext = os.path.splitext(self.filename)

        kaa_info = kaa.metadata.parse(filename)
        #~ print "*"*80
        #~ print pformat_info(kaa_info)
        #~ print "*"*80

        try:
            self.dt = get_date(kaa_info)
        except Exception, err:
            print "*** kaa error (file %r): %s" % (filename, err)
            return

        if self.dt:
            self.date_str = datetime.strftime(self.dt, "%Y-%m-%d_%Hh%Mm")
            if self.name.startswith(self.date_str):
                _prefix = self.name + FILENAME_SUFFIX
            else:
                _prefix = self.date_str + "_" + self.name + FILENAME_SUFFIX
            self.out_name = "%s.mkv" % _prefix
            self.log_name = "%s.log" % _prefix


    def rename(self):
        print self.name, self.date_str,
        if self.name.startswith(self.date_str):
            print "ja"
            return
        print "nein"

        new_filename = self.date_str + "_" + self.filename
        print "rename %r to %r" % (self.filename, new_filename)
        if SIMULATE_ONLY:
            print "(simulate only)"
            return

        os.rename(self.filename, new_filename)
        # Update filenames:
        self.filename = new_filename
        self.name, self.ext = os.path.splitext(self.filename)

    def test(self):
        if "xvid" in self.name.lower():
            print "Skip Xvid file '%s'" % filename
            return False

        if "x264" in self.name.lower():
            print "Skip x264 file '%s'" % filename
            return False

        if self.dt is None:
            print "*** Error: No datetime found, skip."
            return False

        if os.path.isfile(self.out_name):
            print "Skip existing file '%s'" % self.out_name
            return False

        return True


class VideoConverter(object):
    def __init__(self):
        files = self.read_current_dir()
        file_count = len(files)
        print "found %s files to convert." % file_count

        for no, file in enumerate(files):
            print "_"*79
            file.rename()
            txt = " *** convert file %i/%i - %s ***" % (no, file_count, file.filename)
            change_title(txt)
            print txt

            try:
                self.mediainfo_to_log(file)
                self.convert(file)
            except (Exception, KeyboardInterrupt), e:
                print
                print
                print "Abort: %s" % e
                print
                self.delete_files([
                    file.out_name,
                    file.log_name,
                ])
                print "bye ;)"
                sys.exit(1)

            print "_"*79
            print "converting video %s done." % file.filename
            print

            if CONVERT_ONLY_ONE_FILE:
                return

    def delete_files(self, files):
        for filename in files:
            if os.path.exists(filename):
                print
                print "Remove %r..." % filename,
                try:
                    os.remove(filename)
                except Exception, err:
                    print "Error:", err
                else:
                    print "OK"

    def read_current_dir(self):
        files = []
        for filename in sorted(os.listdir(".")):
            name, ext = os.path.splitext(filename)
            if ext.lower() not in SOURCE_EXT:
                continue
            print "_"*79
            print "File:", filename

            f = VideoFile(filename)
            if f.test() != True:
                continue

            files.append(f)
            if CONVERT_ONLY_ONE_FILE:
                break

        return files

    def mediainfo_to_log(self, file):
        cmd = ["mediainfo", "--Full", file.filename, "--LogFile=%s" % file.log_name]
        print "_"*79
        print " ".join(cmd)
        if SIMULATE_ONLY:
            print "(simulate only!)"
            return
        subprocess.Popen(cmd).wait()

    def convert(self, file):
        cmd = [
            "nice",
            "avconv", "-i", file.filename
        ] + AVCONV_OPTIONS + [
            file.out_name,
            "2>&1 | tee --append", file.log_name,
        ]
        print "_"*79
        cmd = " ".join(cmd)
        print cmd
        print " -"*40
        if SIMULATE_ONLY:
            print "(simulate only!)"
            return

        subprocess.Popen(cmd, shell=True).wait()




if __name__ == '__main__':
    v = VideoConverter()
