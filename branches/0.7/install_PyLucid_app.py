#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid "installer"
"""

__version__ = "v0.7"

__history__ = """
v0.7
    - Umbau zu einer colubrid WSGI ObjectApplication
v0.6
    - Neu: update_db()
v0.5
    - Neu: "Information about installed modules"
    - ein paar "confirm"-Dialoge eingebaut...
v0.4.1
    - Ein wenig Aufgeräumt
v0.4
    - Anderer Aufbau der actions: In Sektionen unterteilt.
    - Neu: db_info
v0.3.1
    - Packports Pfad hinzugefügt
v0.3
    - Es kann nur einmal ein Admin angelegt werden
    - Benutzt nun einige PyLucid-Objekte (erforderlich für neues userhandling)
    - Möglichkeit dir Markup-String zu IDs zu konvertieren (Änderung in PyLucid v0.5)
    - CSS Spielereien 2
v0.2
    - Anpassung an neue install-Daten-Struktur.
    - "add Admin"-Formular wird mit JavaScript überprüft.
    - NEU Path Check: allerdings wird erstmal nur die Pfade angezeigt, mehr nicht...
    - CSS Spielereien
    - Aussehen geändert
v0.1.0
    - NEU: "partially re-initialisation DB tables" damit kann man nur ausgesuhte
        Tabellen mit den Defaultwerten überschrieben.
v0.0.8
    - Fehler in SQL_dump(): Zeigte SQL-Befehle nur an, anstatt sie auszuführen :(
v0.0.7
    - Neue Art die nötigen Tabellen anzulegen.
v0.0.6
    - Einige anpassungen
v0.0.5
    - NEU: convert_db: Convertiert Daten von PHP-LucidCMS nach PyLucid
v0.0.4
    - Anpassung an neuer Verzeichnisstruktur
v0.0.3
    - NEU: update internal pages
v0.0.2
    - Anpassung an neuer SQL.py Version
    - SQL-connection werden am Ende beendet
v0.0.1
    - erste Version
"""

__todo__ = """
Sicherheitslücke: Es sollte nur ein Admin angelegt werden können, wenn noch keiner existiert!
"""


import cgi, urllib

from PyLucid.system.exceptions import *

# Colubrid
from colubrid import ObjectApplication
from colubrid import HttpResponse





HTML_head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>PyLucid Setup</title>
<meta name="robots"             content="noindex,nofollow" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<style type="text/css">
html, body {
    padding: 30px;
    background-color: #FFFFEE;
}
body {
    font-family: tahoma, arial, sans-serif;
    color: #000000;
    font-size: 0.9em;
    background-color: #FFFFDB;
    margin: 30px;
    border: 3px solid #C9C573;
}
form * {
  vertical-align:middle;
}
input {
    border: 1px solid #C9C573;
    margin: 0.4em;
}
pre {
    background-color: #FFFFFF;
    padding: 1em;
}
#menu li, #menu li a {
    list-style-type: none;
    padding: 0.3em;
}
#menu h4 {
    margin: 0px;
}
a {
    color:#00BBEE;
    padding: 0.1em;
}
a:hover {
    color:#000000;
    background-color: #F4F4D2;
}
</style>
<h2>PyLucid Setup %s</h2>""" % __version__
HTML_bottom = "</body></html>"




from PyLucid.install import menu
from PyLucid.install.ObjectApp_Base import ObjectApp_Base

from PyLucid.install.App_tests import tests
from PyLucid.install.App_Update import update
from PyLucid.install.App_LowLevelAdmin import LowLevelAdmin
from PyLucid.install.App_ScratchInstall import install



#~ import inspect


import config # PyLucid Konfiguration
from PyLucid.system import sessiondata
from PyLucid.system import preferences
from PyLucid.system import tools
from PyLucid.system import db
from PyLucid.system import jinjaRenderer




class PyLucidInstallApp(ObjectApplication):
    """
    Klasse die die Programmlogik zusammenstellt
    """
    charset = 'utf-8'
    slash_append = True

    root = menu.menu
    root.install        = install
    root.update         = update
    root.LowLevelAdmin  = LowLevelAdmin
    root.tests          = tests

    def __init__(self, *args):
        super(PyLucidInstallApp, self).__init__(*args)
        self.response = HttpResponse()

        # Jinja-Context anhängen
        self.request.context = {}

        #~ self.request.jinjaRenderer = jinjaRenderer.jinjaRenderer(self.request)

        self._write_head()

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg           = sessiondata.page_msg(debug=True)
        #~ self.page_msg           = sessiondata.page_msg(debug=False)
        self.request.page_msg   = self.page_msg
        #~ self.request.exposed.append("page_msg") # An Debug-Info dranpacken

        # Verwaltung für Einstellungen aus der Datenbank
        self.preferences            = preferences.preferences(self.request, config.config)
        self.request.preferences    = self.preferences

        # Passt die verwendeten Pfade an.
        self.request.URLs = preferences.URLs(self.request)

        tools.request           = self.request # Request Objekt an tools übergeben
        self.request.tools      = tools

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.request.db = db.get_PyLucid_Database(self.request)
        #~ self.request.db = SQL_wrapper.SQL_wrapper(self.request)
        self.db = self.request.db

        # Menügenerator in die Basisklasse "einpflanzen"
        ObjectApp_Base.MenuGenerator = menu.Install_MenuGenerator(
            self.response, self.root,
            blacklist = ("response",)
        )

        # Der Basisklasse das response Object einpflanzen, damit es auch ausgaben machen kann.
        ObjectApp_Base.response = self.response


    def process_request(self):
        super(PyLucidInstallApp, self).process_request()

        pathInfo = self.request.environ.get('PATH_INFO', '/')
        pathInfo = urllib.unquote(pathInfo)
        try:
            pathInfo = unicode(pathInfo, "utf-8")
        except:
            pass

        #~ make_menu

        self.response.write(self.page_msg.get())
        self.response.write(HTML_bottom)
        #~ self.db.close()
        return self.response


    def _write_head(self, backlink=True):
        self.response.write(HTML_head)



app = PyLucidInstallApp

