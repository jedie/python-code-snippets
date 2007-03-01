#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

"""
Erzeugt das Administration-Menü
(ehemals front_menu aus dem alten page-renderer)

<lucidTag:admin_menu/>
Sollte im Template für jede Seite eingebunden werden.
"""

from django.template import Template, Context
from django.template.loader import get_template

from PyLucid.system.BaseModule import PyLucidBaseModule

class admin_menu(PyLucidBaseModule):

    def lucidTag( self ):
        """
        Front menu anzeigen
        """
        context = {
            "login": self.request.static_tags.get_login_link(),
            "edit_page_link": self.URLs.commandLink("pageadmin", "edit_page"),
            "new_page_link": self.URLs.commandLink("pageadmin", "new_page"),
            "sub_menu_link": self.URLs.commandLink("admin_menu", "sub_menu"),
        }
#        self.templates.write("top_menu", context)
        
        t = get_template("PyLucid/modules/admin_menu/top_menu.html")
        c = Context(context)
        html = t.render(c)
        return html

    def sub_menu( self ):

        context = {"commandURLprefix": self.URLs["commandBase"]}
        #~ self.page_msg(context)

        self.templates.write("sub_menu", context)








