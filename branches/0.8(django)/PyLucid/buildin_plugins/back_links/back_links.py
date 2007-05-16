#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
<lucidTag:back_links/>
Generiert eine horizontale zurück-Linkleiste

Created by Jens Diemer

GPL-License
"""

import cgi

from PyLucid.system.BaseModule import PyLucidBaseModule

from PyLucid.models import Page

class back_links(PyLucidBaseModule):
    indexlink = '<a href="/">Index</a>'
    backlink  = '<a href="%(url)s">%(title)s</a>'

    def lucidTag( self ):
        """
        generate the backlinks
        """
        current_page = self.context["PAGE"]
        try:
            parent_page = current_page.parent
        except Page.DoesNotExist:
            # The parent id is 0 and there is no page with id 0
            return ""

        if parent_page.id == 0: # No higher-ranking page
            return ""

        try:
            # Link-Daten aus der DB hohlen
            data = self.backlink_data(parent_page.id)
        except IndexError, e:
            self.response.write("[back links error: %s]" % e)
            return

        self.make_links( data )

    def backlink_data(self, page_id):
        """
        get the link data from the db
        """
        data = []
        urls = [""]

        while page_id != 0:
            page = Page.objects.get(id=page_id)
            urls.append(page.shortcut)

            title = page.title
            if title in (None, ""):
                title = page.name

            data.append({
                    "title": title,
                    "url": "/".join(urls),
            })

            try:
                page_id = page.parent.id
            except Page.DoesNotExist:
                # The parent id is 0 and there is no page with id 0
                break

        data.reverse()

        return data

    def make_links( self, data ):
        """
        write the links directly into the page
        """
        self.response.write(self.indexlink)

        for link_data in data:
            link = self.backlink % {
                "url": link_data["url"],
                "title": cgi.escape( link_data["title"] ),
            }
            self.response.write(" &lt; %s" % link)







