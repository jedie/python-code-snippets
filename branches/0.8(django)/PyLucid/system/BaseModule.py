#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Basis Modul von den andere Module erben können

Bsp.:

from PyLucid.system.BaseModule import PyLucidBaseModule

class Bsp(PyLucidBaseModule):
    def __init__(self, *args, **kwargs):
        super(Bsp, self).__init__(*args, **kwargs)



Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import posixpath, os

from django.contrib.sites.models import Site

from PyLucid import settings
from PyLucid.db import DB_Wrapper


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
        if self["scriptRoot"] == "": self["scriptRoot"] = "/"

        self["docRoot"] = self.addSlash(posixpath.split(self["scriptRoot"])[0])

        self["absoluteIndex"] = self["hostname"] + self["scriptRoot"]
        
        self["commandBase"] = posixpath.join(
            self["scriptRoot"], settings.COMMAND_URL_PREFIX
        )

    #__________________________________________________________________________

    def commandLink(self, modulename, methodname="", args="", addSlash=True):
        args = self._prepage_args(args)
        link = posixpath.join(
            self["commandBase"], str(self.request.current_page.id), modulename, methodname, args
        )

        if addSlash:
            link = self.addSlash(link)
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


#______________________________________________________________________________


class PyLucidBaseModule(object):
    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        self.db = DB_Wrapper(request.page_msg)
        self.page_msg = request.page_msg
        
        self.URLs = URLs(request)
        self.URLs.debug()

    #~ def absolute_link(self, url):
        #~ if isinstance(url, list):
            #~ url = "/".join(url)

        #~ url = posixpath.join(Site.objects.get_current().domain, url)

        #~ return 'http://%s' % url
