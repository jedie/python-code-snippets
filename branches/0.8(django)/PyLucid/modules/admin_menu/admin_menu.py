#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

"""
the administration top menu

TODO: edit_page_link should use pageadmin.edit_page - a inline editing
"""

from PyLucid.system.BaseModule import PyLucidBaseModule

class admin_menu(PyLucidBaseModule):

    def lucidTag(self):
        """
        Front menu anzeigen
        """
        current_page = self.context["PAGE"]
        current_page_id  = current_page.id
        edit_link = self.URLs.adminLink("PyLucid/page/%s/" % current_page_id)

        context = {
            "login": self.context["login_link"],
#            "edit_page_link": self.URLs.commandLink("pageadmin", "edit_page"),
            "edit_page_link": edit_link,
            "new_page_link": self.URLs.adminLink("/_admin/PyLucid/page/add/"),
            "sub_menu_link": self.URLs.commandLink("admin_menu", "sub_menu"),
        }
        self._render_template("top_menu", context)

    def sub_menu(self):
        context = {"commandURLprefix": self.URLs["commandBase"]}
#        self.page_msg(context)

        html = self._render_template("sub_menu", context)



