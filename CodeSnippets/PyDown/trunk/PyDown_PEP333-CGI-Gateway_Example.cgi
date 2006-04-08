#!D:\python\python24\python.exe
# -*- coding: UTF-8 -*-

"""
PyDown CGI-Handler für Apache

Führt PyDown als CGI aus.
Dies ist die "Start-Datei" die per URL aufgerufen werden muß!
Nur diese Datei benötigt Ausführungsrechte!
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\nHardcore Debug:"
#~ import cgitb;cgitb.enable()


try:
    from colubrid.debug import DebuggedApplication
except ImportError, e:
    import sys
    msg = "Content-type: text/html; charset=utf-8\r\n\r\n"
    msg += "<h1>Colubrid import error: %s</h1>" % e
    msg += "Download at: http://wsgiarea.pocoo.org/colubrid/"
    sys.stdout.write(msg)
    sys.stderr.write(msg)
    sys.exit()

from PyDown import PEP333_WSGI_CGIServer

if __name__ == "__main__":
    app = DebuggedApplication('PyDown_config:app')
    PEP333_WSGI_CGIServer.run_with_cgi(app)



