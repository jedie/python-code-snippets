#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License v2 or above - http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://www.PyLucid.org"

__info__ = """<a href="%s" title="PyLucid - A OpenSource CMS in pure Python CGI by Jens Diemer">\
PyLucid</a> v0.7.0Alpha""" % __url__

import cgi, urllib

from PyLucid.system.exceptions import *

# Colubrid
from colubrid import BaseApplication
from colubrid import HttpResponse



import config # PyLucid Konfiguration

#__init__
from PyLucid.system import sessiondata
from PyLucid.system import preferences
from PyLucid.system import tools
from PyLucid.system import db
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
    slash_append = True

    def __init__(self, *args):
        super(PyLucidApp, self).__init__(*args)
        self.response = HttpResponse()
        #~ self.request.response = self.response

        # Tools
        tools.request       = self.request  # Request Objekt an tools übergeben
        tools.response      = self.response # Response Objekt an tools übergeben
        self.request.tools  = tools         # Tools an Request Objekt anhängen

        self.response.echo = tools.echo() # Echo Methode an response anhängen

        # Jinja-Context anhängen
        self.request.context = {}

        #~ self.request.jinjaRenderer = jinjaRenderer.jinjaRenderer(self.request)

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.request.page_msg = sessiondata.page_msg(debug=True)
        #~ self.request.page_msg = sessiondata.page_msg(debug=False)

        # Verwaltung für Einstellungen aus der Datenbank
        self.request.preferences = preferences.preferences(
            self.request, config.config
        )

        # Passt die verwendeten Pfade an.
        self.request.URLs = preferences.URLs(self.request)

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.request.db = db.db(self.request, self.response)

        # Shorthands
        self.page_msg       = self.request.page_msg
        self.db             = self.request.db
        self.preferences    = self.request.preferences


    def init2(self):
        """
        Getrennt vom normalen init, weil zwischenzeitlich evtl. nur ein CSS
        ausgeliefert werden sollte oder PyLucid installieret werden soll...
        Dazu sind die restilichen Objekte garnicht nötig.
        """
        self.preferences.update_from_sql() # Preferences aus der DB lesen

        # Log-Ausgaben in SQL-DB
        self.request.log    = SQL_logging.log(self.request)
        #~ self.request.log.debug_last()

        # Allgemeiner CGI Sessionhandler auf mySQL-Basis
        self.request.session = sessionhandling.sessionhandler(
            #~ self.request, page_msg_debug=False
            self.request, page_msg_debug=True
        )

        # Aktuelle Seite ermitteln und festlegen
        detect_page.detect_page(self.request).detect_page()
        # Überprüfe Rechte der Seite
        #~ self.verify_page()

        self.request.parser = page_parser.parser(self.request)
        self.request.render = page_parser.render(self.request, self.response)

        # Verwaltung von erweiterungs Modulen/Plugins
        self.request.module_manager = module_manager.module_manager(
            self.request, self.response
        )
        #~ self.request.module_manager.debug()

        # Der ModulManager, wird erst nach dem Parser instanziert. Damit aber
        # der Parser auf ihn zugreifen kann, packen wir ihn einfach dorthin ;)
        self.request.parser.module_manager = self.request.module_manager

        #Shorthands
        self.parser = self.request.parser
        self.render = self.request.render
        self.session = self.request.session
        self.module_manager = self.request.module_manager


    def process_request(self):
        self.page_msg("jep! Ich lebe...")

        pathInfo = self.request.environ.get('PATH_INFO', '/')
        pathInfo = urllib.unquote(pathInfo)
        try:
            pathInfo = unicode(pathInfo, "utf-8")
        except:
            pass

        if pathInfo.startswith("/%s" % self.preferences["installURLprefix"]):
            self.installPyLucid()
        else:
            self.process_normal_request(pathInfo)

        self.db.close()
        self.page_msg("ENDE!")
        return self.response

    def process_normal_request(self, pathInfo):

        self.init2()
        self.setup_staticTags()

        if pathInfo.startswith("/%s" % self.preferences["commandURLprefix"]):
            # Ein Kommando soll ausgeführt werden
            content = self.module_manager.run_command(pathInfo)
            self.response.write(content)
            return

        self.render.render_page()

    def setup_staticTags(self):
        # "Statische" Tag's definieren
        self.parser.tag_data["powered_by"]  = __info__
        if self.session["user"] != False:
            self.parser.tag_data["script_login"] = \
            '<a href="%s&amp;command=auth&amp;action=logout">logout [%s]</a>' % (
                self.request.URLs["base"], self.request.session["user"]
            )
        else:
            self.parser.tag_data["script_login"] = \
            '<a href="%s&amp;command=auth&amp;action=login">login</a>' % (
                self.request.URLs["base"]
            )

    def installPyLucid(self):
        self.response.write("<h3>install %s</h3>" % __info__)
        from PyLucid.install.install import InstallApp
        InstallApp(self.request, self.response).process_request()

app = PyLucidApp

# Middleware um die Page-Msg Ausgaben einzusetzten
from PyLucid.middlewares.Replacer import ReplacePageMsg
app = ReplacePageMsg(app, "<lucidTag:page_msg/>")

# Middleware, die den Tag <script_duration /> ersetzt
from PyLucid.middlewares.Replacer import ReplaceDurationTime
app = ReplaceDurationTime(app, "<lucidTag:script_duration/>")

if __name__ == '__main__':
    from colubrid.debug import DebuggedApplication
    from colubrid import execute
    app = DebuggedApplication('PyLucid_app:app')
    execute(app, reload=True)
