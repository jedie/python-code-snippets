#!/usr/bin/python
# -*- coding: UTF-8 -*-

class info:
    def __init__(self, request):
        self.request = request

        # Shorthands
        self.cfg        = self.request.cfg
        self.path       = self.request.path
        self.context    = self.request.context
        self.db         = self.request.db


    def status(self):
        """
        Informations-Seite anzeigen
        """
        self.db.log(type="view", item="infopage")

        # Information aus der DB sammeln
        self.context["current_downloads"] = self.db.human_readable_downloads()
        self.context["last_log"] = self.db.human_readable_last_log(20)

        self.context["bandwith"] = self.db.get_bandwith()

        #~ if self.cfg["debug"]: self.request.debug_info()

        self.request.render("Infopage_base")


def status(request):
    info(request).status()