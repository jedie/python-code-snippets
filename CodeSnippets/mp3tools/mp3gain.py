#!/usr/bin/env python
# coding: utf-8

"""
    MP3 Gain client script
    ~~~~~~~~~~~~~~~~~~~~~~
    
    Apply MP3 Gain to all mp3 files.
    It reads all mp3 dirs and process the dirs from the newest modification time to the oldest.

    
    http://mp3gain.sourceforge.net/
   
    
    using
    ~~~~~
    
    Use a small dispatcher file like this one:
    --------------------------------------------------------------------------
        #!/usr/bin/env python
        # coding: utf-8

        import os
        import sys
        
        sys.path.insert(0, "c:\\path\\to\\mp3gain_dir\\")

        from mp3gain import Config, main

        cfg = Config
        
        cfg.debug = False
        cfg.base_dir = os.path.expanduser("~/my_mp3s/")
        
        main(cfg)

        raw_input("ENTER") # If you start it with the mouse ;)
    --------------------------------------------------------------------------
    
    
    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2009 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE.txt for more details.
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__version__ = "SVN $Rev: $"

import os
import sys
import time
import pprint
import fnmatch
import subprocess



def human_time(t):
    if t > 3600:
        divisor = 3600.0
        unit = "h"
    elif t > 60:
        divisor = 60.0
        unit = "min"
    else:
        divisor = 1
        unit = "sec"

    return "%.1f%s" % (round(t / divisor, 2), unit)


class Config(object):
    """
    Contains the configurations.

    base_dir
        Directory witch contains the MP3 files. (The artist direcories)
    """
    base_dir = None
    debug = True
    verbose = True
    mp3gain_path = ""
    mp3gain_args = [
        "-k", # automatically lower Track/Album gain to not clip audio
        "-a", # apply Album gain automatically
        "-o", # output is a database-friendly tab-delimited list
        "-p", # Preserve original file timestamp
#        "-s r", # force re-calculation (do not read tag info)
    ]



def mp3gain_filename(cfg):
    filename = "mp3gain"
    if sys.platform == "win32":
        filename += ".exe"

    return os.path.join(cfg.mp3gain_path, filename)


def check(cfg):
    """ check if mp3gain.exe exist. """
    filename = mp3gain_filename(cfg)

    process = subprocess.Popen(
        args=[filename, "-v"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
    )
    process.wait()
    if process.returncode != 0:
        print "Error:"
        print "\t'%s' not found." % filename
        print "\tUse -p PATH to specify the path to MP3Gain"
        print "\t(Download from: http://mp3gain.sourceforge.net)"
        if cfg.verbose:
            print "stdout:", process.stdout.read()
            print "stderr:", process.stderr.read()
        sys.exit(1)
    else:
        print process.stderr.read().strip()

    assert os.path.isdir(cfg.base_dir), "Wrong path, please check cfg.base_dir!"


def filter_mp3_files(filenames):
    mp3files = []
    for filename in filenames:
        if fnmatch.fnmatch(filename, "*.mp3"):
            mp3files.append(filename)
    return mp3files


class MP3dir(object):
    def __init__(self, cfg, dirpath, filenames):
        self.cfg = cfg
        self.dirpath = dirpath
        self.filenames = filenames

    def get_last_mtime(self):
        """ returns the newest modification timestamp """
        last_mtime = 0
        for filename in self.filenames:
            current_mtime = os.path.getmtime(os.path.join(self.dirpath, filename))
            if current_mtime > last_mtime:
                last_mtime = current_mtime
        return last_mtime

    def run_mp3gain(self):
        args = [mp3gain_filename(self.cfg)] + self.cfg.mp3gain_args + self.filenames
        process = subprocess.Popen(args, shell=False, cwd=self.dirpath)
        process.wait()

    def __repr__(self):
        return "MP3Dir %s mp3s in %s" % (len(self.filenames), self.dirpath)


def read_dirs(cfg):
    """
    Create a dict with the file information.
    The key is the newest timestamp of all containing mp3 files.
    The value is a list of MP3dir() instances.
    """
    print "read %s" % cfg.base_dir
    dircount = 0
    mp3count = 0
    dirinfo = {}
    time_threshold = time.time() + 0.01
    for dirpath, dirnames, filenames in os.walk(cfg.base_dir):
        dircount += 1
        mp3_files = filter_mp3_files(filenames)
        mp3count += len(mp3_files)
        if time.time() > time_threshold:
            time_threshold = time.time() + 0.01
            sys.stdout.write("\r%s dirs %s mp3 files readed...      " % (dircount, mp3count))

        if not mp3_files:
            continue

        mp3dir = MP3dir(cfg, dirpath, mp3_files)

        last_mtime = mp3dir.get_last_mtime()
        if last_mtime not in dirinfo:
            dirinfo[last_mtime] = []

        dirinfo[last_mtime].append(mp3dir)

    return dirinfo


def mp3gain(dirinfo):
    """
    run mp3gain from the newest timestamp to the oldest.
    """
    total_mp3_count = 0
    for mp3dirs in dirinfo.values():
        for mp3dir in mp3dirs:
            total_mp3_count += len(mp3dir.filenames)

    start_time = time.time()
    current_mp3_count = 0
    for timestamp, mp3dirs in sorted(dirinfo.iteritems(), reverse=True):
        for mp3dir in mp3dirs:
            print "_" * 79
            print mp3dir
            print

            mp3dir.run_mp3gain() # process all mp3 in the current dir
            print
            print "-" * 79

            current_mp3_count += len(mp3dir.filenames)

            elapsed = float(time.time() - start_time) # Vergangene Zeit
            estimated = elapsed / current_mp3_count * total_mp3_count # Geschätzte Zeit

            print(
                "%(current)i/%(total)i MP3s"
                " - %(percent).1f%%"
                " - current: %(elapsed)s"
                " - total: %(estimated)s"
                " - remain: %(remain)s"
            ) % {
                "current"  : current_mp3_count,
                "total"    : total_mp3_count,
                "percent"  : round(float(current_mp3_count) / total_mp3_count * 100.0, 2),
                "elapsed"  : human_time(elapsed),
                "estimated": human_time(estimated),
                "remain"   : human_time(estimated - elapsed),
            }




def main(cfg):
    check(cfg)
    dirinfo = read_dirs(cfg)
    if cfg.debug:
        pprint.pprint(dirinfo)
    mp3gain(dirinfo)

    print "--- END ---"


if __name__ == "__main__":
    cfg = Config
    cfg.debug = True
    cfg.base_dir = os.path.expanduser("~/servershare/MP3z/")
    main(cfg)
