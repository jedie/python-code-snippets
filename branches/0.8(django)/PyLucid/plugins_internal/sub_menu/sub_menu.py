#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
<lucidTag:sub_menu/>
Generiert Links aller Unterseiten

Last commit info:
----------------------------------
$LastChangedDate: $
$Rev: $
$Author: JensDiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev: $"

# Python-Basis Module einbinden
import re, os, sys, urllib, cgi



from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.models import Page

TEMPLATE = """
<ul>
{% for page in sub_pages %}
  <li><a href="{{ page.shortcut }}">{{ page.name|escape }}</a></li>
{% endfor %}
</ul>
"""

class sub_menu(PyLucidBaseModule):

    def lucidTag( self ):
        """
        """
        current_page_id = self.request.current_page.id
        sub_pages = Page.objects.filter(
            parent__exact=current_page_id, showlinks__exact=1
        )
        if self.request.user.username != "":
            sub_pages = sub_pages.filter(permitViewPublic__exact=1)

        sub_pages = sub_pages.order_by('position')

        sub_pages = sub_pages.values("name", "shortcut", "title")

        prelink = self.db.page.get_link_by_id(current_page_id)

        context = {
            "sub_pages": sub_pages,
            "prelink": prelink,
        }
        self._render_string_template(TEMPLATE, context)#, debug=True)
















