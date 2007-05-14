#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
URL class
"""

import os, posixpath

from PyLucid import settings

class URLs(dict):
    def __init__(self, request):
        self.request = request
        self.page_msg = request.page_msg

        self.setup_URLs()

    def setup_URLs(self):
        """
        Pfad für Links festlegen
        """
        self["cwd"] = os.getcwdu()
        self["host"] = self.request.META['HTTP_HOST']
        self["hostname"] = "%s://%s" % (
            self.request.META.get('wsgi.url_scheme', "http"),
            self["host"],
        )

        self["scriptRoot"] = self.request.META.get("SCRIPT_NAME", "/")

        self["docRoot"] = self.addSlash(posixpath.split(self["scriptRoot"])[0])

        self["absoluteIndex"] = self.addSlash(
            "".join((self["hostname"], self["scriptRoot"]))
        )
#        self.page_msg("Absolute Index: '%s'" % self["absoluteIndex"])

        self["commandBase"] = "/".join((
            self["scriptRoot"], settings.COMMAND_URL_PREFIX,
            str(self.request.current_page_id)
        ))
        self["adminBase"] = "/".join((
            self["scriptRoot"], settings.ADMIN_URL_PREFIX
        ))

    #__________________________________________________________________________

    def commandLink(self, modulename, methodname="", args="", addSlash=True):
        args = self._prepage_args(args)
        link = "/".join((
            self["commandBase"], modulename, methodname, args
        ))

        if addSlash:
            link = self.addSlash(link)
        return link

    def adminLink(self, url):
        link = "/".join((
            self["adminBase"], url
        ))
        return link

    #__________________________________________________________________________

    def addSlash(self, path):
        """
        >>> addSlash("/noSlash")
        '/noSlash/'
        >>> addSlash("/hasSlash/")
        '/hasSlash/'
        """
        if path=="" or path[-1]!="/":
            return path+"/"
        else:
            return path


    def _prepage_args(self, args):
        if isinstance(args, (list, tuple)):
            return "/".join([str(i) for i in args])
        else:
            return str(args)

    #__________________________________________________________________________

    def debug(self):
        self.page_msg("URLs debug:")
        for k,v in self.items():
            self.page_msg(" - %15s: '%s'" % (k,v))