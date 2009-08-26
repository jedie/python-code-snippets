#!/usr/bin/env python
# coding: utf-8

"""
    reniceall
    ~~~~~~~~~
    
    set a new nice level to all process threads.
    Usage e.g. (set all kvm threads to nice level 20):
        sudo python reniceall.py -n 20 kvm
    
    History
        v0.0.1 - first version
        
    :copyleft: 2009 by Jens Diemer.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import optparse
import subprocess
from pprint import pprint

__version__ = "0.0.1"

print "\n%s v%s (GNU General Public License v3 or above) - by www.jensdiemer.de\n" % (
    os.path.basename(__file__), __version__
)


def get_all_pid():
    cmd = ["ps", "-eTo", "spid,comm"]
    print "call:", " ".join(cmd)
    process = subprocess.Popen(args=cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
    )
    stderr = process.stderr.read()
    if stderr:
        print "--- stderr ouput: ---"
        print stderr
        print "---------------------"

    output = process.stdout.read()
    output_lines = output.strip().splitlines()[1:]
    result = {}
    for line in output_lines:
        line = line.strip()
        try:
            pid, process_name = line.split(" ", 1)
        except ValueError, err:
            print "Split output line error: %s" % err
            print "line: %r" % line
        else:
            if process_name not in result:
                result[process_name] = []
            result[process_name].append(pid)
    return result

def renice_pids(process_pids, nice_level):
    cmd = ["renice", str(nice_level), "-p"]
    cmd += process_pids
    print "call:", " ".join(cmd)
    subprocess.Popen(args=cmd)

def reniceall(process_name, nice_level):
    print("Set nice level to %r for all %r process threads.\n" % (nice_level, process_name))
    pid_dict = get_all_pid()
    #pprint(pid_dict)
    try:
        process_pids = pid_dict[process_name]
    except KeyError:
        print "Process %r is not running!" % process_name
        sys.exit(1)

    print "all pids from the process %r: %r" % (process_name, process_pids)
    renice_pids(process_pids, nice_level)


def parameter_error(msg="Options/parameter error."):
    print "%s\n" % msg
    parser.print_help()
    sys.exit()


if __name__ == "__main__":
#    reniceall(process_name="kvm", nice_level=20)
#    sys.exit()

    parser = optparse.OptionParser(usage="%prog [options] process_name")
    parser.add_option("-n", type="int", dest="nice_level", help="new nice level for the given process")
    options, args = parser.parse_args()

    if len(args) != 1:
        parameter_error()

    nice_level = options.nice_level
    if nice_level == None:
        parameter_error()

    process_name = args[0]

    reniceall(process_name, nice_level)

