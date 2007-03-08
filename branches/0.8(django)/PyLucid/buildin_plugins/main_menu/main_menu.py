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

from django.template import Template, Context
from django.template.loader import get_template

import re, os, sys, urllib, cgi



class main_menu(PyLucidBaseModule):

    def lucidTag(self):
        self.current_page_id  = self.request.current_page.id
        
#        "name","shortcut","title"
        menu_data = Page.objects.values(
            "id", "parent", "name", "title", "shortcut"
        ).order_by("position")
        #self.page_msg(values)
        menu_data = TreeGenerator().generate(menu_data)
#        self.page_msg(menu_data)

#        # "Startpunkt" für die Menügenerierung feststellen
#        parentID = self.request.current_page.parent
#
#        # Gibt es Untermenupunkte?
#        parentID = self.check_submenu(parentID)
#
#        # Wird von self.create_menudata() "befüllt"
#        self.menudata = []
#        # Füllt self.menudata mit allen relevanten Daten
#        self.create_menudata(parentID)
#
#        # Ebenen umdrehen, damit das Menü auch richtig rum
#        # dargestellt werden kann
#        self.menudata.reverse()
#
#        # Generiert das Menü aus self.menudata
#        menu_data = self.make_menu()

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
            

    def where_filter(self, where_rules):
        """
        Erweitert das SQL-where Statement um das Rechtemanagement zu
        berücksichtigen.
        Selbe Funktion ist auch bei sub_menu vorhanden
        """
        where_rules.append(("showlinks",1))
        #~ if not self.session.get("isadmin", False):
            #~ where_rules.append(("permitViewPublic",1))

        return where_rules

    def check_submenu(self, parentID, internal=False):
        """
        Damit sich das evtl. vorhandene Untermenüpunkt "aufklappt" wird
        nachgesehen ob ein Menüpunkt als ParentID die aktuelle SeitenID hat.
        """
        where_filter = self.where_filter( [("parent",self.current_page_id)] )
        # Gibt es Untermenupunkte?
        result = self.db.select(
                select_items    = ["parent"],
                from_table      = "page",
                where           = where_filter,
                limit           = (0,1)
            )
        
        if not result:
            # Es gibt keine höhere Ebene (keine Untermenupunkte)
            return parentID
        else:
            # Als startpunkt wird die ParentID eines Untermenupunktes übergeben
            return result[0]["parent"]

    def create_menudata(self, parentID):
        """
        Hohlt die relevanten Menüdaten aus der DB in einer Rekursiven-Schleife
        """
        # Alle Daten der aktuellen Ebene hohlen
        parents = self.db.select(
                select_items    = ["id","name","shortcut","title","parent"],
                from_table      = "page",
                where           = self.where_filter( [("parent",parentID)] ),
                order           = ("position","ASC")
            )
        self.menudata.append( parents )

        # Hohlt die parentID, um zur nächte Ebene zurück gehen zu können
        parent = self.db.select(
                select_items    = ["parent"],
                from_table      = "page",
                where           = [ ("id",parentID) ]
            )
        if parent:
            # Unterste Ebene noch nicht erreicht -> rekursiver Aufruf
            self.create_menudata(parent[0]["parent"])

    def make_menu(self, menulevel=0, parentname=""):
        """
        Erstellt das Menü aus self.menudata in einer Rekursiven-Schleife
        """
        result = []

        # Daten der Aktuellen Menüebene
        leveldata = self.menudata[menulevel]

        if len(self.menudata) > (menulevel+1):
            # Es gibt noch eine höhere Menu-Ebene
            try:
                higher_level_parent = self.menudata[menulevel+1][0]["parent"]
            except IndexError:
                # Aber nicht, wenn die aktuelle Seite "versteckt" ist
                higher_level_parent = False
        else:
            # Es gibt keine höhere Ebene
            higher_level_parent = False

        for menuitem in leveldata:
            name = menuitem["name"]
            title = menuitem["title"]
            if title == None:
                title = name

            link = "%s/%s" % (parentname, menuitem["shortcut"])
            linkURL = link#self.URLs.pageLink(link)

            htmlLink = {
                "level"     : menulevel,
                "href"      : linkURL,
                "name"      : name,
                "title"     : title
            }

            if menuitem["id"] == self.current_page_id:
                # Der aktuelle Menüpunkt ist der "angeklickte"
                htmlLink["is_current_page"] = True

            if higher_level_parent != False:
                # Generell gibt es noch eine höhere Ebene

                if menuitem["id"] == higher_level_parent:
                    # Es wurde der Menüpunkt erreicht, der das Untermenü
                    # "enthält", deswegen kommt ab hier erstmal das
                    # Untermenü rein
                    children = self.make_menu(menulevel+1, link)
                    htmlLink["children"] = children

            result.append(htmlLink)

        return result










