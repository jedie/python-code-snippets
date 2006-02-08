#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)


"""
subprocess with timeout
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.2"

__history__="""
v0.2
    - neu: def cmd() - vereinfachter Aufruf
v0.1
    - erste Version
"""


import os, sys, threading, subprocess, time, signal


class subprocessIO:
    def __init__( self ):
        self.stdout_data = ""

    def write( self, line ):
        self.stdout_data += line

    def flush( self ):
        pass

    def get( self ):
        return self.stdout_data


class subprocess2(threading.Thread):
    def __init__( self, command, cwd, stdoutObj, *args, **kw):
        threading.Thread.__init__(self,*args,**kw)
        self.command    = command
        self.cwd        = cwd
        self.stdoutObj  = stdoutObj

    def readOutData( self, readObj ):
        "Ausgaben vom subprocess ausgeben"
        while 1:
            line = readObj.readline()
            if line == "": break
            self.stdoutObj.write( line )

    def run(self):
        "Führt per subprocess einen den Befehl 'self.command' aus."
        #~ print "Starte '%s %s'..." % (self.cwd,self.command),

        # TESTEN:
        "stderr = subprocess.STDOUT"
        self.process = subprocess.Popen(
                self.command,
                cwd     = self.cwd,
                shell   = True,
                stdout  = subprocess.PIPE,
                stderr  = subprocess.PIPE
            )
        # Ausgaben auslesen
        self.readOutData( self.process.stdout )
        self.readOutData( self.process.stderr )

    def stop( self ):
        """
        Testet ob der Prozess noch läuft, wenn ja, wird er mit
        os.kill() (nur unter UNIX verfügbar!) abgebrochen.
        """
        if self.process.poll() != None:
            #~ print "Prozess ist schon beendet"
            return

        print "\nProzess abbrechen...",
        if os.name != "posix":
            print "\n>>> os.kill() nur unter UNIX verfügbar!"
            return
        os.kill( self.process.pid, signal.SIGQUIT )
        #~ print "OK"



class string_saver:
    def __init__( self ):
        self.data = ""
    def write( self, txt ):
        self.data += txt
    def get( self ):
        return self.data


def cmd( command, current_dir, process_timeout, stdoutObj="" ):
    if type(stdoutObj) == str:
        # Daten sollen als String zurÃ¼ck gegeben werden
        save_in_String = True
        stdoutObj = string_saver()
    else:
        # Daten werden zum stdoutObj geschrieben
        save_in_String = False

    MySubprocess = subprocess2( command, current_dir, stdoutObj )
    MySubprocess.start()                    # thread starten
    MySubprocess.join(process_timeout)      # ...laufen lassen...
    MySubprocess.stop()                     # Prozess evtl. abbrechen
    if save_in_String:
        # Daten sollen als String zurÃ¼ck gegeben werden
        return stdoutObj.get()
    else:
        MySubprocess.stdoutObj.flush()





if __name__=="__main__":
    from optparse import OptionParser
    OptParser = OptionParser()
    options, args = OptParser.parse_args()

    if len(args) != 0:
        # for-test-Schleife
        for i in xrange(10):
            print i
            sys.stdout.flush()
            time.sleep(0.2)
        print "for-test-Schleife abgelaufen!"
        sys.exit()


    class RedirectStdOut:
        def write( self, txt ):
            sys.stdout.write( txt )
        def flush( self ):
            print "Flush!"
            sys.stdout.flush()

    test=subprocess2(
        "python.exe %s test" % __file__,
        os.getcwd(),
        RedirectStdOut()
        )
    test.start()    # thread starten
    test.join(1)    # 1sek laufen lassen
    test.stop()     # Prozess abbrechen
    test.stdoutObj.flush()

    print "Fertig!"
