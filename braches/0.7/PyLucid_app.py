#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://www.PyLucid.org"

__info__ = """<a href="%s" title="PyLucid - A OpenSource CMS in pure Python CGI by Jens Diemer">\
PyLucid</a> v0.7.0Alpha""" % __url__

# Als erstes Mal die Zeit stoppen ;)
import time
start_time = time.time()
start_clock = time.clock()

#_________________________________________________________________________
## Python-Basis Module einbinden
import os, sys, urllib, cgi


#_________________________________________________________________________
## Interne PyLucid-Module einbinden

from PyLucid.python_backports.utils import *

import config # PyLucid Konfiguration
from PyLucid.system import SQL
from PyLucid.system import sessiondata
from PyLucid.system import sessionhandling
from PyLucid.system import SQL_logging
from PyLucid.system import module_manager
from PyLucid.system import tools
from PyLucid.system import preferences
from PyLucid.system import page_parser

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

class detect_page:
    """
    Legt die page ID der aktuellen Seite fest.
    Speichert die ID als "page_id"-Key in den CGIdata, also: self.CGIdata["page_id"]
    """
    def __init__(self, request):

        # shorthands
        self.CGIdata        = request.CGIdata
        self.page_msg       = request.page_msg
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences

    #_________________________________________________________________________

    def detect_page(self):
        "Findet raus welches die aktuell anzuzeigende Seite ist"

        if self.CGIdata.has_key("page_id"):
            # Bei Modulen kann die ID schon in der URL mitgeschickt werden.
            self.check_page_id(self.CGIdata["page_id"])
            return

        if self.CGIdata.has_key("command"):
            # Ein internes Kommando (LogIn, EditPage ect.) wurde ausgeführt
            self.set_history_page()
            return

        if self.preferences["poormans_modrewrite"] == True:
            # Auswerten von os.environ-Eintrag "REQUEST_URI"
            try:
                request_uri = self.request.environ["REQUEST_URI"]
            except KeyError:
                raise KeyError(
                    "Can't use 'poormans_modrewrite':",
                    "There is no REQUEST_URI in Environment!"
                )

            # Scheidet das evtl. vorhandene Verzeichnis ab, in dem sich PyLucid
            # befindet. Denn das gehört nicht zum Seitennamen den der User sehen will.
            if request_uri.startswith(self.preferences["poormans_url"]):
                request_uri = request_uri[len(self.preferences["poormans_url"]):]

            #~ self.page_msg("request_uri:", request_uri)

            self.check_page_name(request_uri)
            return

        if len(self.CGIdata) == 0:
            # keine CGI-Daten vorhanden
            # `-> Keine Seite wurde angegeben -> default-Seite wird angezeigt
            self.set_default_page()
            return

        page_ident = self.preferences["page_ident"].replace("?","")
        page_ident = page_ident.replace("=","")
        if self.CGIdata.has_key(page_ident):
            #~ self.CGIdata.debug()
            #~ self.page_msg( cgi.escape( self.CGIdata[page_ident] ) )
            self.check_page_name(self.CGIdata[page_ident])
            return

        # Es konnte keine Seite in URL-Parametern gefunden werden, also
        # wird die Standart-Seite genommen
        self.set_default_page()

    def check_page_id( self, page_id ):
        """ Testet ob die page_id auch richtig ist """
        try:
            db_page_id = self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["id"]
        except IndexError:
            pass
        else:
            if db_page_id == page_id:
                # Alles OK
                return

        self.page_msg("404 Not Found. Page with id '%s' unknown." % page_id)
        self.set_default_page()

    def set_history_page( self ):
        if self.session.has_key("page_history"):
            self.CGIdata["page_id"] = self.session["page_history"][0]
        else:
            self.page_msg( "Debug: History nicht vorhanden!" )
            self.set_default_page()

    def check_page_name( self, page_name ):
        """ ermittelt anhand des page_name die page_id """

        # Aufteilen: /bsp/ -> ['','%3ClucidTag%3ABsp%2F%3E','']
        page_name_split = page_name.split("/")

        # unquote + Leere Einträge löschen: ['','%3ClucidTag%3ABsp%2F%3E',''] -> ['<lucidTag:Bsp/>']
        page_name_split = [urllib.unquote_plus(i) for i in page_name_split if i!=""]

        #~ page_name = urllib.unquote(  )
        #~ self.CGIdata["REQUEST_URI"] = urllib.unquote_plus(page_name)

        if page_name == "/" or page_name == "":
            # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
            self.set_default_page()
            return

        page_id = 0
        for name in page_name_split:
            #~ self.page_msg( name )
            if name.startswith("index.py?") and name[-1] == "=":
                # Ist ein Parameter und kein Seitenname
                continue

            try:
                page_id = self.db.select(
                        select_items    = ["id","parent"],
                        from_table      = "pages",
                        where           = [ ("name",name), ("parent",page_id) ]
                    )[0]["id"]
            except Exception,e:
                if self.preferences["real_self_url"] == os.environ["REQUEST_URI"]:
                    # Aufruf der eigenen index.py Datei
                    self.set_default_page()
                    return
                else:
                    self.page_msg( "404 Not Found. The requested URL '%s' was not found on this server." % name )
                    #~ self.page_msg( page_name_split )
                    if page_id == 0:
                        # Nur wenn nicht ein Teil der URL stimmt, wird auf die Hauptseite gesprunngen
                        self.set_default_page()
                        return

        self.CGIdata["page_id"] = int( page_id )

    def set_default_page( self ):
        "Setzt die default-Page als aktuelle Seite"
        try:
            self.CGIdata["page_id"] = self.preferences["core"]["defaultPageName"]
        except KeyError:
            self.error(
                "Can'r read preferences from DB.",
                "(Did you install PyLucid correctly?)"
            )
        try:
            self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ["id",self.CGIdata["page_id"]]
            )[0]["id"]
        except IndexError:
            # Die defaultPageName Angabe ist falsch
            self.page_msg("default Page with ID %s not found!" % self.CGIdata["page_id"] )
            try:
                self.CGIdata["page_id"] = self.db.select(
                    select_items    = ["id"],
                    from_table      = "pages",
                    order           = ("id","ASC"),
                    limit           = (0,1) # Nur den ersten ;)
                )[0]["id"]
            except IndexError:
                # Es gibt wohl überhaupt keine Seite???
                self.error("Can't find pages!", self.page_msg.data)


