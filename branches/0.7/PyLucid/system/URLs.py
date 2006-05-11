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


import os, posixpath, urllib



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

        self.setup_path_info()
        self.setup_URLs()


    def setup_path_info(self):
        pathInfo = self.request.environ.get('PATH_INFO', '/')
        #~ self.response.write("OK: %s" % pathInfo)
        #~ return self.response

        pathInfo = urllib.unquote(pathInfo)
        try:
            pathInfo = unicode(pathInfo, "utf-8")
        except:
            pass

        pathInfo = pathInfo.strip("/")
        pathInfo = pathInfo + "/"
        self.request.environ["PATH_INFO"] = pathInfo

    def setup_URLs(self):
        # Pfad für Links festlegen
        #~ self["real_self_url"] = self.environ["APPLICATION_REQUEST"]
        self["real_self_url"] = self.environ.get('SCRIPT_NAME')

        preferences = self.preferences
        if preferences["poormans_modrewrite"] == True:
        #~ if self.preferences["poormans_modrewrite"] == True:
            self.preferences["page_ident"] = ""

        self["link"] = self["base"] = self["real_self_url"]

        #~ self["poormans_url"] = self["real_self_url"]

        pathInfo = self.environ["PATH_INFO"].split("&")[0]

        if self["base"] == "":
            self["current_action"] = "/%s" % pathInfo
        else:
            self["current_action"] = "/".join(
                (self["base"], pathInfo)
            )


    def items(self):
        """ Überschreibt das items() von dict, um eine Reihenfolge zu erwirken """
        values = [(len(v),k,v) for k,v in self.iteritems()]
        values.sort()

        result = []
        for _,k,v in values:
            result.append((k,v))

        return result

    #_________________________________________________________________________

    def make_command_link(self, modulename, methodname):
        return "/".join(
            (
                self["base"],
                self.preferences["commandURLprefix"],
                modulename,
                methodname
            )
        ) + "/"

    def make_action_link(self, methodname):
        return "%s%s/" % (
            self["command"], methodname
        )

    def make_current_action_link(self, info):
        return "%s%s/" % (
            self['current_action'], info
        )

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("path debug:")
        self.page_msg("path_info:", self.environ["PATH_INFO"])
        for k,v in self.items():
            self.page_msg(
                "- %15s: '%s'" % (k,v)
            )






