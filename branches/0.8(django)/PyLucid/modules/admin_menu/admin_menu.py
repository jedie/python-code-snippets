#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

"""
the administration top menu

TODO: edit_page_link should use pageadmin.edit_page - a inline editing
"""

from StringIO import StringIO

from PyLucid.system.tinyTextile import TinyTextileParser

from PyLucid.system.BaseModule import PyLucidBaseModule

class admin_menu(PyLucidBaseModule):

    def lucidTag( self ):
        """
        Front menu anzeigen
        """
        edit_link = self.URLs.adminLink(
            "PyLucid/page/%s/" % self.request.current_page_id
        )

        context = {
            "login": self.request.static_tags.get_login_link(),
#            "edit_page_link": self.URLs.commandLink("pageadmin", "edit_page"),
            "edit_page_link": edit_link,
            "new_page_link": self.URLs.adminLink("/_admin/PyLucid/page/add/"),
            "sub_menu_link": self.URLs.commandLink("admin_menu", "sub_menu"),
        }
        self._render_template("top_menu", context)

    def sub_menu(self):
        context = {"commandURLprefix": self.URLs["commandBase"]}
#        self.page_msg(context)

        html = self._get_rendered_template("sub_menu", context)

        p = TinyTextileParser(self.response, self.request, self.response)
        p.parse(html)
