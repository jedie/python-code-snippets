#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-


import os, sys, threading, subprocess, time, signal




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

    def get_process_obj( self ):
        return self.process

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






if __name__=="__main__":
    from optparse import OptionParser
    OptParser = OptionParser()
    options, args = OptParser.parse_args()

    if len(args) != 0:
        # for-test-Schleife
        for i in xrange(20):
            print i
            sys.stdout.flush()
            time.sleep(0.2)
        print "for-test-Schleife abgelaufen!"
        sys.exit()


    class RedirectStdOut:
        def write(self, txt):
            sys.stdout.write( txt )

    test=subprocess2(
        "python.exe %s test" % __file__,
        os.getcwd(),
        RedirectStdOut()
        )
    test.start()    # thread starten
    test.join(3)    # 1sek laufen lassen
    test.stop()     # Prozess abbrechen

    print "Fertig!"
