#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License v2 or above - http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://www.PyLucid.org"

__info__ = """<a href="%s" title="PyLucid - A OpenSource CMS in pure Python CGI by Jens Diemer">\
PyLucid</a> v0.7.0Alpha""" % __url__



#_________________________________________________________________________
## Python-Basis Module einbinden
import os, sys, urllib, cgi


#_________________________________________________________________________
## Interne PyLucid-Module einbinden

from PyLucid.python_backports.utils import *

import config # PyLucid Konfiguration
from PyLucid.system import db
from PyLucid.system import sessiondata
from PyLucid.system import sessionhandling
from PyLucid.system import SQL_logging
from PyLucid.system import module_manager
from PyLucid.system import tools
from PyLucid.system import preferences
from PyLucid.system import page_parser
from PyLucid.system import detect_page

#~ # Versions-Information übertragen
preferences.__info__    = __info__

#~ import cgitb;cgitb.enable()
#~ print "Content-type: text/html; charset=utf-8\r\n\r\nDEBUG:<pre>"

#_________________________________________________________________________
## colubuird imports

from colubrid import BaseApplication

#~ import sys
#~ sys.path.insert(0,"PyLucid")
#~ from PyLucid import index




class PyLucid(BaseApplication):

    def __init__(self, *args):
        super(PyLucid, self).__init__(*args)

        # POST und GET Daten zusammen fassen
        # wird u.a. für's ModuleManager "CGI_laws" und "get_CGI_data" verwendet
        import copy
        self.request.CGIdata = copy.copy(self.request.GET)
        self.request.CGIdata.update(self.request.POST)
        self.request.CGIdata = dict(self.request.CGIdata)
        self.request.exposed.append("CGIdata")# An Debug-Info dranpacken

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg           = sessiondata.page_msg(debug=True)
        #~ self.page_msg           = sessiondata.page_msg(debug=False)
        self.request.page_msg   = self.page_msg
        #~ self.request.exposed.append("page_msg") # An Debug-Info dranpacken

        # Verwaltung für Einstellungen aus der Datenbank
        self.preferences            = preferences.preferences(self.request, config.config)
        self.request.preferences    = self.preferences
        self.request.exposed.append("preferences") # An Debug-Info dranpacken

        # Passt die verwendeten Pfade an.
        self.request.URLs = preferences.URLs(self.request)
        self.request.exposed.append("URLs") # An Debug-Info dranpacken

        tools.request           = self.request # Request Objekt an tools übergeben
        self.request.tools      = tools

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.request.db = db.get_PyLucid_Database(self.request)
        #~ self.request.db = SQL_wrapper.SQL_wrapper(self.request)
        self.db = self.request.db

        # URLs zusammenbauen, die immer gleich sind.
        #~ self.request.path.setup_URLs()

    def init2(self):
        """
        Getrennt vom normalen init, weil zwischenzeitlich evtl. nur ein CSS ausgeliefert
        werden sollte... Dazu sind die restilichen Objekte garnicht nötig.
        """
        self.request.preferences.update_from_sql() # Preferences aus der DB lesen

        # Log-Ausgaben in SQL-DB
        self.log            = SQL_logging.log(self.request)
        self.request.log    = self.log
        self.request.exposed.append("log") # An Debug-Info dranpacken
        #~ self.request.log.debug_last()

        # Allgemeiner CGI Sessionhandler auf mySQL-Basis
        self.session            = sessionhandling.sessionhandler(self.request, page_msg_debug=False)
        #~ self.session        = sessionhandling.sessionhandler(self.request, page_msg_debug=True )
        self.request.session = self.session
        #~ self.request.session.debug()
        self.request.exposed.append("session") # An Debug-Info dranpacken

        # Aktuelle Seite ermitteln und festlegen
        detect_page.detect_page(self.request).detect_page()
        # Überprüfe Rechte der Seite
        #~ self.verify_page()

        self.parser = page_parser.parser(self.request)
        self.request.parser = self.parser

        self.render = page_parser.render(self.request)
        self.request.render = self.render

        # Verwaltung von erweiterungs Modulen/Plugins
        self.module_manager = module_manager.module_manager(self.request)
        #~ self.module_manager.debug()
        self.request.module_manager = self.module_manager

        # Der ModulManager, wird erst nach dem Parser instanziert. Damit aber der Parser
        # auf ihn zugreifen kann, packen wir ihn einfach dorthin ;)
        self.parser.module_manager = self.module_manager

    #_________________________________________________________________________

    def process_request(self):
        self.request.headers['Content-Type'] = 'text/html'
        #~ self.request.echo(__info__)

        #~ self.page_msg("get_available_markups:", self.db.get_available_markups())

        self.init2()

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

        self.render.render_page()


        # Debug
        #~ self.request.log.debug_last()
        #~ self.page_msg("page_id:", self.CGIdata.page_id)
        self.request.echo(self.page_msg.get())
        self.request.debug_info()

        # Datenbank verbindung beenden
        self.db.close()


from PyLucid.middlewares.replacer import replacer

app = replacer(PyLucid)


    #~ os.environ['SERVER_NAME'] = "colubird CGIServer"
    #~ os.environ['SERVER_PORT'] = "8080"
    #~ exports = {}
    #~ from colubrid import execute
    #~ from colubrid.debug import DebuggedApplication

    #~ execute.CGIServer(DebuggedApplication(app), exports).run()

    #~ execute.StandaloneServer().run()

    #~ CGIServer(app, exports).run()
