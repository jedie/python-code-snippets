#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__     = "http://www.PyLucid.org"

__info__ = """<a href="%s" title="\
PyLucid - A OpenSource CMS in pure Python CGI by Jens Diemer">PyLucid</a>\
v0.7.0Alpha""" % __url__


debug = True
#~ debug = False



import cgi, urllib, os
import sys #Debug

from PyLucid.system.exceptions import *

# Colubrid
from colubrid import BaseApplication
from colubrid import HttpResponse

WSGIrequestKey = "colubrid.request"


import config # PyLucid Grundconfiguration

#__init__
from PyLucid.system import tools
from PyLucid.system import db
from PyLucid.system import URLs
from PyLucid.system import jinjaRenderer

# init2
from PyLucid.system import sessionhandling
from PyLucid.system import SQL_logging
from PyLucid.system import module_manager
from PyLucid.system import page_parser
from PyLucid.system import detect_page




class PyLucidApp(BaseApplication):
    """
    Klasse die die Programmlogik zusammenstellt
    """
    charset = 'utf-8'
    #~ slash_append = True
    slash_append = False

    def __init__(self, environ, start_response):
        super(PyLucidApp, self).__init__(environ, start_response)

        self.response = HttpResponse()

        self.environ        = environ

        self.request.runlevel = "init"
        self.request.log            = None
        self.request.render         = None
        self.request.session        = None
        self.request.module_manager = None

        # environ['PATH_INFO'] anpassen
        self.setup_path_info()

        # Tools
        tools.request       = self.request  # Request Objekt an tools übergeben
        tools.response      = self.response # Response Objekt an tools übergeben
        self.request.tools  = tools         # Tools an Request Objekt anhängen

        self.response.echo = tools.echo() # Echo Methode an response anhängen

        # Jinja-Context anhängen
        self.request.context = {}

        #~ self.request.jinjaRenderer = jinjaRenderer.jinjaRenderer(self.request)

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.request.page_msg = environ['PyLucid.page_msg']

        # Verwaltung für Einstellungen aus der Datenbank (Objekt aus der Middleware)
        self.request.preferences = environ['PyLucid.preferences']

        # Passt die verwendeten Pfade an.
        self.request.URLs = URLs.URLs(self.request)
        self.request.URLs.debug()

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.request.db = environ['PyLucid.database']
        self.request.db.connect(self.request.preferences)
        #~ self.request.db = db.db(self.request, self.response)
        self.request.db.page_msg = self.request.page_msg

        # Shorthands
        self.page_msg       = self.request.page_msg
        self.db             = self.request.db
        self.preferences    = self.request.preferences
        self.tools          = self.request.tools
        self.URLs           = self.request.URLs

    def setup_path_info(self):
        pathInfo = self.request.environ.get('PATH_INFO', '/')
        #~ self.response.write("OK: %s" % pathInfo)
        #~ return self.response

        pathInfo = urllib.unquote(pathInfo)
        try:
            pathInfo = unicode(pathInfo, "utf-8")
        except:
            pass

        pathInfo = pathInfo.strip("/")
        self.request.environ["PATH_INFO"] = pathInfo

    def setup_runlevel(self):

        pathInfo = self.request.environ["PATH_INFO"]

        if pathInfo.startswith(self.preferences["installURLprefix"]):
            self.request.runlevel = "install"
        elif pathInfo.startswith(self.preferences["commandURLprefix"]):
            self.request.runlevel = "command"
        else:
            self.request.runlevel = "normal"

    def init2(self):
        """
        Getrennt vom normalen init, weil zwischenzeitlich evtl. nur ein CSS
        ausgeliefert werden sollte oder PyLucid installieret werden soll...
        Dazu sind die restilichen Objekte garnicht nötig.
        """
        # Preferences aus der DB lesen
        self.request.preferences.update_from_sql(self.db)

        # Log-Ausgaben in SQL-DB
        self.request.log    = SQL_logging.log(self.request)
        #~ self.request.log.debug_last()

        # Allgemeiner CGI Sessionhandler auf mySQL-Basis
        self.request.session = sessionhandling.sessionhandler(
            #~ self.request, page_msg_debug=False
            self.request, self.response, page_msg_debug=True
        )

        # Aktuelle Seite ermitteln und festlegen
        detect_page.detect_page(self.request, self.response).detect_page()
        # Überprüfe Rechte der Seite
        #~ self.verify_page()

        self.request.render = page_parser.render(self.request, self.response)

        # Verwaltung von erweiterungs Modulen/Plugins
        self.request.module_manager = module_manager.module_manager(
            self.request, self.response
        )
        #~ self.request.module_manager.debug()

        # Der ModulManager, wird erst nach dem Parser instanziert. Damit aber
        # der Parser auf ihn zugreifen kann, packen wir ihn einfach dorthin ;)
        #~ self.request.parser.module_manager = self.request.module_manager

        #Shorthands
        self.render = self.request.render
        self.session = self.request.session
        self.module_manager = self.request.module_manager


    def process_request(self):

        self.setup_runlevel()

        if self.request.runlevel == "install":
            self.installPyLucid()
        else:
            self.process_normal_request()

        if debug:
            from colubrid.debug import debug_info
            self.page_msg(debug_info(self.request))

        return self.response

    def debug(self, *txt):
        #~ sys.stderr.write(
        self.page_msg(
            "%s\n" % " ".join([str(i) for i in txt])
        )

    def setup_staticTags(self):
        """
        "Statische" Tag's definieren
        """
        self.request.staticTags = {}

        self.request.staticTags["powered_by"]  = __info__
        if self.session["user"] != False:
            link = self.URLs.make_command_link("auth", "logout")
            self.request.staticTags["script_login"] = \
            '<a href="%s">logout [%s]</a>' % (
                link, self.request.session["user"]
            )
        else:
            link = self.URLs.make_command_link("auth", "login")
            self.request.staticTags["script_login"] = \
            '<a href="%s">login</a>' % (link)

    def process_normal_request(self):

        self.init2()
        self.setup_staticTags()

        #~ self.tools.page_msg_debug(self.environ)

        if self.request.runlevel == "command":
            # Ein Kommando soll ausgeführt werden
            self.request.staticTags["robots"] = self.preferences["robots_tag"]["internal_pages"]

            # Schreibt das Template für das aktuelle Kommando ins
            # response Objekt. Darin ist der page_body-Tag der von
            # der replacer-Middleware bzw. mit dem page_body-Module
            # ausgefüllt wird.
            self.render.write_command_template()
        else:
            # Normale Seite wird ausgegeben
            self.request.staticTags["robots"] = self.preferences["robots_tag"]["content_pages"]

            # Schreib das Template mit dem page_body-Tag ins
            # response Objekt.
            self.render.write_page_template()

    def installPyLucid(self):
        from PyLucid.install.install import InstallApp
        InstallApp.__info__ = __info__
        InstallApp(self.request, self.response).process_request()


app = PyLucidApp

# preferences
from PyLucid.middlewares.preferences import preferencesMiddleware
app = preferencesMiddleware(app)

# database
from PyLucid.middlewares.database import DatabaseMiddleware
app = DatabaseMiddleware(app)

# Middleware Page-Message-Object
from PyLucid.middlewares.page_msg import page_msg
app = page_msg(app)


# Middleware um die Tags auszuführen
from PyLucid.middlewares.Replacer import ReplacePyLucidTags
app = ReplacePyLucidTags(app, WSGIrequestKey)
app = ReplacePyLucidTags(app, WSGIrequestKey)


# Middleware um die Page-Msg Ausgaben einzusetzten
from PyLucid.middlewares.page_msg import ReplacePageMsg
app = ReplacePageMsg(app, "<lucidTag:page_msg/>")


# Middleware, die den Tag <lucidTag:script_duration/> ersetzt
from PyLucid.middlewares.Replacer import ReplaceDurationTime
app = ReplaceDurationTime(app, "<lucidTag:script_duration/>", WSGIrequestKey)



if __name__ == '__main__':
    from colubrid.debug import DebuggedApplication
    from colubrid import execute
    app = DebuggedApplication('PyLucid_app:app')
    execute(app, reload=True)
