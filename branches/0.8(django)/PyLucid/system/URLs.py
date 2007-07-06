#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid URLs
    ~~~~~~~~~~~~

    The URLs class has some usefull methods for plugins to build links.

    The view put a instance in context["URLs"]. The BasePlugin bind the class
    to self. So every plugin can easy access the methods with self.URLs.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

import os, posixpath

from PyLucid import settings

class URLs(dict):
    def __init__(self, context):
        self.context     = context
        self.request     = context["request"]
        self.page_msg    = context["page_msg"]

        self.current_plugin = None

        self.setup_URLs()

    def setup_URLs(self):
        """
        Set some base urls, which are same for every Request and inside the
        response would be built.
        """
        self["cwd"] = os.getcwdu()
        self["host"] = self.request.META['HTTP_HOST']
        self["hostname"] = "%s://%s" % (
            self.request.META.get('wsgi.url_scheme', "http"),
            self["host"],
        )

#        self["scriptRoot"] = self.request.META.get("SCRIPT_NAME", "/")
        self["scriptRoot"] = "/"

        self["docRoot"] = self.addSlash(posixpath.split(self["scriptRoot"])[0])

        self["absoluteIndex"] = self.addSlash(
            "".join((self["hostname"], self["scriptRoot"]))
        )
        self["adminBase"] = posixpath.join(
            self["scriptRoot"], settings.ADMIN_URL_PREFIX
        )

    #__________________________________________________________________________

    def _generate_url(self, parts, args, addSlash):
        """
        Generate the link from the given parts and args.
        """
        if args != None:
            # Extend parts with the args.
            if isinstance(args, (list, tuple)):
                args = [str(i) for i in args]
                parts += args
            else:
                parts.append(str(args))

        # Join parts + args together.
        link = "/".join(parts)

        if addSlash:
            link = self.addSlash(link)
        return link

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

    #__________________________________________________________________________

    def get_command_base(self):
        """
        Generate the command base for self.commandLink() and self.methodLink().
        Note: This is extra not build in self.setup_URLs(), because a Plugin
        can change the current page!
        e.g.: After a new page created, PyLucid goto this new page and every
        command/method link should use the new page id.
        """
        return posixpath.join(
            self["scriptRoot"], settings.COMMAND_URL_PREFIX,
            str(self.context["PAGE"].id)
        )

    def commandLink(self, plugin_name, method_name, args=None, addSlash=True):
        """
        generate a command link to the given plugin and method
        - args can be a list, tuple or a string.
        - addSlash=False if the url has a filename.
        """
        command_base = self.get_command_base()
        parts = [command_base, plugin_name, method_name]
        return self._generate_url(parts, args, addSlash)

    def methodLink(self, method_name, args=None, addSlash=True):
        """
        generate a link to a other method in the current used plugin.
        - args can be a list, tuple or a string.
        - addSlash=False if the url has a filename.
        """
        command_base = self.get_command_base()
        parts = [command_base, self.current_plugin, method_name]
        return self._generate_url(parts, args, addSlash)

    def adminLink(self, url):
        """
        generate a link into the django admin panel.
        """
        link = "/".join((
            self["adminBase"], url
        ))
        return link

    #__________________________________________________________________________

    def debug(self):
        """
        write debug information into the page_msg
        """
        self.page_msg("URLs debug:")
        for k,v in self.items():
            self.page_msg(" - %15s: '%s'" % (k,v))