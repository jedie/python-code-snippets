#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyDown fastCGI-Handler

Führt PyDown als fastCGI aus.

Brauch einen Handler-Eintrag in der .htaccess:
 >>> AddHandler fastcgi-script .fcg
s. http://httpd.apache.org/docs/2.0/mod/mod_mime.html#addhandler

Benötigt den WSGI-Server aus dem flup-Paket
per SVN: http://svn.saddi.com/flup/trunk/flup/server
Info: http://www.saddi.com/software/flup/
"""

try:
    from flup_server.fcgi import WSGIServer
except ImportError, e:
    import sys
    msg = "Content-type: text/plain; charset=utf-8\r\n"
    msg += "<h1>Colubrid-WSGI-Implementation, Import Error: %s</h1>\n" % s
    msg += "<p>Download via SVN: http://svn.saddi.com/flup/trunk/flup/server<br />\n"
    msg += "Info: http://www.saddi.com/software/flup/</p>\n"
    sys.stdout.write(msg)
    sys.stderr.write(msg)
    sys.exit()

from PyDown_config import app


if __name__ == "__main__":
    WSGIServer(app).run()

