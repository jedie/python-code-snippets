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
    from colubrid.debug import DebuggedApplication
except ImportError, e:
    import sys
    msg = "Content-type: text/html; charset=utf-8\r\n\r\n"
    msg += "<h1>Colubrid import error: %s</h1>" % e
    msg += "Download at: http://wsgiarea.pocoo.org/colubrid/"
    sys.stdout.write(msg)
    sys.stderr.write(msg)
    sys.exit()

try:
    from flup_server.fcgi import WSGIServer
except ImportError, e:
    import sys
    msg = "Content-type: text/html; charset=utf-8\r\n\r\n"
    msg += "<h1>flup_server import error: %s</h1>\n" % e
    msg += "<p>Download via SVN: http://svn.saddi.com/flup/trunk/flup/server<br />\n"
    msg += "Info: http://www.saddi.com/software/flup/</p>\n"
    sys.stdout.write(msg)
    sys.stderr.write(msg)
    sys.exit()

if __name__ == "__main__":
    app = DebuggedApplication('PyDown_config:app')
    WSGIServer(app).run()

