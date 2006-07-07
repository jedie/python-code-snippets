#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das SiteMap
<lucidTag:SiteMap/>
"""

__version__="0.1"

__history__="""
v0.1
    - PyLucid["URLs"]
    - Anpassung an neuen ModuleManager
v0.0.5
    - Link wird nun auch vom ModulManager verwendet.
    - Testet page-title auch auf None
v0.0.4
    - Anpassung an neuen ModulManager
v0.0.3
    - Neue Tags für CSS
v0.0.2
    - "must_login" und "must_admin" für Module-Manager hinzugefügt
v0.0.1
    - erste Version
"""

import cgitb;cgitb.enable()
import cgi, urllib



from PyLucid.system.BaseModule import PyLucidBaseModule

class SiteMap(PyLucidBaseModule):

    def lucidTag(self):
        """ Baut die SiteMap zusammen """
        self.data = self.db.get_sitemap_data()

        self.parent_list = self.get_parent_list()
        #~ return str( self.parent_l    ist )

        self.link  = '<a href="%(link)s">%(name)s</a>'

        self.response.write('<div id="SiteMap">\n')
        self.make_sitemap()
        self.response.write('</div>\n')

    def get_parent_list(self):
        parents = []
        for site in self.data:
            if not site["parent"] in parents:
                parents.append(site["parent"])
        return parents

    def make_sitemap(self, parentname = "", id = 0, deep = 0):
        self.response.write(
            '<ul class="id_%s deep_%s">\n' % (id, deep)
        )
        for site in self.data:
            if site["parent"] == id:
                self.response.write(
                    '<li class="id_%s deep_%s">' % (site["id"], deep)
                )

                link = "%s/%s" % (parentname, site["shortcut"])
                linkURL = self.URLs.pageLink(link)

                self.response.write(
                    self.link % {
                        "link"  : linkURL,
                        "name"  : cgi.escape(site["name"]),
                    }
                )

                if (site["title"] != "") and \
                        (site["title"] != None) and \
                        (site["title"] != site["name"]):
                    self.response.write(
                        " - %s" % cgi.escape(site["title"])
                    )

                self.response.write("</li>\n")

                if site["id"] in self.parent_list:
                    self.make_sitemap(link, site["id"], deep +1)

        self.response.write("</ul>\n")






