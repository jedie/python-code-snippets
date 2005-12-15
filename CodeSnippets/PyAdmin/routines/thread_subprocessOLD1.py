

import os, sys, threading, subprocess, time, signal



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


def readOutData( readObj ):
    "Ausgaben vom subprocess ausgeben"
    while 1:
        line = readObj.readline()
        if line == "": break
        sys.stdout.write( line )


class subprocess2(threading.Thread):
    def __init__( self, command, cwd, *args, **kw):
        threading.Thread.__init__(self,*args,**kw)
        self.command    = command
        self.cwd        = cwd

    def readOutData( self, readObj ):
        "Ausgaben vom subprocess ausgeben"
        while 1:
            line = readObj.readline()
            if line == "": break
            sys.stdout.write( line )

    def run(self):
        #~ "Führt per subprocess einen den Befehl 'self.command' aus."
        #~ print "Starte '%s'..." % self.command,
        #~ self.process =
        return subprocess.Popen(
                self.command,
                cwd     = self.cwd,
                shell   = True,
                stdout  = subprocess.PIPE,
                stderr  = subprocess.PIPE
            )
        #~ return self.process
        #~ print "OK"
        #~ print "Lese Ausgaben:"
        #~ print "-"*80
        #~ self.readOutData( self.process.stdout )
        #~ self.readOutData( self.process.stderr )
        #~ print "-"*80

    def get_process_obj( self ):
        return self.process

    def stop( self ):
        """
        Testet ob der Prozess noch läuft, wenn ja, wird er mit
        os.kill() (nur unter UNIX verfügbar!) abgebrochen.
        """
        if self.process.poll() != None:
            print "Prozess ist schon beendet"
            return

        print "Prozess abbrechen...",
        os.kill( self.process.pid, signal.SIGQUIT )
        print "OK"


if __name__=="__main__":
    test=subprocess2( "dir", "c:\\" )
    #~ test.start()    # thread starten
    process_obj = test.run()
    #~ process_obj = test.get_process_obj()
    readOutData( process_obj.stdout )
    test.join(3)    # 1sek laufen lassen
    test.stop()     # Prozess abbrechen

    print "Fertig!"
