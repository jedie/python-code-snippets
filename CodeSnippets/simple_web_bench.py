#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfacher Web-Seiten Preformance Test.

Ruft eine Webseite x-mal hintereinander in x-Threads gleichzeitig ab und
ermittelt die Durchschnittszeit.
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__     = "http://www.python-forum.de/topic-7447.html"

__version__ = "0.2"

__history__ = """
v0.2
    - Nun mehrer Anfragen gleichzeitig :)
v0.1
    - erste Version
"""



import sys, socket, urllib2, time, threading


timeout = 10

socket.setdefaulttimeout(timeout) # Geht erst ab Python 2.3



class Requester(object):
    def __init__(self, count, threads, delete=2, verbose=False):
        """
        count - Anzahl der Prüfungsrunden
        threads - Anzahl der gleichzeitigen Seitenabrufe
        delete - Gibt an wieviele der schlechtesten und besten Zeiten, für die
            errechnung des Durchnitts gelöscht werden.
        verbose - Mehr Ausgaben :)
        """
        self.count = count
        self.threads = threads
        self.delete = delete

        self.verbose = verbose

    def measuring(self, url):
        """
        Führt die Messung der >url< durch.
        """
        self.url = url

        self.response_times = []

        print
        print ">", url,

        try:
            self.count_requests()
        except (urllib2.URLError, RuntimeError), e:
            print "\nError:", e
            return

        if self.verbose:
            print
            print "min: %0.2fsec, max: %0.2fsec" % (
                min(self.response_times), max(self.response_times)
            )

        average = sum(self.response_times) / len(self.response_times)
        print ">>> average: %0.2fsec" % average,

        target_len = (self.count * self.threads) - (2*self.delete)

        if len(self.response_times) < target_len:
            print "- %d timeouts!(>%dsec)" % (
                (target_len - len(self.response_times)), timeout
            )
            print "Note: Values are not in average calculation!"
        else:
            print

        if self.verbose: print "-"*79

    def count_requests(self):
        """
        Startet die Prüfrunden x-mal (Anzahl: self.count)
        """
        if self.verbose:
            print "\nRequest %s times %s requests:" % (
                self.count, self.threads
            )

        for i in xrange(self.count):
            self.threading_request()
            if self.verbose:
                print

        if len(self.response_times) == 0:
            raise RuntimeError("No Request successfully! URL incorrectly?")

        print

        if self.verbose:
            print "delete %d min time(s) and delete %d max time(s)" % (
                self.delete, self.delete
            )

        if len(self.response_times) - (2*self.delete) <= 0:
            raise RuntimeError("Too few measured values!")

        for dummy in xrange(self.delete):
            # schnellsten Request löschen:
            self.response_times.remove(min(self.response_times))
            # langsamsten Request löschen:
            self.response_times.remove(max(self.response_times))



    def threading_request(self):
        """
        Führt eine Prüfrunde durch
        """
        #
        # Threads erzeugen.
        #
        threads = []
        for dummy in xrange(self.threads):
            threads.append(threading.Thread(target=self.request))
        #
        # Threads starten.
        #
        for thread in threads:
            thread.start()
        #
        # Auf alle Threads warten.
        #
        for thread in threads:
            thread.join()

    def request(self):
        """
        Ruft die Seite einmal ab und trägt die Zeit in self.response_times ein
        """
        start_time = time.time()

        try:
            f = urllib2.urlopen(self.url)
            sidecontent = f.read()
            f.close()
        except urllib2.URLError,e:
            if self.verbose:
                print "Error:", e
            else:
                sys.stdout.write("X")
        else:
            duration_time = time.time() - start_time

            if self.verbose:
                print "%0.2fs" % duration_time,
            else:
                sys.stdout.write(".")

            self.response_times.append(duration_time)


#~ verbose = True
verbose = False
r = Requester(count=5, threads=2, delete=3, verbose=verbose)
#~ r = Requester(count=15, threads=5, delete=3, verbose=verbose)

r.measuring("http://heise.de")
r.measuring("http://google.de")