class PyLucid(BaseApplication):

    def __init__(self, *args):
        super(PyLucid, self).__init__(*args)

        # POST und GET Daten zusammen fassen
        import copy
        self.request.CGIdata = copy.copy(self.request.GET)
        self.request.CGIdata.update(self.request.POST)
        #~ self.request.CGIdata = dict(self.request.CGIdata)
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
        self.request.db = SQL.db(self.request)
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
        detect_page(self.request).detect_page()
        # Überprüfe Rechte der Seite
        #~ self.verify_page()


    #_________________________________________________________________________

    def process_request(self):
        self.request.headers['Content-Type'] = 'text/html'
        self.request.echo(__info__)

        self.page_msg("get_available_markups:", self.db.get_available_markups())

        self.init2()
        #~ self.request.echo("<pre>")
        #~ for k,v in self.request.environ.iteritems():
            #~ self.request.echo("%s - %s\n" % (k,v))

        #~ self.request.echo("- "*40)

        #~ for k,v in os.environ.iteritems():
            #~ self.request.echo("%s - %s\n" % (k,v))
        #~ self.request.echo("</pre>")

        # Debug
        #~ self.request.log.debug_last()
        #~ self.page_msg("page_id:", self.CGIdata.page_id)
        self.request.echo(self.page_msg.get())
        self.request.debug_info()


app = PyLucid
    #~ os.environ['SERVER_NAME'] = "colubird CGIServer"
    #~ os.environ['SERVER_PORT'] = "8080"
    #~ exports = {}
    #~ from colubrid import execute
    #~ from colubrid.debug import DebuggedApplication

    #~ execute.CGIServer(DebuggedApplication(app), exports).run()

    #~ execute.StandaloneServer().run()

    #~ CGIServer(app, exports).run()
