#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    subprocess with timeout
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__version__ = "SVN $Rev: $"


import os, subprocess, threading, signal

KILL_SIGNAL = signal.SIGKILL

class subprocess2(threading.Thread):
    """
    subprocess with a timeout

    Note: os.kill() doesn't exist under Windows!
    """
    def __init__(self, *args, **kwags):
        self.killed = None

        self.timeout = kwags.pop("timeout", 5)

        self.args = args
        self.kwags = kwags

        threading.Thread.__init__(self)

        self.start()
        self.join(self.timeout)
        self.stop()

    def run(self):
        """
        start child process and wait for terminate
        """
        self.process = subprocess.Popen(*self.args, **self.kwags)
        self.process.wait()
        if self.killed == None:
            # The process terminate and was not killed in the past
            self.killed = False

    def stop(self):
        """
        kill the child process if it's not terminated in the past
        """
        if self.killed == False:
            # process is terminate
            return
        else:
            # kill a running process
            self.killed = True
            os.kill(self.process.pid, KILL_SIGNAL)


if __name__ == "__main__":
    print "try 'ls'..."
    p = subprocess2("ls",
        stdout=subprocess.PIPE,
        shell=True, timeout = 1
    )
    print "returncode:", p.process.returncode
    print "killed:", p.killed
    print "stdout: %r" % p.process.stdout.read()

    print "-"*79

    print "start the python interpreter..."
    p = subprocess2("python",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout = 1
    )
    print "returncode:", p.process.returncode
    print "killed:", p.killed
    if not p.killed:
        # read only if process ended normaly, otherwise the read blocked!
        print "stdout: %r" % p.process.stdout.read()
        print "stderr: %r" % p.process.stderr.read()

    print "-"*79