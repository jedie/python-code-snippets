#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Generiert das komplette Seitenmenü mit Untermenüs in eine Baumansicht

Das Menü wird eingebunden mit dem lucid-Tag:
<lucidTag:main_menu/>

ToDo: Use the Template to generate the Sitemap. But there is no recuse-Tag
    in the django template engine :(
    - http://www.python-forum.de/topic-9655.html
    - http://groups.google.com/group/django-users/browse_thread/thread/3bd2812a3d0f7700/14f61279e0e9fd90

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: JensDiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev:$"

from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.tools.tree_generator import TreeGenerator
from PyLucid.models import Page
#from PyLucid.db.page import MenuData



class main_menu(PyLucidBaseModule):

    def lucidTag(self):
        current_page = self.context["PAGE"]
        self.current_page_id  = current_page.id

#        "name","shortcut","title"
        menu_data = Page.objects.values(
            "id", "parent", "name", "title", "shortcut"
        ).order_by("position")
#        self.page_msg(menu_data)

        if self.request.user.is_anonymous():
            menu_data = menu_data.exclude(permitViewPublic = False)
#        self.page_msg(menu_data)

        menu_data = TreeGenerator().get_tree_menu(
            menu_data, self.current_page_id
        )
#        self.page_msg(menu_data)

        menu_data = self.get_html(menu_data)
        self.response.write(menu_data)
        return

        context = {
            "menu_data" : menu_data
        }
        self._render_template(main_menu, context)

    def get_html(self, menu_data, parent=None):
        """
        [{'id': 1L,
          'level': 1,
          'name': 'index',
          'parent': 0L,
          'shortcut': 'Index',
          'title': 'index'},
         {'id': 10L,
          'level': 1,
          'name': 'Designs',
          'parent': 0L,
          'shortcut': 'Designs',
          'subitems': [{'id': 13L,
                        'level': 2,
                        'name': 'elementary',
                        'parent': 10L,
                        'shortcut': 'Elementary',
                        'title': 'elementary'},
                       {'id': 12L,
                        'level': 2,
                        'name': 'old defaul
        """
        html = (
            '<li>'
            '<a href="%(href)s" title="%(title)s">%(name)s</a>'
            '</li>'
        )
        if parent == None:
            result = ['<ul id="main_menu">']
        else:
            result = ["<ul>"]

        for entry in menu_data:
            href = []
            if parent:
                href.append(parent)

            href.append(entry["shortcut"])
            href = "/".join(href)

            entry["href"] = "".join((self.URLs["absoluteIndex"], href))

            if entry["id"] == self.current_page_id:
                entry["name"] = '<span class="current">%s</span>' % entry["name"]

            result.append(html % entry)

            if entry.has_key("subitems"):
                result.append(
                    self.get_html(entry["subitems"], parent=href)
                )

        result.append("</ul>")
        return "\n".join(result)











