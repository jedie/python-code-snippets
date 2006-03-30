#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyDown CGI-Handler für Apache

Führt PyDown als CGI aus.
Dies ist die "Start-Datei" die per URL aufgerufen werden muß!
Nur diese Datei benötigt Ausführungsrechte!
"""

#~ print "Content-type: text/html; charset=utf-8\r\n"
#~ import cgitb;cgitb.enable()


try:
    from colubrid.server import CGIServer
    from colubrid.debug import DebuggedApplication
except ImportError, e:
    print "Content-type: text/plain; charset=utf-8\r\n"
    print "<h1>Colubrid-WSGI-Implementation, Import Error: %s</h1>" % s
    print "Download at: http://wsgiarea.pocoo.org/colubrid/"
    import sys
    sys.exit()


if __name__ == "__main__":
    app = DebuggedApplication('PyDown_config:app')
    CGIServer(app).run()

