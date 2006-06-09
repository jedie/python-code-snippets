#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
CSS in die CMS Seite einfügen
"""

__version__="0.2"

__history__="""
v0.2
    - Anpassung an PyLucid v0.7
    - NEU: nun können die CSS Daten als Link in die Seite eingefügt werden,
        dabei wird auch eine "Browsercache-Anfrage" berücksichtigt.
v0.1.0
    -  erste Version
"""

import sys, os, datetime
from colubrid import HttpResponse


from PyLucid.system.BaseModule import PyLucidBaseModule


class page_style(PyLucidBaseModule):

    #~ def __init__(self, *args, **kwargs):
        #~ super(page_style, self).__init__(*args, **kwargs)

    def lucidTag(self):
        cssTag = (
            '<link rel="stylesheet" type="text/css"'
            ' href="%sstylesheet.css" />\n'
        ) % self.URLs.actionLink("sendStyle")
        self.response.write(cssTag)

        # Schreibt den addCode-Tag, damit am Ende noch die CSS/JS Daten
        # von Modulen eingefügt werden können
        self.response.write(self.response.addCode.tag)

    def print_current_style(self):
        """
        CSS direkt in die Seite einfügen
        """
        self.response.write('<style type="text/css">')

        page_id = self.session["page_id"]
        getItems = ["content"]
        css = self.db.side_style_by_id(page_id, getItems)
        css = css["content"]
        self.response.write(css)

        self.response.write('</style>')

        # Schreibt den addCode-Tag, damit am Ende noch die CSS/JS Daten
        # von Modulen eingefügt werden können
        self.response.write(self.response.addCode.tag)

    def sendStyle(self, function_info):
        """
        Sendet das CSS als Datei, da in die Seite nur ein Link eingefügt, der
        jetzt "ausgeführt" wird.
        Dabei wird eine "Browsercache-Anfrage" berücksichtigt.
        """
        timeFormat = "%a, %d %b %Y %H:%M:%S GMT"

        # Ein "wirklich" frisches response-Object nehmen:
        response = HttpResponse()
        response.headers['Content-Type'] = 'text/css; charset=utf-8'
        response.headers['Connection'] = "Keep-Alive"

        page_id = self.session["page_id"]
        getItems = ["id", "content","lastupdatetime"]
        cssData = self.db.side_style_by_id(page_id, getItems)

        lastupdatetime = cssData["lastupdatetime"]
        lastModified = lastupdatetime.strftime(timeFormat)
        #~ print "lastModified:", lastModified

        # 604800Sec / 60Sec / 60Min / 24h = 7Tage ;)
        maxAge = 604800
        response.headers['Cache-Control'] = 'max-age=%s' % maxAge

        expires = lastupdatetime + datetime.timedelta(seconds=maxAge)
        expires = expires.strftime(timeFormat)
        #~ print "expires:", expires
        response.headers['Expires'] = expires

        # ID damit der Browser das Style eindeutige Identifizieren kann:
        eTag = '"style-%s"' % cssData["id"]
        response.headers['Etag'] = eTag

        # Chaching im Browser überprüfen:
        if "HTTP_IF_MODIFIED_SINCE" in self.environ and \
                                        "HTTP_IF_NONE_MATCH" in self.environ:
            # Der Browser fragt nach, ob es die Daten aus seinem Chache nehmen
            # soll.
            send_modified = self.environ["HTTP_IF_MODIFIED_SINCE"]
            send_eTag = self.environ["HTTP_IF_NONE_MATCH"]
            if send_eTag == eTag and send_modified == lastModified:
                # CSS Daten haben sich nicht geändert!
                response.status = 304 # HTTP/1.x 304 Not Modified
                return response

        # Die CSS Daten werden zum ersten mal gesendet oder diese haben
        # sich seit dem letzten Aufruf geändert.

        cssContent = cssData["content"]

        # Content-Length kann nur in UTF8 und nicht richtig in Unicode
        # ermittelt werden!!!
        cssContent = cssContent.encode("utf8")
        contentLen = len(cssContent)
        response.headers['Content-Length'] = '%s' % contentLen

        response.headers['Last-Modified'] = lastModified
        response.headers['Content-Transfer-Encoding'] = '8bit' #'binary'
        response.headers['Content-Type'] = \
            'text/css; charset=utf-8'

        response.write(cssContent)

        # force Windows input/output to binary
        if sys.platform == "win32":
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        return response







