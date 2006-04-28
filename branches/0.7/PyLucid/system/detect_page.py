#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Durch poormans_modrewrite ist es nicht ganz so einfach festzustellen, welche
Seite die aktuelle ist :)
"""

__version__="0.1"

__history__="""
v0.1
    - Ausgekoppelt aus der index.py
    - Speichert die aktuelle Seite nicht mehr in CGIdata["page_id"] sondern in session["page_id"]
"""


import urllib

class detect_page:
    """
    Legt die page ID der aktuellen Seite fest.
    Speichert die ID als "page_id"-Key in den Session-Daten, also: request.session["page_id"]
    """
    def __init__(self, request):
        self.request        = request

        # shorthands
        self.page_msg       = request.page_msg
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences
        self.environ        = request.environ
        self.URLs           = request.URLs

    #_________________________________________________________________________

    def detect_page(self):
        "Findet raus welches die aktuell anzuzeigende Seite ist"

        if self.request.args.has_key("page_id"):
            # Bei Modulen kann die ID schon in der URL mitgeschickt werden.
            self.check_page_id(self.request.args["page_id"])
            return

        if self.request.args.has_key("command"):
            # Ein internes Kommando (LogIn, EditPage ect.) wurde ausgeführt
            self.set_history_page()
            return

        if self.preferences["poormans_modrewrite"] == True:
            # Auswerten von os.environ-Eintrag "REQUEST_URI"
            try:
                request_uri = self.environ["REQUEST_URI"]
            except KeyError:
                raise KeyError(
                    "Can't use 'poormans_modrewrite':",
                    "There is no REQUEST_URI in Environment!"
                )

            # Scheidet das evtl. vorhandene Verzeichnis ab, in dem sich PyLucid
            # befindet. Denn das gehört nicht zum Seitennamen den der User sehen will.
            if request_uri.startswith(self.URLs["poormans_url"]):
                request_uri = request_uri[len(self.URLs["poormans_url"]):]

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
            self.session["page_id"] = self.session["page_history"][0]
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
                        where           = [("name",name), ("parent",page_id)]
                    )[0]["id"]
            except Exception,e:
                if self.URLs["real_self_url"] == self.environ["APPLICATION_REQUEST"]:
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

        self.session["page_id"] = int(page_id)

    def set_default_page( self ):
        "Setzt die default-Page als aktuelle Seite"
        try:
            self.session["page_id"] = self.preferences["core"]["defaultPageName"]
        except KeyError:
            self.error(
                "Can'r read preferences from DB.",
                "(Did you install PyLucid correctly?)"
            )
        try:
            self.db.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ["id",self.session["page_id"]]
            )[0]["id"]
        except IndexError:
            # Die defaultPageName Angabe ist falsch
            self.page_msg("default Page with ID %s not found!" % self.session["page_id"] )
            try:
                self.session["page_id"] = self.db.select(
                    select_items    = ["id"],
                    from_table      = "pages",
                    order           = ("id","ASC"),
                    limit           = (0,1) # Nur den ersten ;)
                )[0]["id"]
            except IndexError:
                # Es gibt wohl überhaupt keine Seite???
                self.error("Can't find pages!", self.page_msg.data)

        self.page_msg("set_default_page(): ID %s" % self.session["page_id"])