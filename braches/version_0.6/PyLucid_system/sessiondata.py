#!/usr/bin/python
# -*- coding: UTF-8 -*-



__version__ = "v0.0.6"

__history__ = """
v0.0.6

v0.0.5
    - Fehlerabfrage bei convert_types() erweitert
v0.0.4
    - detect_page() zur index.py verschoben
v0.0.3
    - Mehrfach connection vermieden.
v0.0.2
    - Die Daten werden nun schon mal vorverarbeitet
    - os.environ['QUERY_STRING'] wird mit urllib.unquote() verarbeitet
v0.0.1
    - erste Version
"""


# Python-Basis Module einbinden
import os, cgi, urllib

# PyLucid Module
import config

if config.system.page_msg_debug:
    import inspect

from socket import getfqdn

#~ from config import dbconf


# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"

import sys

class CGIdata:
    """
    Wertet die POST- und GET-Daten aus.
    Macht sich als dict verfügbar.
    Stellt fest, welche Seite abgefunden werden soll
    """
    def __init__( self, PyLucid ):
        """
        CGIdata ist eine abgeleitetes Dictionary und kann
        somit wie ein Dict angesprochen werden.
        """
        self.page_msg   = PyLucid["page_msg"]

        #~ self.page_msg( "TEST*****" )

        self.data = {} # Dict in dem die CGIdaten gespeichert werden

        self.get_CGIdata() # CGI-Daten ermitteln

        self.convert_types()

        self.get_client_info()

    def get_CGIdata( self ):
        """
        sammelt POST und GET Daten zusammen
        Er wird zuerst cgi.FieldStorage abgefragt und dann erst den QUERY_STRING, weil
        cgi.FieldStorage automatisch ein urllib.unquote() durchführt, aber die Original
        Daten gebraucht werden, die im QUERY_STRING noch drin stecken.
        Das ist wichtig für Seitennamen mit "Sonderzeichen" wie "/" ;)

        Normalerweise reicht ein cgi.FieldStorage( keep_blank_values=1 ) und die
        os.environ['QUERY_STRING'] Auswertung könnte man sich sparen. Aber das
        ganze funktioniert nicht mit Python v2.2.1 :( Also wird's doch umständlich
        gemacht ;)
        """

        if os.environ.has_key("CONTENT_LENGTH"):
            # Ist nur vorhanden, wenn der Client POST Daten schickt.
            length = int(os.environ["CONTENT_LENGTH"])
            if length>65534:
                print "Content-type: text/html; charset=utf-8\r\n"
                print "<h1>Error: Too much POST/GET content!</h1>"
                print "Content length = %s" % length
                sys.exit()
            #~ else:
                #~ self.page_msg( "Content length = %s" % length )

            FieldStorageData = cgi.FieldStorage()

            # POST Daten auswerten
            for i in FieldStorageData.keys():
                self.data[i] = FieldStorageData.getvalue(i)

        if os.environ.has_key('QUERY_STRING'):
            # GET URL-Parameter parsen
            for item in os.environ['QUERY_STRING'].split("&"):
                size = len(item)
                if size>10000:
                    self.page_msg( "CGI Error, GET Parameter size overload: '%s...'" % item[:10])
                    continue

                item = item.split("=",1)
                if len(item)==1:
                    if item[0]!="":
                        self.data[ item[0] ] = ""
                else:
                    self.data[ item[0] ] = item[1]

        #~ self.page_msg( self.data )

    def convert_types( self ):
        """
        Versucht Zahlen von str nach int zu convertieren
        """
        for k,v in self.data.iteritems():
            try:
                self.data[k] = int( v )
            except:
                pass


    def get_client_info( self ):
        """
        Client Informationen festhalten. Ist u.a. für's SQL-logging interessant.
        """
        if not os.environ.has_key("REMOTE_ADDR"):
            self.data["client_ip"] = "unknown"
            self.data["client_domain"] = "unknown"
            return

        self.data["client_ip"] = os.environ["REMOTE_ADDR"]
        try:
            self.data["client_domain"] = getfqdn( self.data["client_ip"] )
        except Exception, e:
            self.data["client_domain"] = "unknown: '%s'" % e

    #______________________________________________________________________________
    # Methoden um an die Daten zu kommen ;)

    def __getitem__( self, key ):
        return self.data[key]

    def iteritems( self ):
        return self.data.iteritems()

    def __setitem__( self, key, value ):
        self.data[key] = value

    def has_key( self, key ):
        return self.data.has_key( key )

    def __str__( self ):
        return str( self.data )

    def keys( self ):
        return self.data.keys()

    def __len__( self ):
        return len( self.data )

    def get(self, key, default):
        return self.data.get(key, default)

    #______________________________________________________________________________

    def error( self, txt1, txt2="" ):
        print "Content-type: text/html\n"
        print "<h1>Error: %s</h1>" % txt1
        print txt2
        import sys
        sys.exit()

    def debug( self ):
        #~ print "Content-type: text/html\n"
        #~ print "<pre>"
        #~ for k,v in self.data.iteritems():
            #~ self.page_msg( "%s - %s" % (k,v) )
        #~ print cgi.FieldStorage( keep_blank_values=True )
        #~ print "REQUEST_URI:",os.environ["REQUEST_URI"]
        #~ print "</pre>"
        import cgi

        import inspect
        # PyLucid's page_msg nutzen
        self.page_msg( "-"*30 )
        self.page_msg(
            "CGIdata Debug (from '...%s' line %s):" % (inspect.stack()[1][1][-20:], inspect.stack()[1][2])
        )

        self.page_msg( "-"*30 )
        for k,v in self.data.iteritems():
            self.page_msg( "%s - %s" % ( k, cgi.escape(str(v)) ) )
        self.page_msg( "FieldStorage:", cgi.FieldStorage( keep_blank_values=True ) )
        try:
            self.page_msg( 'os.environ["QUERY_STRING"]:', os.environ['QUERY_STRING'] )
        except:
            pass
        try:
            self.page_msg( 'os.environ["REQUEST_URI"]:', os.environ["REQUEST_URI"] )
        except:
            pass
        try:
            self.page_msg( 'os.environ["CONTENT_LENGTH"]:', os.environ["CONTENT_LENGTH"] )
        except:
            pass
        self.page_msg( "-"*30 )



