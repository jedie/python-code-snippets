#!/usr/bin/python
# -*- coding: UTF-8 -*-

class info:
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # Shorthands
        self.cfg        = self.request.cfg
        self.path       = self.request.path
        self.context    = self.request.context
        self.db         = self.request.db

        if self.request.form.has_key("bandwith"):
            self.change_bandwith(self.request.form["bandwith"])

        self.status()

    def status(self):
        """
        Informations-Seite anzeigen
        """
        self.db.log(type="view", item="infopage")

        # Information aus der DB sammeln
        self.context["current_downloads"] = self.db.human_readable_downloads()
        self.context["current_uploads"] = self.db.human_readable_uploads()
        self.context["last_log"] = self.db.human_readable_last_log(20)

        self.context["bandwith"] = self.db.get_bandwith()

        #~ if self.cfg["debug"]: self.request.debug_info()

        self.request.render("Infopage_base")

    def change_bandwith(self, bandwith):
        """
        Bandbreite soll geändert werden
        """
        if self.context["is_admin"] != True:
            raise AccessDenied("Only Admin can cange preferences!")

        try:
            bandwith = int(bandwith)
            if bandwith<1 or bandwith>999: raise ValueError
        except ValueError:
            self.request.write("Can't cahnge bandwith: value error!")
            return

        self.response.write("change bandwith to: %s" % bandwith)

        self.db.set_bandwith(bandwith)

        self.db.log(type="admin", item="change bandwith to %s" % bandwith)






