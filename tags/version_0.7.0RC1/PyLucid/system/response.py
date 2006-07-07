#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""

"""

__version__="0.1"

__history__="""
v0.1
    - erste Version
"""

__todo__="""
"""

# Colubrid
from colubrid import HttpResponse

import re, os, cgi





lucidSplitRE = re.compile("<lucid(.*?)")

ignore_tag = ("page_msg", "script_duration")




class HttpResponse(HttpResponse):
    """
    Den original HttpResponse von colubrid erweitern, sodas alle
    PyLucid-Tags beim schreiben vom ModuleManager ausgefüllt werden
    """

    def write(self, txt):
        #~ if not isinstance(self.response, list):
            #~ raise TypeError('read only or dynamic response object')

        #~ if not isinstance(txt, basestring):
            #~ raise TypeError('str or unicode required')

        txt = lucidSplitRE.split(txt)
        for part in txt:
            if part.startswith("Tag:"):
                # Bsp part => Tag:page_body/><p>jau</p>

                tag, post = part.split(">",1)
                # tag  => Tag:page_body/
                # post => <p>jau</p>

                tag = tag[4:]
                if tag[-1]=="/": # .rstrip("/") gibt es in Python 2.2 so nicht
                    tag = tag[:-1]

                # Tag Ã¼ber Module-Manager ausfÃ¼hren
                self.handleTag(tag)

                # Teil hinter dem Tag schreiben
                self.response.append(post)
            elif part.startswith("Function:"):
                # Bsp part:
                # Function:IncludeRemote>http://www.google.de</lucidFunction><p>jau</p>

                function, post = part.split("</lucidFunction>")
                # function  => Function:IncludeRemote>http://www.google.de
                # post      => <p>jau</p>

                function, function_info = function.split(">")
                # function      => Function:IncludeRemote
                # function_info => http://www.google.de

                function = function.split(":")[1]
                # function => IncludeRemote

                self.module_manager.run_function(function, function_info)

                # Teil hinter dem Tag schreiben
                self.response.append(post)
            else:
                self.response.append(part)

    def handleTag(self, tag):
        if tag in ignore_tag:
            self.response.append("<lucidTag:%s/>" % tag)
        elif tag in self.staticTags:
            self.response.append(self.staticTags[tag])
        else:
            self.module_manager.run_tag(tag)

    def get(self):
        "zurÃ¼ckliefern der bisher geschriebene Daten"
        content = self.response
        # FIXME: unicode-Fehler sollten irgendwie angezeigt werden!
        result = ""
        for line in content:
            if type(line)!=unicode:
                line = unicode(line, errors="replace")
            result += line

        self.response = []
        return result




class staticTags(dict):
    """
    Dict zum speichern der statischen Tag-Informationen
    """

    def init2(self, request, response):
        #~ dict.__init__(self)

        # Shorthands
        self.environ        = request.environ
        self.runlevel       = request.runlevel
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
        #~ if self.session.has_key("user") and self.session["user"] != False:
        if self.session != None and self.session["user"] != False:
            link = self.URLs.commandLink("auth", "logout")
            self["script_login"] = '<a href="%s">logout [%s]</a>' % (
                link, self.session["user"]
            )
        else:
            link = self.URLs.commandLink("auth", "login")
            self["script_login"] = '<a href="%s">login</a>' % (link)

        if self.runlevel.is_command():
            # Ein Kommando soll ausgeführt werden
            self.setup_command_tags()


    def setup_command_tags(self):
        self["robots"] = self.preferences["robots_tag"]["internal_pages"]
        self["page_keywords"] = ""
        self["page_description"] = ""

        #FIXME:
        self["page_name"] = self["page_title"] = self.environ["PATH_INFO"]
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

