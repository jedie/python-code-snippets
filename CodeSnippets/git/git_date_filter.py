#!/usr/bin/env python
# coding: utf-8

"""
    git filter to change committer date in version info file.
    
    more info in README:
    https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/#readme
    
    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
    :homepage: https://github.com/jedie/python-code-snippets/tree/master/CodeSnippets/git/
"""

import sys
import os
import subprocess
import time
import re

SMUDGE = "smudge"
CLEAN = "clean"
CLEAN_DATE_STRING = "$date$"
SMUDGE_DATE_STRING = "$date:%s$"
SMUDGE_DATE_PREFIX = "$date:"
SMUDGE_DATE_REGEX = re.compile(r"(\$date:.*?\$)")



def _error(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    sys.exit(1)

def get_commit_timestamp(path=None, format="%m%d"):
    if path is None:
        path = os.path.abspath(os.path.dirname(__file__))

    try:
        process = subprocess.Popen(
            # %ct: committer date, UNIX timestamp  
            ["/usr/bin/git", "log", "--pretty=format:%ct", "-1", "HEAD"],
            shell=False, cwd=path,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except Exception, err:
        return _error("Can't get git hash: %s" % err)

    process.wait()
    returncode = process.returncode
    if returncode != 0:
        return _error(
            "Can't get git hash, returncode was: %r"
            " - git stdout: %r"
            " - git stderr: %r"
            % (returncode, process.stdout.readline(), process.stderr.readline())
        )

    output = process.stdout.readline().strip()
    try:
        timestamp = int(output)
    except Exception, err:
        return _error("git log output is not a number, output was: %r" % output)

    try:
        return time.strftime(format, time.gmtime(timestamp))
    except Exception, err:
        return _error("can't convert %r to time string: %s" % (timestamp, err))


def smudge():
    commit_timestamp = get_commit_timestamp()
    for line in sys.stdin:
        if CLEAN_DATE_STRING in line:
            line = line.replace(CLEAN_DATE_STRING, SMUDGE_DATE_STRING % commit_timestamp)
        sys.stdout.write(line)


def clean():
    """
    >>> SMUDGE_DATE_REGEX.sub(CLEAN_DATE_STRING, 'foo = "$date:123.456.789$" # bar')
    'foo = "$date$" # bar'
    """
    for line in sys.stdin:
        if SMUDGE_DATE_PREFIX in line:
            line = SMUDGE_DATE_REGEX.sub(CLEAN_DATE_STRING, line)
        sys.stdout.write(line)


if __name__ == "__main__":
#    import doctest
#    print doctest.testmod()
#    sys.exit()

    if len(sys.argv) < 2:
        _error("Error: missing commandline parameters!")

    if sys.argv[1] == SMUDGE:
        smudge()
    elif sys.argv[1] == CLEAN:
        clean()
    else:
        _error("Error: first argument must be %s or %s" % (SMUDGE, CLEAN))
