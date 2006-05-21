#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__     = "http://www.PyLucid.org"

__info__ = """<a href="%s" title="\
PyLucid - A OpenSource CMS in pure Python CGI by Jens Diemer">PyLucid</a> \
v0.7.0preAlpha""" % __url__


#~ debug = True
debug = False



import cgi, os, time
import sys #Debug

from PyLucid.system.exceptions import *

# Colubrid
from colubrid import BaseApplication

WSGIrequestKey = "colubrid.request"


import config # PyLucid Grundconfiguration

#__init__
from PyLucid.system import response
from PyLucid.system import tools
from PyLucid.system import URLs
from PyLucid.system import jinjaRenderer

# init2
#~ from PyLucid.system import staticTags
from PyLucid.system import sessionhandling
from PyLucid.system import SQL_logging
from PyLucid.system import module_manager
from PyLucid.system import page_parser
from PyLucid.system import detect_page
from PyLucid.system import template_engines


response.__info__ = __info__ # Übertragen




class PyLucidApp(BaseApplication):
    """
    Klasse die die Programmlogik zusammenstellt
    """
    charset = 'utf-8'
    #~ slash_append = True
    slash_append = False

    def __init__(self, environ, start_response):
        super(PyLucidApp, self).__init__(environ, start_response)

        # Eigenes response-Objekt. Eigentlich genau wie das
        # original von colubrid, nur mit einer kleinen Erweiterung
        self.response = response.HttpResponse()

        self.environ        = environ

        self.request.runlevel = "init"

        self.request.debug = self.request_debug

        # Für _install:
        self.request.log            = None
        self.request.render         = None
        self.request.tag_parser     = None
        self.request.session        = None
        self.request.module_manager = None
        self.request.templates      = None

        # Verwaltung für Einstellungen aus der Datenbank (Objekt aus der Middleware)
        self.request.preferences = environ['PyLucid.preferences']

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.request.page_msg = environ['PyLucid.page_msg']

        # Passt die verwendeten Pfade an.
        self.request.URLs = URLs.URLs(self.request)

        # Tools
        tools.request       = self.request  # Request Objekt an tools übergeben
        tools.response      = self.response # Response Objekt an tools übergeben
        self.request.tools  = tools         # Tools an Request Objekt anhängen

        self.response.echo = tools.echo() # Echo Methode an response anhängen

        # Jinja-Context anhängen
        self.request.context = {}

        #~ self.request.jinjaRenderer = jinjaRenderer.jinjaRenderer(self.request)

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.request.db = environ['PyLucid.database']
        self.request.db.connect(self.request.preferences)
        #~ self.request.db = db.db(self.request, self.response)
        self.request.db.page_msg = self.request.page_msg

        # FIXME - Auch in der DB-Klasse wird tools benötigt
        self.request.db.tools = self.request.tools

        # Shorthands
        self.page_msg       = self.request.page_msg
        self.db             = self.request.db
        self.preferences    = self.request.preferences
        self.tools          = self.request.tools
        self.URLs           = self.request.URLs

    def request_debug(self):
        from colubrid.debug import debug_info
        self.page_msg(debug_info(self.request))


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
            #~ self.request, self.response, page_msg_debug=True
            self.request, self.response, page_msg_debug=False
        )

        self.request.staticTags = response.staticTags(self.request, self.response)

        self.request.render = page_parser.render(self.request, self.response)

        # Verwaltung von erweiterungs Modulen/Plugins
        self.request.module_manager = module_manager.module_manager(
            self.request, self.response
        )
        #~ self.request.module_manager.debug()

        #~ self.request.tag_parser = page_parser.tag_parser(self.request, self.response)

        # Aktuelle Seite ermitteln und festlegen
        detect_page.detect_page(self.request, self.response).detect_page()
        # Überprüfe Rechte der Seite
        #~ self.verify_page()

        # Einheitliche Schnittstelle zu den Templates Engines
        self.request.templates = template_engines.TemplateEngines(self.request, self.response)

        #Shorthands
        self.render         = self.request.render
        #~ self.tag_parser     = self.request.tag_parser
        self.session        = self.request.session
        self.module_manager = self.request.module_manager
        self.staticTags     = self.request.staticTags

        # Übertragen von Objekten
        self.db.render = self.render

        self.response.module_manager = self.module_manager
        self.response.staticTags = self.staticTags

        # Statische-Tag-Informationen setzten:
        self.staticTags.setup()


    def process_request(self):

        #~ self.URLs.debug()

        self.environ["request_start"] = time.time()

        self.setup_runlevel()

        if self.request.runlevel == "install":
            try:
                self.installPyLucid()
            except WrongInstallLockCode:
                # Der Zugang zum Install wurde verweigert, also
                # zeigen wir die normale CMS-Seite
                self.request.runlevel = "normal"
            else:
                return self.response

        # init der Objekte für einen normalen Request:
        self.init2()

        if self.request.runlevel == "normal":
            # Normale CMS Seite ausgeben
            self.normalRequest()

        elif self.request.runlevel == "command":
            # Ein Kommando soll ausgeführt werden
            moduleOutput = self.module_manager.run_command()
            if callable(moduleOutput):
                # Wird wohl ein neues response-Objekt sein.
                # z.B. bei einem Dateidownload!
                return moduleOutput

            # Ausgaben vom Modul speichern, dabei werden diese automatisch
            # im response-Objekt gelöscht, denn ein "command"-Modul schreib
            # auch, wie alle anderen Module ins response-Object ;)
            content = self.response.get()

            if self.session.has_key("render follow"):
                # Eintrag löschen, damit der nicht in die DB für den nächsten
                # request gespeichert wird:
                del(self.session["render follow"])

                # Es soll nicht die Ausgaben den Modules angezeigt werden,
                # sondern die normale CMS Seite. (z.B. nach dem Speichern
                # einer editierten Seite!)
                self.normalRequest()
            else:
                # Ausgaben vom Modul sollen in die Seite eingebaut werden:
                self.staticTags["page_body"] = content
                self.render.write_command_template()

        else:
            raise RuntimeError # Kann eigentlich nie passieren ;)

        # Evtl. vorhandene Sessiondaten in DB schreiben
        self.session.commit()

        if debug:
            self.request.debug()

        return self.response


    def normalRequest(self):
        # Normale Seite wird ausgegeben

        # Schreib das Template mit dem page_body-Tag ins
        # response Objekt.
        self.render.write_page_template()



    def debug(self, *txt):
        #~ sys.stderr.write(
        self.page_msg(
            "%s\n" % " ".join([str(i) for i in txt])
        )

    def process_normal_request(self):
        """
        Entweder wird ein "_command" ausgeführt oder eine
        normale CMS Seite angezeigt.
        """

    def installPyLucid(self):
        """
        Der aktuelle request ist im "_install"-Bereich
        """
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

# Middleware, die die Tags "script_duration" und "page_msg" ersetzt
from PyLucid.middlewares.replacer import Replacer
app = Replacer(app)



if __name__ == '__main__':
    from colubrid.debug import DebuggedApplication
    from colubrid import execute
    app = DebuggedApplication('PyLucid_app:app')
    execute(app, reload=True)