##_______________________________________________________________________________________




class page_msg:
    """
    Kleine Klasse um die Seiten-Nachrichten zu verwalten
    page_msg wird in index.py den PyLucid-Objekten hinzugefugt.
    mit PyLucid["page_msg"]( "Eine neue Nachrichtenzeile" ) wird Zeile
    für Zeile Nachrichten eingefügt.
    Die Nachrichten werden ganz zum Schluß in der index.py in die
    generierten Seite eingeblendet. Dazu dient der Tag <lucidTag:page_msg/>
    """
    def __init__( self ):
        if config.system.page_msg_debug:
            self.data = "<p>[config.system.page_msg_debug = True!]</p>"
        else:
            self.data = ""

    def __call__( self, *msg ):
        """ Fügt eine neue Zeile mit einer Nachricht hinzu """
        if config.system.page_msg_debug:
            # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
            filename = inspect.stack()[1][1].split("/")[-1][-20:]
            fileinfo = "%-20s line %3s: " % (filename, inspect.stack()[1][2] )
            self.data += fileinfo.replace(" ","&nbsp;")

        self.data += "%s <br />\n" % " ".join( [str(i) for i in msg] )

    def write( self, *msg ):
        self.__call__( *msg )


    def get(self):
        if self.data != "":
            # Nachricht vorhanden -> wird eingeblendet
            return '<fieldset id="page_msg"><legend>page message</legend>%s</fieldset>' % self.data
        else:
            return ""










if __name__ == "__main__":
    page_name = "/Programmieren/Python/PyLucid"
    #~ page_name = "/Programmieren"
    page_name = page_name.split("/")[1:]
    #~ for name in page_name:

    print page_name












