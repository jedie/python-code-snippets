#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
TrueCrypt - brute force

Nützlich wenn man ein zusammengesetztes Password benutzt, man die Einzelteile
noch kennt, aber nicht mehr weiß wie die Reihenfolge ist ;)

Kann auch statt TrueCrypt jedes andere Kommandozeilen Programm benutzten.


WICHTIG:
    Der Pfad und die Parameter zum TrueCrypt Kommandozeilen Programm müßen
    angepasst werden!!!


used the combine method by Fritz Cizmarov alias Dookie
url: http://www.python-forum.de/topic-1812.html
"""

__author__      = "Jens Diemer (http://www.jensdiemer.de)"
__url__         = "http://svn.pylucid.net/pylucid/CodeSnippets/"
__license__     = "GNU General Public License (GPL)"


import sys, subprocess, time


class BruteForcer:
    def __init__(self, words, minlen, maxlen, command):
        # Anzahl der Kombinationen ermitteln
        count = self.count(words, minlen, maxlen)

        start_time = time_threshold = int(time.time())
        for pos, bin in enumerate(self.combine2(words, minlen, maxlen)):
            bin = "".join(bin)

            current_time = int(time.time())
            if current_time > time_threshold:
                elapsed = float(current_time-start_time)    # Vergangene Zeit
                estimated = elapsed / (pos+1) * count         # Geschäzte Zeit

                if estimated>60:
                    time_info = "%.1f/%.1fmin" % (elapsed/60, estimated/60)
                else:
                    time_info = "%.0f/%.1fsec" % (elapsed, estimated)

                sys.stdout.write("\r")
                sys.stdout.write(
                    "tested %i password from %i - %s          " % (
                        pos+1, count, time_info
                    )
                )
                time_threshold = current_time

            returncode = self.cmd(command % bin)
            if returncode == 0:
                print
                print "Richtige Passwort gefunden!!!"
                print ">>>%s<<<" % bin
                sys.exit()

        print
        print "Passwort nicht gefunden :("


    def count(self, iterable, minlen, maxlen):
        """ Liefert die Anzahl der Kombinationen zurück """
        count = 0
        l = len(iterable)
        for n in xrange(minlen, maxlen+1):
            count += l ** n

        return count


    def combine2(self, iterable, minlen, maxlen):
        """
        Erzeugt alle Kombinationen der Elemente in iterable
        mit der Länge von >minlen< bin >maxlen<
        """
        for n in xrange(minlen, maxlen+1):
            for bin in self.combine(iterable, n):
                yield bin

        raise StopIteration


    def combine(self, iterable, n):
        """
        Erzeugt alle Kombinationen der Elemente in iterable mit der Länge n
        """
        iters = [iter(iterable) for i in xrange(n)] # Liste mit Iteratoren
        liste = [it.next() for it in iters]         # Liste mit 1. Kombination

        while True:
            yield tuple(liste) # Wichtig weil liste mutable ist !!!
            for i in xrange(n-1,-1,-1): # Stellen weiterschalten
                try:
                    liste[i] = iters[i].next()
                    break # alles OK, kein Ueberlauf, naechstes Wort bereit
                except StopIteration: # Ueberlauf
                    iters[i] = iter(iterable)  # Iterator zuruecksetzen
                    liste[i] = iters[i].next() # Stelle zuruecksetzen
                    continue # weiter mit naechster Stelle
            else: # alle Stellen hatten einen Ueberlauf
                raise StopIteration # Stop, alle Kombinationen sind durch


    def cmd(self, command):
        """
        Führt den Befehl in der shell aus und liefert den Rückgabecode zurück
        """
        # stderr auch lesen:
        process = subprocess.Popen(
            command, shell=True,
            #~ stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # warten, bis der gestartete Prozess zu Ende ist
        process.wait()

        # die Standardausgabe des Prozesses ausgeben
        #~ print process.stdout.read()
        # die Fehlerausgabe (sofern vorhanden) anzeigen
        #~ print process.stderr.read()

        # den Rückgabewert des Prozesses ausgeben
        # ist 0 wenn das Programm problemlos durchgelaufen ist
        return process.returncode



BruteForcer(
    words = (
        "syllable","part","lot","component","fragment","brick"
    ),
    minlen = 2,
    maxlen = 4,
    command = (
        "C:\\TrueCrypt\\TrueCrypt.exe /auto /beep /quit /silent"
        " /password %s"
        " /keyfile C:\\ExampleKeyFile.dat"
        " /volume C:\\ExampleContainer.tc"
    )
)