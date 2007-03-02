#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Generiert das komplette Seitenmenü mit Untermenüs in eine Baumansicht

Das Menü wird eingebunden mit dem lucid-Tag:
<lucidTag:main_menu/>


x = {
    'value':1, 'children': [
        { 'value': 2, 'children': []},
        {'value' : 3, 'children': [{ 'value':4, 'children':[] }]}
]}

"""

from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.system.tools.tree_generator import TreeGenerator
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
        context = {
            "menu_data" : menu_data
        }

        #~ self.templates.write("main_menu", )
        t = get_template("PyLucid/buildin_plugins/main_menu/main_menu.html")
        #~ t = Template("main_menu")
        c = Context(context)
        html = t.render(c)
        return html
#        return HttpResponse(html)

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










