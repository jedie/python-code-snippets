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
    - Speichert die aktuelle Seite nicht mehr in CGIdata["page_id"] sondern in
        session["page_id"]
"""


import urllib, cgi


from PyLucid.system.BaseModule import PyLucidBaseModule

class detect_page(PyLucidBaseModule):
    """
    Legt die page ID der aktuellen Seite fest.
    Speichert die ID als "page_id"-Key in den Session-Daten,
    also: request.session["page_id"]
    """
    #~ def __init__(self, *args, **kwargs):
        #~ super(detect_page, self).__init__(*args, **kwargs)

    def detect_page(self):
        "Findet raus welches die aktuell anzuzeigende Seite ist"

        if self.request.args.has_key("page_id"):
            # Bei Modulen kann die ID schon in der URL mitgeschickt werden.
            self.check_page_id(self.request.args["page_id"])
            return

        if self.runlevel.is_command():
            # Ein internes Kommando (LogIn, EditPage ect.) wurde ausgeführt
            if self.session.has_key("page_id"):
                self.check_page_id(self.session["page_id"])
            else:
                self.set_history_page()
            return


        pathInfo = self.environ.get("PATH_INFO","/")
        self.check_page_name(pathInfo)
        return

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
            self.check_page_id(self.session["page_id"])
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

        correctShortcuts=[]
        page_id = 0
        for no, shortcut in enumerate(page_name_split):
            try:
                page_id = self.db.select(
                    select_items    = ["id","parent"],
                    from_table      = "pages",
                    where           = [
                        ("shortcut",shortcut), ("parent",page_id)
                    ]
                )[0]["id"]
            except Exception,e:
                wrongShortcuts = page_name_split[no:]
                msg = (
                    "404 Not Found."
                    " The requested URL '%s' was not found on this server."
                ) % cgi.escape("/".join(wrongShortcuts))
                self.page_msg(msg)

                if no == 0:
                    # Kein Teil der URL ist richtig
                    self.set_default_page()
                    return
                else:
                    # Die ersten Teile der URL sind richtig, also werden diese
                    # berÃ¼cksichtig
                    # URLs richtig setzten, damit die generierung von Links
                    # auch die richtige Grundlage haben:
                    self.URLs.handle404errors(correctShortcuts, wrongShortcuts)
                    break
            else:
                correctShortcuts.append(shortcut)

        self.session["page_id"] = int(page_id)

        # Aktuelle Seite zur page_history hinzufÃ¼gen:
        self.session.set_pageHistory(self.session["page_id"])


    def set_default_page( self ):
        "Setzt die default-Page als aktuelle Seite"
        try:
            self.session["page_id"] = self.preferences["core"]["defaultPageName"]
        except KeyError:
            self.page_msg(
                "Can'r read preferences from DB.",
                "(Did you install PyLucid correctly?)"
            )
            self.session["page_id"] = 0
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