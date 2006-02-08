#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verwaltung der Einstellungen
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.1"

__history__="""
v0.0.2
    - Fehlerabfrage beim Zugriff auf die SQL DB
v0.0.1
    - erste Version
"""


import os



class preferences(dict):
    """
    preferences Tabelle aus Datenbank lesen und als Dict zur verfügung stellen
    """

    def __init__(self, request, config):
        dict.__init__(self)

        self.update(config)

        self.request    = request

        #~ self.request.page_msg(self)

    def update_from_sql( self ):
        """ Preferences aus der DB lesen und in self speichern """

        try:
            RAWdata = self.request.db.get_all_preferences()
        except Exception, e:
            self.request.echo("<h1>Error: Can't read preferences:</h1>")
            self.request.echo(e)
            self.request.echo("<p>(Did you install PyLucid correctly?)</p>")
            self.request.echo("<hr><address>%s</address>" % __info__)
            raise Exception(e)

        for line in RAWdata:
            # Die Values sind in der SQL-Datenbank als Type varchar() angelegt.
            # Doch auch Zahlenwerte sind gespeichert, die PyLucid doch lieber
            # auch als Zahlen sehen möchte ;)
            try:
                line["value"] = int(line["value"])
            except ValueError:
                pass

            if not self.has_key(line["section"]):
                # Neue Sektion
                self[line["section"]] = {}

            self[line["section"]][line["varName"]] = line["value"]





class URLs(dict):
    """
    Passt die verwendeten Pfade an.
    Ist ausgelagert, weil hier und auch gleichzeitig von install_PyLucid verwendet wird.
    """
    def __init__(self, request):
        dict.__init__(self)

        # shorthands
        self.request        = request
        self.environ        = request.environ
        self.page_msg       = request.page_msg
        self.preferences    = request.preferences

        self.setup()

    def setup(self):
        #~ if self.preferences["script_filename"] == "":
            #~ self.preferences["script_filename"] = self.environ["APPLICATION_REQUEST"]
            #~ "script_filename"   : os.environ['SCRIPT_FILENAME'],

        #~ if self.preferences["document_root"] == "":
            #~ self.preferences["document_root"] = os.environ['DOCUMENT_ROOT']

        #~ # Dateinamen rausschneiden
        #~ self.preferences["script_filename"] = os.path.split(self.preferences["script_filename"])[0]

        #~ self.preferences["script_filename"] = os.path.normpath(self.preferences["script_filename"])
        #~ self.preferences["document_root"]   = os.path.normpath(self.preferences["document_root"])

        # Pfad für Links festlegen
        self["real_self_url"] = self.environ["APPLICATION_REQUEST"]

        if self.preferences["poormans_modrewrite"] == True:
            self.preferences["page_ident"] = ""
        else:
            if self["real_self_url"][-1] == "/": # Slash am Ende entfernen
                self["real_self_url"] = self["real_self_url"][:-1]

            self["real_self_url"] += "/index.py"

        self["poormans_url"] = self["real_self_url"]

        self["link"] = "%s%s" % (
            self["poormans_url"], self.preferences["page_ident"]
        )
        self["base"] = "%s?page_id=%s" % (
            self["real_self_url"], -1#CGIdata["page_id"]
        )

    def items(self):
        """ Überschreibt das items() von dict, um eine Reihenfolge zu erwirken """
        values = [(len(v),k,v) for k,v in self.iteritems()]
        values.sort()

        result = []
        for _,k,v in values:
            result.append((k,v))

        return result
