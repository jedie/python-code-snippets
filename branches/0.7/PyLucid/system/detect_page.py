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


from PyLucid.system.BaseModule import PyLucidBaseModule

class detect_page(PyLucidBaseModule):
    """
    Legt die page ID der aktuellen Seite fest.
    Speichert die ID als "page_id"-Key in den Session-Daten, also: request.session["page_id"]
    """
    #~ def __init__(self, *args, **kwargs):
        #~ super(detect_page, self).__init__(*args, **kwargs)

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


        pathInfo = self.environ.get("PATH_INFO","/")
        self.check_page_name(pathInfo)
        return

        #~ pageIdent = self.preferences["page_ident"]
        #~ if self.request.args.has_key(pageIdent):
            #~ page_name = self.request.args[pageIdent]
            #~ self.check_page_name(page_name)
            #~ return


        # Es konnte keine Seite in URL-Parametern gefunden werden, also
        # wird die Standart-Seite genommen
        #~ self.set_default_page()

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

    def check_page_name(self, page_name):
        """ ermittelt anhand des page_name die page_id """

        # /bsp/und%2Foder/ -> bsp/und%2Foder
        page_name = page_name.strip("/")

        if page_name == "":
            # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
            self.set_default_page()
            return

        # bsp/und%2Foder -> ['bsp', 'und%2Foder']
        page_name_split = page_name.split("/")

        page_id = 0
        for shortcut in page_name_split:
            try:
                page_id = self.db.select(
                    select_items    = ["id","parent"],
                    from_table      = "pages",
                    where           = [("shortcut",shortcut), ("parent",page_id)]
                )[0]["id"]
            except Exception,e:
                if self.URLs["real_self_url"] == self.environ["APPLICATION_REQUEST"]:
                    # Aufruf der eigenen index.py Datei
                    self.set_default_page()
                    return
                else:
                    self.page_msg(
                        "404 Not Found. The requested URL '%s' was not found on this server." % shortcut
                    )
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