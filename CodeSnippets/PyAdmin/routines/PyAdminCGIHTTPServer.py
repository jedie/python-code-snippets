#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.4"

#########
# History
# v0.0.4


import CGIHTTPServer, SocketServer, BaseHTTPServer
import os, sys, time, socket


import config

cfg = config.Parser()

cfg.set_section( "Server" )
ListenPort  = cfg.get( "ListenPort", "int" )
LogFile     = os.path.join( os.getcwd(), cfg.get( "LogFile" ) )
AllowIPs    = cfg.get( "AllowIPs" )
AllowIPs = AllowIPs.split(",")
AllowIPs = [IP.strip() for IP in AllowIPs]



class RedirectStdOut:
    def __init__( self, File, stdoutObj ):
        self.MyStdOut = stdoutObj
        self.File = File

    def write( self, *txt ):
        txt = " ".join([str(i) for i in txt])
        # Auf Konsole Ausgeben
        self.MyStdOut.write( txt )
        # In Log-Datei schreiben
        FileHandle = file( self.File, "a" )
        FileHandle.write( txt )
        FileHandle.close()


class MyRequestHandler( CGIHTTPServer.CGIHTTPRequestHandler ):
    "Modifizieren des Standart RequestHandlers"

    # Damit auch unter Linux, welches fork unterstützt, das Python-CGI-Skript
    # unter dem User ausgeführt wird, mit dem der CGIHTTPServer gestartet wurde
    # und nicht mit User nobody...
    have_fork = False
    have_popen2 = False
    have_popen3 = False

    def __init__( self, request, client_address, parent ):
        CGIHTTPServer.CGIHTTPRequestHandler.__init__( self, request, client_address, parent )
        #~ self.server_shutdown = False

    #~ def is_python(self, path):
        #~ """Test whether argument path is a Python script."""
        #~ print path
        #~ head, tail = os.path.splitext(path)
        #~ print tail.lower(), tail.lower() in (".py", ".pyw")
        #~ return tail.lower() in (".py", ".pyw")

    def is_cgi( self ):
        "Modifikation, sodas man im CGI-Verzeichnis ein Dir-Listing bekommt"
        path = self.path

        if path == "/__self__.kill()":
            raise KeyboardInterrupt, "*** Server über URL beendet ***"

        for x in self.cgi_directories:
            i = len(x)
            if path[:i] == x and (path[i+1:] and path[i] == '/'):
                self.cgi_info = path[:i], path[i+1:]
                return True
        return False




class MyThreadingServer( BaseHTTPServer.HTTPServer ):
#~ class MyThreadingServer( SocketServer.ThreadingTCPServer ):
    """
    Verbesserung des Standart Servers:
     - ermöglicht das abarbeiten mehrere Anfragen parallel (z.B. Download mehrere Dateien gleichzeitig)
     - Ermöglicht das einschränken des IP-Bereiches aus denen der Server Anfragen behandelt
    """
    allow_reuse_address = 1    # Seems to make sense in testing environment

    def __init__(self, server_address, request_handler, AllowIPs):
        #~ SocketServer.ThreadingTCPServer.__init__(self, server_address, request_handler)
        BaseHTTPServer.HTTPServer.__init__(self, server_address, request_handler)
        self.AllowIPs = [mask.split('.') for mask in AllowIPs]
        self.ServerLoop = True

    #~ def server_bind(self):
        #~ """Override server_bind to store the server name. (Parallele Anfragen)"""
        #~ SocketServer.ThreadingTCPServer.server_bind(self)
        #~ host, port = self.socket.getsockname()[:2]
        #~ self.server_name = socket.getfqdn(host)
        #~ self.server_port = port

    def verify_request(self, request, client_address):
        """Checkt ob die IP-Adresse der Anfrage in 'AllowIPs' vorhanden ist"""
        #~ print "request:",request
        #~ print dir(request)

        def check_ip(mask):
            for mask_part, ip_part in zip(mask, ip):
                if mask_part != ip_part and mask_part != '*':
                    return False
            return True

        ip = client_address[0].split('.')

        for mask in self.AllowIPs:
            if check_ip(mask):
                return True

        print "IP not allowed:", client_address

        # Beugt DOS Attacken vor, in dem die Rückmeldung verzögert und
        # somit CPU-Zeit freigegeben wird.
        time.sleep(1)

        return False

    def serve_forever(self):
        """Handle one request at a time until doomsday."""
        while self.ServerLoop:
            self.handle_request()

    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.

        The default is to print a traceback and continue.

        """
        print '-'*40

        import exceptions
        if sys.exc_type == exceptions.KeyboardInterrupt:
            print "Server wird beendet!"
            self.ServerLoop = False
            return

        # Normale Fehlerausgabe
        print 'Exception happened during processing of request from',
        print client_address
        import traceback
        traceback.print_exc() # XXX But this goes to stderr!
        print '-'*40




def ServerStart():
    # Ausgaben in Datei mitloggen:
    sys.stdout = RedirectStdOut( LogFile, sys.stdout )
    sys.stderr = RedirectStdOut( LogFile, sys.stderr )

    print "="*80

    # Umgebungsvariablen setzten, die man in CGI-Skripten abfragen kann und normalerweise
    # von einem echten WebServer automatisch gesetzt werden
    os.environ['DOCUMENT_ROOT']     = os.getcwd()
    #~ os.environ['HTTP_HOST']         = "localhost"

    # Liste aller Unetrverzeichnisse erzeugen, damit überall CGIs ausgeführt werden.
    print "Lese Verzeichnisbaum für CGI-Ausführung...",
    cgiVerz = "." # CGI's in jedem Pfad erlauben
    #~ cgi_directories = [os.path.normpath( os.sep + i[0] ) for i in os.walk(cgiVerz)]
    cgi_directories = ["/modules", "/routines"]
    print "OK",len(cgi_directories),"Verz. gefunden\n"
    #~ for i in cgi_directories: print i

    print "ROOT-Pfad .......................:", os.getcwd()
    print "Log-Datei .......................:", LogFile
    print "Starte CGI-HTTP-Server auf Port .:", ListenPort
    print "Zugelassener IP-Bereich .........:", AllowIPs
    print
    print "Seiten sind nun unter [http://localhost:%s] erreichbar!\n" % ListenPort

    # Leider versteht sich CGIHTTPServer nur auf HTTP v1.0, darin wird kein
    # ACCEPT_ENCODING behandelt :(
    #~ os.environ["HTTP_ACCEPT_ENCODING"] = "gzip"
    #~ os.environ["HTTP_ACCEPT_ENCODING"] = "deflate"
    os.environ["HTTP_ACCEPT_ENCODING"] = ""

    # Variablen in MyRequestHandler setzten:
    MyRequestHandler.cgi_directories    = cgi_directories

    httpd = MyThreadingServer( ("", ListenPort), MyRequestHandler, AllowIPs )

    print "*** Server gestartet ***"

    httpd.serve_forever()
    #~ while 1:
        #~ httpd.handle_request()





if __name__=="__main__":
    "Lokaler Test"
    os.chdir("..")

    cgiVerz = "." # CGI's in jedem Pfad erlauben
    ListenPort = 9000
    AllowIPs = ('127.0.0.1', '192.168.*.*')
    LogFile = "logs\\LogFile.txt"

    ServerStart( cgiVerz, ListenPort, AllowIPs, LogFile )


