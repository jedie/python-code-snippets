#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid main menu plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a nested tree menu.

    TODO:
        - Use the django template engine to generate the nested html list from
            the tree dict. But the Problem is: There is no recusive function
            available. So we must implement this. See:

    Links about a recusive function with the django template engine:
    - http://www.python-forum.de/topic-9655.html
    - http://groups.google.com/group/django-users/browse_thread/thread/3bd2812a3d0f7700/14f61279e0e9fd90

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev$
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

__version__= "$Rev$"

from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.tools.tree_generator import TreeGenerator
from PyLucid.models import Page

from django.core.cache import cache
CACHE_KEY = "main_menu"

class main_menu(PyLucidBaseModule):

    def lucidTag(self):
        """
        write the current opened tree menu
        """
        current_page = self.context["PAGE"]
        self.current_page_id  = current_page.id

        if self.request.user.is_anonymous():
            cache_key = "%s_anonymous" % CACHE_KEY
        else:
            cache_key = CACHE_KEY

        tree = cache.get(cache_key)
        if tree == None:
            # Not in the cache available
            menu_data = Page.objects.values(
                "id", "parent", "name", "title", "shortcut"
            ).order_by("position")

            if self.request.user.is_anonymous():
                menu_data = menu_data.exclude(permitViewPublic = False)

            tree = TreeGenerator(menu_data)
            cache.set(cache_key, tree, 120)
#        else:
#            self.page_msg("Menu data from the cache.")

        # Generate the opened tree dict for the given page id
        menu_data = tree.get_menu_tree(self.current_page_id)

        # Create from the tree dict a nested html list.
        menu_data = self.get_html(menu_data)

        self.response.write(menu_data)


    def get_html(self, menu_data, parent=None):
        """
        Generate a nested html list from the given tree dict.
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

