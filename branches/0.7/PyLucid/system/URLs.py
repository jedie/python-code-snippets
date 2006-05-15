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
        """Pfad für Links festlegen"""

        self["command"] = None # Wird vom Module-Manager festgelegt
        self["action"] = None # Wird vom Module-Manager festgelegt

        #~ self["real_self_url"] = self.environ["APPLICATION_REQUEST"]

        self["real_self_url"] = "%s://%s%s" % (
            self.environ.get('wsgi.url_scheme', "http"),
            self.environ['HTTP_HOST'],
            self.environ['SCRIPT_ROOT'],
        )

        preferences = self.preferences
        if preferences["poormans_modrewrite"] == True:
        #~ if self.preferences["poormans_modrewrite"] == True:
            self.preferences["page_ident"] = ""

        self["link"] = self["base"] = self.environ.get('SCRIPT_NAME')

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
        temp = []
        for k,v in self.iteritems():
            try:
                temp.append((len(v),k,v))
            except TypeError:
                # z.B. bei v == None ;)
                temp.append((0,k,v))

        temp.sort()

        result = []
        for _,k,v in temp:
            result.append((k,v))

        return result

    #_________________________________________________________________________

    #~ def __setitem__(self, item, value):
        #~ """ Nur für Debuging!!! """
        #~ msg = ""
        #~ try:
            #~ import inspect
            #~ # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
            #~ filename = inspect.stack()[1][1].split("/")[-1][-20:]
            #~ msg += "%s line %3s" % (filename, inspect.stack()[1][2])
        #~ except Exception, e:
            #~ msg += "<small>(inspect Error: %s)</small> " % e

        #~ self.page_msg(
            #~ "setitem from '%s': item %s - value %s" % (msg, item, value)
        #~ )

        #~ dict.__setitem__(self, item, value)

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

    def get_commandURLPrefix(self):
        if self["base"] == "":
            base = "/"
        else:
            base = self["base"]

        return base + self.request.staticTags['commandURLprefix']

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("path debug:")
        self.page_msg("path_info:", self.environ["PATH_INFO"])
        #~ for k,v in self.iteritems():
            #~ self.page_msg(k,v)
        #~ self.page_msg(self)
        for k,v in self.items():
            self.page_msg(
                "- %15s: '%s'" % (k,v)
            )






