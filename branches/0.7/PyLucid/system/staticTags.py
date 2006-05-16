#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Dict zum speichern der statischen Tag-Informationen
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.1"

__history__="""
v0.1
    - erste Version
"""


import os, cgi



class staticTags(dict):

    def __init__(self, request, response):
        dict.__init__(self)

        self.request = request

        # Shorthands
        self.preferences    = request.preferences
        self.URLs           = request.URLs
        self.session        = request.session
        self.tools          = request.tools

    def setup(self):
        """
        "Statische" Tag's definieren
        """
        self["commandURLprefix"] = self.preferences["commandURLprefix"]
        self["installURLprefix"] = self.preferences["installURLprefix"]

        self["powered_by"]  = __info__
        if self.session["user"] != False:
            link = self.URLs.make_command_link("auth", "logout")
            self["script_login"] = '<a href="%s">logout [%s]</a>' % (
                link, self.session["user"]
            )
        else:
            link = self.URLs.make_command_link("auth", "login")
            self["script_login"] = '<a href="%s">login</a>' % (link)

        if self.request.runlevel == "command":
            # Ein Kommando soll ausgeführt werden
            self.setup_command_tags()


    def setup_command_tags(self):
        self["robots"] = self.preferences["robots_tag"]["internal_pages"]
        self["page_keywords"] = ""
        self["page_description"] = ""

        #FIXME:
        self["page_name"] = self["page_title"] = self.request.environ["PATH_INFO"]
        self["page_last_modified"] = ""
        self["page_datetime"] = ""


    def fill_with_page_data(self, page_data):
        """
        Eintragen von Tags durch die CMS-Seiten-Informationen aus der DB
        Wird von page_parser.render verwendet
        """
        self["robots"] = self.preferences["robots_tag"]["content_pages"]

        self["markup"]               = page_data["markup"]
        self["page_name"]            = cgi.escape(page_data["name"])
        self["page_title"]           = cgi.escape(page_data["title"])
        self["page_keywords"]        = page_data["keywords"]
        self["page_description"]     = page_data["description"]

        self["page_last_modified"]   = self.tools.convert_date_from_sql(
            page_data["lastupdatetime"], format = "preferences"
        )

        self["page_datetime"]        = self.tools.convert_date_from_sql(
            page_data["lastupdatetime"], format = "DCTERMS.W3CDTF"
        )





