#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verwaltung der verfügbaren URLs
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.1"

__history__="""
v0.1
    - erste Version
"""


import os



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
        #~ self["real_self_url"] = self.environ["APPLICATION_REQUEST"]
        self["real_self_url"] = self.environ.get('SCRIPT_NAME',"")

        if self.preferences["poormans_modrewrite"] == True:
            self.preferences["page_ident"] = ""

        self["poormans_url"] = self["real_self_url"]

        self["link"] = self["base"] = self["poormans_url"]

        #~ self["link"] = "%s?%s=" % (
            #~ self["poormans_url"], self.preferences["page_ident"]
        #~ )
        #~ self["base"] = "%s?page_id=%s" % (
            #~ self["real_self_url"], -1#CGIdata["page_id"]
        #~ )

    def items(self):
        """ Überschreibt das items() von dict, um eine Reihenfolge zu erwirken """
        values = [(len(v),k,v) for k,v in self.iteritems()]
        values.sort()

        result = []
        for _,k,v in values:
            result.append((k,v))

        return result

    def make_command_link(self, modulename, methodname):
        return "/".join(
            (
                self["base"],
                self.preferences["commandURLprefix"],
                modulename,
                methodname
            )
        )

    def debug(self):
        self.page_msg("path debug:")
        for k,v in self.items():
            self.page_msg(
                "- %15s:%s" % (k,v)
            )






