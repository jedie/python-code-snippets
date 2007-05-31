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

class sub_menu(PyLucidBaseModule):

    def lucidTag( self ):
        """
        """
        current_page_id = self.current_page.id

        sub_pages = Page.objects.filter(
            parent__exact=current_page_id, showlinks__exact=1
        )
#        self.page_msg(sub_pages)

        if self.request.user.is_anonymous():
            sub_pages = sub_pages.exclude(permitViewPublic = False)

#        self.page_msg(sub_pages)

        sub_pages = sub_pages.order_by('position')

        sub_pages = sub_pages.values("name", "shortcut", "title")

        prelink = self.db.page.get_link_by_id(current_page_id)

        context = {
            "sub_pages": sub_pages,
            "prelink": prelink,
        }
        self._render_template("sub_menu", context)
















