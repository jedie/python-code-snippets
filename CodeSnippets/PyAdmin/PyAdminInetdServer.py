#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.2"



## Revisions-History
# v0.0.2
#   - es werden Einträge in die "syslog" vorgenommen
# v0.0.1
#   - Erste Version


import os, sys, socket, urllib, syslog

#~ sys.stdin.readline()
#~ print "HTTP/1.1 200 OK"
#~ print "Content-Type: text/plain\n"

# wird per inetd Aufgerufen -> der Aktuelle Pfad ist dabei \
# somit wird in's PyAdmin-Verz gewechselt
PyAdmin_root_dir = os.path.split(__file__)[0]
os.chdir( PyAdmin_root_dir )

# Ausgelagerte .py-Dateien in den Pfad aufnehmen
sys.path.append( os.path.join( PyAdmin_root_dir, "routines" ) )

import config, CGIdata

def debug( *txt ):
    txt = " ".join( [str(i) for i in txt] )
    print "HTTP/1.1 200 OK"
    print "Content-Type: text/html\n"
    print "<pre>"
    print txt

#~ debug("OK")

class inetdServer:
    """
    __init__        - Startet die abarbeitung eines requests
    read_config()   - Konfiguration einlesen
    parse_request() - Erste zeile von stdin zerlegen und überprüfen, setzten von absolut_path
        |-> verify_client_IP()       - Checkt ob die IP-Adresse der Anfrage in 'AllowIPs' vorhanden ist
        `-> CGIdata.parse_GET_data() - GET-Daten aus der URL speichern
    do_request()    - "unterscheidet, welche Art von request vorliegt
        |-> Menü wird Aufgebaut
        |-> start_module()  - Modul wird gestartet
        `-> send_file()     - sendet Dateien direkt an den Browser, wenn sie in 'extensions_map' vorkommen
    """

    # Dateitypen die ohne weitere Überprüfung per request
    # zum Client geschoben werden...
    extensions_map = {
        ".html" : "text/html",
        ".htm"  : "text/html",
        ".png"  : "image/png",
        ".jpg"  : "image/jpeg",
        ".js"   : "text/javascript",
        ".css"  : "text/css"
        }

    def __init__( self ):
        self.AllowIPs = ""
        self.IP = "0.0.0.0"

        self.CGIdata       = CGIdata.CGI_data_Parser()
        self.EnvironData   = CGIdata.environ_data_Parser()

        self.read_config()
        self.parse_request()
        self.do_request()

    def do_request( self ):
        """
        unterscheidet, welche Art von request vorliegt:
            - erster Aufruf nur mit "/" -> Menü wird ausgegeben
            - Modul wird aufgerufen
            - Datei (z.B. .css, .jpg) wurde angefordert
        """
        #~ debug("OK")
        if self.relativ_path == "/":
            Modulename = "SystemInfo"
        else:
            Modulename = self.absolut_path.split("?",1)[0] # Evtl. vorhandene GET-Daten wegschneiden
            head, Modulename = os.path.split( Modulename )

        if Modulename in self.AllowModules:
            self.start_module( Modulename )

        if not os.path.isfile( self.absolut_path ):
            self.error(404, "File [%s] not found" % self.absolut_path)
        else:
            self.send_file()

    def start_module( self, Modulename ):
        "Ein Modul wurde aufgerufen, welches jetzt 'gestartet' wird"

        syslog.syslog( syslog.LOG_NOTICE, "PyAdmin - %s call Module [%s]" % (self.IP, Modulename) )

        # CGI-Daten verarbeiten
        self.parseCGIdata()

        # Modul importieren
        mod = __import__( "modules." + Modulename, globals(), locals(), [ Modulename ] )

        # CGI-Daten an Modul "übermitteln"
        mod.CGIdata = self.CGIdata.get_data()
        # Das Modul aktivieren
        mod.inetd_start()
        sys.exit(0)

    def parseCGIdata( self ):
        """
        liest alle Daten von stdin ein.
        Dabei werden diese in folgende Module abgespeichert:
        self.CGIdata       = CGIdata.CGI_data_Parser()
        self.EnvironData   = CGIdata.environ_data_Parser()
        """
        for i in xrange(20):
            line = sys.stdin.readline()
            if line == "\r\n": break

            self.EnvironData.parse( line )

            if "content-length" in line.lower():
                self.CGIdata.content_length( line )

        self.CGIdata.parse_POST_data()

        #~ print "\n*** CGI-daten ***"
        #~ for k,v in self.CGIdata.get_data().iteritems(): print k,":",v
        #~ print "\n*** Environ-Data ***"
        #~ for k,v in self.EnvironData.get_data().iteritems(): print k,":",v
        #~ print

    def send_file( self ):
        "sendet Dateien direkt an den Browser, wenn sie in 'extensions_map' vorkommen"
        ctype = self.guess_type( self.absolut_path )
        #~ debug( ctype )
        if ctype == False:
            #~ debug( self.extensions_map.keys() )
            self.error( 999, "Fehler! %s " % self.absolut_path )

        if ctype.startswith('text/'):
            mode = 'r'
        else:
            mode = 'rb'
        try:
            f = file( self.absolut_path, mode)
        except IOError:
            self.error(404, "File [%s] not found" % file)

        print 'Content-Length: ' + str(os.fstat(f.fileno())[6])
        print 'Content-Type: %s\n' % ctype

        # In Blöcken, die Datei rausprinten...
        while True:
            data = f.read(8192)
            if not data:
                break
            sys.stdout.write(data)

        f.close()
        sys.exit()

    def guess_type( self, request_file ):
        name, ext = os.path.splitext( request_file )
        ext = ext.lower()
        #~ debug( ext )
        if ext in self.extensions_map.keys():
            return self.extensions_map[ext]
        return False

    def read_config( self ):
        "Server Konfiguration lesen"
        cfg = config.Parser()
        cfg.set_section("Server")
        self.AllowIPs        = cfg.get( "AllowIPs", "list" )
        self.AllowModules    = cfg.get( "AllowModules", "list" )

        #~ AllowIPs = AllowIPs.split(",")
        #~ self.AllowIPs = [IP.strip() for IP in AllowIPs]

    def error( self, code, message ):
        "Fehler, wobei der Request abgebrochen wird"
        self.send_error( code, message )
        sys.exit(0)

    def send_error( self, code, message=None ):
        "Fehlermeldung rausschreiben"
        print "HTTP/1.1 %s %s" % ( code, message )
        print "Content-Type: text/html\n"
        print "<h2>Server error<h2>"
        print "<h1>%s - %s</h1>"  % (code, message)
        print "<hr>"
        print __file__.rsplit("/",1)[-1],"-", " ".join( os.uname() )

    def verify_client_IP( self ):
        "Checkt ob die IP-Adresse der Anfrage in 'AllowIPs' vorhanden ist"
        def check_ip(mask, IP):
            mask = mask.split(".")
            IP = IP.split(".")
            for mask_part, ip_part in zip(mask, IP):
                if mask_part != ip_part and mask_part != '*':
                    return False
            return True

        client = socket.fromfd(sys.stdin.fileno(), socket.AF_INET, socket.SOCK_STREAM )
        self.IP, Port = client.getsockname()

        for mask in self.AllowIPs:
            if check_ip(mask, self.IP):
                return

        syslog.syslog( syslog.LOG_ALERT, "PyAdmin IP [%s] not allowed!!!" % self.IP )

        # Beugt DOS Attacken vor, in dem die Rückmeldung verzögert und
        # somit CPU-Zeit freigegeben wird.
        from time import sleep
        sleep(1)

        self.error( 530, "IP [%s] not allowed" % self.IP)


    def parse_request( self ):
        "Erste zeile von stdin zerlegen und überprüfen, setzten von absolut_path"
        Post_line = sys.stdin.readline()

        self.verify_client_IP()

        Post_line = Post_line.split(" ",2)

        if len(Post_line) != 3:
            self.error( 500, "Internal Server Error: Bad Request!" )

        [command, path, version] = Post_line

        if version[:5] != 'HTTP/':
            self.error( 400, "Bad request version (%r)" % version )

        # GET-Daten aus der URL speichern
        self.CGIdata.parse_GET_data( path )

        self.path = urllib.unquote(path)
        self.relativ_path = os.path.normpath( self.path )
        self.absolut_path = self.translate_path( self.path )

        print "HTTP/1.1 200 OK"

    def translate_path(self, path):
        """
        Umwandeln des Request-Path (angeforderte URL) zum Absoluten
        """

        words = path.split('/')
        path = PyAdmin_root_dir
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path


if __name__ == "__main__":
    inetdServer()