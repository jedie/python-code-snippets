#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
Alle vorgefertigten Methoden, die aktiv Daten in der DB verändern und
über einfache SELECT Befehle hinausgehen

Last commit info:
----------------------------------
LastChangedDate: $LastChangedDate$
Revision.......: $Rev$
Author.........: $Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__ = "$Rev$"


import pickle, sys, datetime, md5

from PyLucid.system.SQL_passive_statements import passive_statements
from PyLucid.system.exceptions import *

debug = False

class active_statements(passive_statements):
    """
    Erweitert den allgemeinen SQL-Wrapper (mySQL.py) um
    spezielle PyLucid-Funktionen.
    """
    #~ def __init__(self, *args, **kwargs):
        #~ super(active_statements, self).__init__(*args, **kwargs)

    #_________________________________________________________________________

    def get_page_link_by_id(self, page_id):
        """ Generiert den absolut-Link zur Seite """
        data = []

        while page_id != 0:
            result = self.select(
                    select_items    = ["shortcut","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append(result["shortcut"])

        # Liste umdrehen
        data.reverse()

        #~ data = [urllib.quote_plus(i) for i in data]

        link = "/".join(data)
        link = self.URLs.pageLink(link)
        return link

    #_________________________________________________________________________
    ## Funktionen für das ändern der Seiten

    def delete_page(self, page_id_to_del):
        first_page_id = self.get_first_page_id()
        if page_id_to_del == first_page_id:
            raise IndexError("The last page cannot be deleted!")

        self.delete(
            table = "pages",
            where = ("id",page_id_to_del),
            limit=1
        )

    def getUniqueShortcut(self, page_name, page_id = None):
        """
        Bearbeitet den gegebenen page_name so, das er Einmalig und "url-safe"
        ist.
        Ist eine page_id angegeben, wird der shortcut von dieser Seite
        ignoriert (wird beim edit page/preview benötigt!)
        """
        shortcutList = self.get_shortcutList(page_id)

        uniqueShortcut = self.tools.getUniqueShortcut(page_name, shortcutList)
        return uniqueShortcut

    def insert_new_page(self, page_data):
        page_data = self.__add_data(page_data)
        self.insert(
            table   = "pages",
            data    = page_data,
        )
        return self.cursor.lastrowid

    #_________________________________________________________________________
    ## Funktionen für das ändern des Looks (Styles, Templates usw.)

    def update_style(self, style_id, style_data):

        # lastupdatetime, lastupdateby hinzufügen:
        style_data = self.__add_data(style_data, add_createtime=False)

        self.update(
            table   = "styles",
            data    = style_data,
            where   = ("id",style_id),
            limit   = 1
        )

    def new_style(self, style_data):
        # createtime, lastupdatetime, lastupdateby hinzufügen:
        style_data = self.__add_data(style_data)

        style_data["description"] = style_data.get("description", None)

        self.insert("styles", style_data)

    def delete_style(self, style):
        if type(style) == str:
            # Der style-Name wurde angegeben
            style_id = self.select(
                select_items    = ["id"],
                from_table      = "styles",
                where           = ("name", style)
            )[0]["id"]
        else:
            style_id = style

        self.delete(
            table   = "styles",
            where   = ("id",style_id),
            limit   = 1
        )

    def delete_style_by_plugin_id(self, plugin_id):
        style_names = self.select(
            select_items    = ["name"],
            from_table      = "styles",
            where           = ("plugin_id",plugin_id),
        )
        self.delete(
            table           = "styles",
            where           = ("plugin_id",plugin_id),
            limit           = 99,
        )
        style_names = [i["name"] for i in style_names]
        return style_names

    def update_template(self, template_id, template_data):

        # lastupdatetime, lastupdateby hinzufügen:
        template_data = self.__add_data(template_data, add_createtime=False)

        self.update(
            table   = "templates",
            data    = template_data,
            where   = ("id",template_id),
            limit   = 1
        )

    def new_template(self, template_data):

        # createtime, lastupdatetime, lastupdateby hinzufügen:
        template_data = self.__add_data(template_data)

        self.insert("templates", template_data)

    def delete_template(self, template_id):
        self.delete(
            table   = "templates",
            where   = ("id",template_id),
            limit   = 1
        )

    def change_page_position(self, page_id, position):
        self.update(
            table   = "pages",
            data    = {"position":position},
            where   = ("id",page_id),
            limit   = 1
        )

    #_____________________________________________________________________________
    ## Preferences

    def set_preferences(self, section, varName, value):
        """
        Ändert den Wert von einem Preferences-Eintrag
        """
        change_dict = {"value": value}
        self.change_preferences(section, varName, change_dict)

    def change_preferences(self, section, varName, change_dict):
        """
        Ändern eines x-beliebigen Tabellen-Feldes von einem Preference-Eintrag
        """
        id = self.get_one_preference(section, varName, select_items=["id"])
        id = id["id"]

        self.update(
            table   = "preferences",
            data    = change_dict,
            where   = ("id",id),
            limit   = 1
        )

    #_________________________________________________________________________
    ## InterneSeiten

    def update_internal_page(self, internal_page_name, page_data):

        # lastupdatetime, lastupdateby hinzufügen:
        page_data = self.__add_data(page_data, add_createtime=False)

        # Speichern
        self.update(
            table   = "pages_internal",
            data    = page_data,
            where   = ("name",internal_page_name),
            limit   = 1
        )

    def new_internal_page(self, data, lastupdatetime=None):
        """
        Erstellt eine neue interne Seite.
        (installation!)
        """

        # Zu IDs Auflösen
        data["markup"] = self.get_markup_id(data["markup"])
        data["template_engine"] = \
                        self.get_template_engine_id(data["template_engine"])

        # createtime, lastupdatetime, lastupdateby hinzufügen:
        data = self.__add_data(data)

        self.insert("pages_internal", data)

    def delete_internal_page(self, name):
        self.delete(
            table = "pages_internal",
            where = ("name", name),
            limit = 1,
        )
        #~ self.delete_blank_pages_internal_categories()

    def delete_internal_page_by_plugin_id(self, plugin_id):
        #~ print "plugin_id:", plugin_id
        page_names = self.select(
            select_items    = ["name"],
            from_table      = "pages_internal",
            where           = ("plugin_id", plugin_id),
        )
        #~ print "page_names:", page_names
        self.delete(
            table           = "pages_internal",
            where           = ("plugin_id", plugin_id),
            limit           = 99,
        )
        page_names = [i["name"] for i in page_names]
        return page_names

    #_________________________________________________________________________
    ## Userverwaltung

    def add_new_user(self, name, realname, email, admin):
        """
        Einen neuen User eintragen (ohne Passwort!)
        Liefert die ID des neuen Users zurück
        """
        username_md5 = md5.new(name).hexdigest()
        data  = {
            "name"          : name,
            "realname"      : realname,
            "username_md5"  : username_md5,
            "email"         : email,
            "admin"         : admin
        }

        # createtime, lastupdatetime, lastupdateby hinzufügen:
        data = self.__add_data(data)

        self.insert("md5users", data)

        return self.cursor.lastrowid

    def update_userdata(self, id, name, realname, email, admin):
        """ Editierte Userdaten wieder speichern """
        data={
            "name": name, "realname": realname,
            "email": email, "admin": admin
        }

        # lastupdatetime, lastupdateby hinzufügen:
        data = self.__add_data(data, add_createtime=False)

        self.update(
            "md5users", data,
            where   = ("id",id),
            limit   = 1
        )

    def change_username(self, old_username, new_username):
        """
        Ändern des Username.
        """
        self.update(
            "md5users",
            data    = {"name": new_username},
            where   = ("name", old_username),
            limit   = 1
        )

    def update_userdata_by_name(self, **kwargs):
        """ Editierte Userdaten wieder speichern """
        data = kwargs
        username = data.pop("name")

        # lastupdatetime, lastupdateby hinzufügen:
        data = self.__add_data(data, add_createtime=False)

        self.update(
            table   = "md5users",
            data    = data,
            where   = ("name",username),
            limit   = 1,
            #~ debug = True,
        )

    def del_user(self, id):
        """ Löschen eines Users """
        self.delete(
            table   = "md5users",
            where   = ("id", id),
            limit   = 1
        )

    #_________________________________________________________________________
    ## Module / Plugins

    def activate_module(self, id):
        self.update(
            table   = "plugins",
            data    = {"active": 1},
            where   = ("id",id),
            limit   = 1
        )

    def deactivate_module(self, id):
        self.update(
            table   = "plugins",
            data    = {"active": 0},
            where   = ("id",id),
            limit   = 1
        )

    def install_plugin(self, module_data):
        """
        Installiert ein neues Plugin/Modul.
        Wichtig: Es wird extra jeder Wert herraus gepickt, weil in module_data
            mehr Keys sind, als in diese Tabelle gehören!!!
        """
        active = module_data["active"]
        if module_data.get("essential_buildin", False) == True:
            active = -1
        elif active == True:
            active = 1
        else:
            active = 0

        data  = {
            "package_name"              : module_data["package_name"],
            "module_name"               : module_data["module_name"],
            "version"                   : module_data["version"],
            "author"                    : module_data["author"],
            "url"                       : module_data["url"],
            "description"               : module_data["description"],
            "long_description"          : module_data["long_description"],
            "active"                    : active,
            "debug"                     : module_data["module_manager_debug"],
            "SQL_deinstall_commands"    : module_data["SQL_deinstall_commands"],
            "plugin_cfg"                : module_data["plugin_cfg"],
        }

        self.insert("plugins", data)
        return self.cursor.lastrowid

    def register_plugin_method(self, plugin_id, method_name, method_cfg):

        where= [("plugin_id", plugin_id), ("method_name", method_name)]

        if self.select(["id"], "plugindata", where):
            raise IntegrityError(
                "Duplicate entry '%s' with ID %s!" % (method_name, plugin_id)
            )

        # True und False in 1 und 0 wandeln
        for k,v in method_cfg.iteritems():
            if v == True:
                method_cfg[k] = 1
            elif v == False:
                method_cfg[k] = 0

        # Daten vervollständigen
        method_cfg.update({
            "plugin_id"     : plugin_id,
            "method_name"   : method_name,
        })

        self.insert(
            table = "plugindata",
            data  = method_cfg,
        )
        return self.cursor.lastrowid

    def delete_plugin(self, id):
        try:
            self.delete(
                table = "plugins",
                where = ("id", id),
                limit = 999,
            )
        except Exception, e:
            raise IntegrityError(
                    "Can't delete plugin! ID: %s (%s: %s)" % (
                    id, sys.exc_info()[0],":", e
                )
            )

    def delete_plugindata(self, plugin_id):
        """
        Löscht alle Methoden zu einem Plugin
        """
        self.delete(
            table = "plugindata",
            where = ("plugin_id", plugin_id),
            limit = 999,
        )

    def delete_plugindata(self, plugin_id):
        """
        Löscht alle Methoden zu einem Plugin
        """
        self.delete(
            table = "plugindata",
            where = ("plugin_id", plugin_id),
            limit = 999,
        )

    #_________________________________________________________________________
    ## L10N

    #~ def set_L10N(self, lang, key):

    #_________________________________________________________________________
    ## Allgemeine Funktionen

    def __add_data(self, data_dict, add_createtime=True):
        """
        Fügt in data_dict "lastupdatetime", "createtime" und "lastupdateby"
        hinzu.

        # createtime, lastupdatetime, lastupdateby hinzufügen:
        data = self.__add_data(data)

        # lastupdatetime, lastupdateby hinzufügen:
        data = self.__add_data(data, add_createtime=False)

        """
        # Daten einfügen
        timestamp = datetime.datetime.now()
        data_dict["lastupdatetime"] = timestamp

        if add_createtime:
            data_dict["createtime"] = timestamp

        try:
            data_dict["lastupdateby"] = self.session['user_id']
        except AttributeError:
            # Wärend der installation gibt es kein session-Objekt!
            pass
        except KeyError:
            # Wenn der User noch nicht eingeloggt ist, gibt es auch
            # keine user_id
            data_dict["lastupdateby"] = 0

        #~ self.page_msg(data_dict["lastupdatetime"], data_dict["lastupdateby"])
        return data_dict

