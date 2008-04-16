#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    mp3val.py
    ~~~~~~~~~

    A script for checking all mp3 recusive with mp3val:
        http://mp3val.sourceforge.net
        http://sourceforge.net/projects/mp3val
    MP3val licensed under the terms of the GNU General Public License

    Use the log file function from mp3val to skip directories how doesn't
    contains new mp3 files, how hasn't been checked in the past.

    using
    ~~~~~
    You can use the commandline interface like:
        python mp3val.py --help

    Use a small dispatcher file like this one:
    --------------------------------------------------------------------------
        #!/usr/bin/env python
        # -*- coding: utf-8 -*-

        import sys
        sys.path.insert(0, "c:\\path\\to\\mp3val_dir\\")

        from mp3val import Config, main

        Config.mp3val_path = "c:\\path\\to\\mp3val_exe_file\\"
        Config.verbose = False

        main(mp3_dir="c:\\the\\mp3s\\")

        raw_input("ENTER") # If you start it with the mouse ;)
    --------------------------------------------------------------------------
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__version__ = "SVN $Rev: $"

import sys, os, subprocess, time, optparse


print "\n%s %s - %s - by www.jensdiemer.de" % (
    os.path.basename(__file__), __version__.replace("$", ""), __license__
)
print "-"*79


class Config(object):
    """
    Contains the configurations.
    """
    mp3val_path = ""
    verbose = False
    log_file_name = "mp3val.log"

CFG = Config()



def mp3val_filename():
    filename = os.path.join(CFG.mp3val_path, "mp3val.exe")
    return filename


def run_mp3val(args):
    filename = mp3val_filename()
    cmd = [filename] + args
    if CFG.verbose:
        print " ".join(cmd)
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    process.wait()
    return process


def check(mp3_dir):
    """
    check if mp3val.exe exist and if MP3_DIR is a existing directory.
    """
    process = run_mp3val(["-v"])
    if process.returncode != 0:
        filename = mp3val_filename()
        print "Error:"
        print "\t'%s' not found." % filename
        print "\tUse -p PATH to specify the path to mp3val.exe"
        print "\t(Download from: http://mp3val.sourceforge.net)"
        if CFG.verbose:
            print process.stderr.read()
            print process.stdout.read()
        sys.exit(1)

    assert os.path.isdir(mp3_dir), "Wrong path, please check MP3_DIR!"

    filename = mp3val_filename()
    assert os.path.isfile(filename), "mp3val not found: '%s'" % filename


def mp3val_file(file_path):
    """
    Use mp3val for the given directory (...file_path\*.mp3)
    """
    mp3_path = os.path.join(file_path, "*.mp3")
    log_file_name = os.path.join(file_path, CFG.log_file_name)

    cmd = [mp3_path, "-l%s" % log_file_name, "-f"]
    process = run_mp3val(cmd)
    if process.returncode != 0:
        print "subprocess Error, Return code:", process.returncode

    print process.stderr.read()
    print process.stdout.read()


def filter_mp3s(filenames):
    """
    returns a list contains only mp3 files.
    """
    mp3_list = []
    for filename in filenames:
        if filename.endswith(".mp3"):
            mp3_list.append(filename)
    return mp3_list

def get_checked_files_info(file_path):
    """
    returns a list of all filenames from mp3val.log
    """
    log_file = os.path.join(file_path, CFG.log_file_name)
    if not os.path.isfile(log_file):
        return []

    f = file(log_file, "r")

    checked_files = []
    for line in f:
        filename = line.split('"',2)[1]
        if not filename in checked_files:
            checked_files.append(filename)
    return checked_files


def needs_check(checked_files, file_path, mp3_list):
    """
    returns True if one mp3 files is not in the checked_files list.
    """
    for filename in mp3_list:
        path = os.path.join(file_path, filename)
        if not path in checked_files:
            return True
    return False


def mp3val_dir(mp3_dir):
    """
    use mp3val for all mp3 files (recusive in path)
    """
    count = 0
    start_time = time.time()
    time_threshold = int(start_time)
    for file_path, _, filenames in os.walk(mp3_dir):
        mp3_list = filter_mp3s(filenames)
        if not mp3_list:
            if CFG.verbose:
                print "No mp3 file in '%s', skip." % file_path
            continue

        current_time = int(time.time())
        if current_time > time_threshold:
            # alive info every second
            time_threshold = current_time
            sys.stdout.write(".")

        count += 1

        checked_files = get_checked_files_info(file_path)
        #~ print checked_files
        if not needs_check(checked_files, file_path, mp3_list):
            if CFG.verbose:
                print "Skip '%s' (all files been check in the past)" % (
                    file_path
                )
            continue

        print
        print "_"*79
        print ">>> %s - %s" % (count, file_path)

        mp3val_file(file_path)


def main(mp3_dir):
    """
    The main function
    """
    check(mp3_dir)
    mp3val_dir(mp3_dir)


def cli():
    """
    commandline interface
    """
    opt_parser = optparse.OptionParser(usage = "%prog MP3_DIR")
    opt_parser.add_option(
        "-v",
        dest    = "verbose",
        action  = "store_true",
        help    = "CFG.verbose output"
    )
    opt_parser.add_option(
        "-p",
        dest    = "mp3val_path",
        default = "",
        action  = "store",
        metavar = "PATH",
        help    = "the path to mp3val.exe, if not in the same directory."
                  " (only the path, without filename)"
    )

    options, args = opt_parser.parse_args()

    if len(args) != 1:
        print "No MP3_DIR specified!\n"
        opt_parser.print_help()
        sys.exit()

    CFG.verbose = options.verbose
    CFG.mp3val_path = options.mp3val_path

    mp3_dir = args[0]
    main(mp3_dir)


if __name__ == "__main__":
    cli()