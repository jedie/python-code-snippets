#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Generiert das SiteMap
<lucidTag:SiteMap/>

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

from PyLucid.tools.tree_generator import TreeGenerator
from PyLucid.models import Page

from PyLucid.system.BaseModule import PyLucidBaseModule

class SiteMap(PyLucidBaseModule):

    def lucidTag(self):
        """ Baut die SiteMap zusammen """
        
        sitemap_data = Page.objects.values(
            "id", "parent", "name", "title", "shortcut"
        ).order_by("position")
        #self.page_msg(values)
        sitemap_data = TreeGenerator().generate(sitemap_data)
        
        html = self.get_html(sitemap_data)
        self.response.write(html)

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
        result = ["<ul>"]
        
        for entry in menu_data:
            href = []
            if parent:
                href.append(parent)
                
            href.append(entry["shortcut"])
            
            href = "/".join(href)
            entry["href"] = "%s/%s/" % (self.URLs["absoluteIndex"], href)
                
            result.append(html % entry)
            
            if entry.has_key("subitems"):
                result.append(
                    self.get_html(entry["subitems"], parent=href)
                )
                
        result.append("</ul>")
        return "\n".join(result)






