#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
Hier sind alle vorgefertigen Module zu finden, die eigentlich nur
ein normaler SELECT Befehl ist. Also nur Methoden die nur Daten aus
der DB bereitstellen.
"""

__version__="0.1"

__history__="""
v0.1
    - erste Release nach aufteilung
    - Allgemeine History nach __init__ verschoben
"""

import urllib, pickle, sys, time

from PyLucid.system.DBwrapper.DBwrapper import SQL_wrapper
from PyLucid.system.exceptions import *

debug = False

class passive_statements(SQL_wrapper):
    """
    Erweitert den allgemeinen SQL-Wrapper (mySQL.py) um
    spezielle PyLucid-Funktionen.
    """
    #~ def __init__(self, *args, **kwargs):
        #~ super(passive_statements, self).__init__(*args, **kwargs)


    def _error(self, type, txt):
        sys.stderr.write("<h1>SQL error</h1>")
        sys.stderr.write("<h1>%s</h1>" % type)
        sys.stderr.write("<p>%s</p>" % txt)
        import sys
        sys.exit()

    def _type_error(self, itemname, item):
        import cgi
        self._error(
            "%s is not String!" % itemname,
            "It's %s<br/>Check SQL-Table settings!" % cgi.escape( str( type(item) ) )
        )

    #_____________________________________________________________________________
    # Spezielle lucidCMS Funktionen, die von Modulen gebraucht werden

    def get_first_page_id(self):
        """
        Liefert die erste existierende page_id zurück
        """
        return self.select(
            select_items    = ["id"],
            from_table      = "pages",
            order           = ("parent","ASC"),
            limit           = 1
        )[0]["id"]

    def get_side_data(self, page_id):
        "Holt die nötigen Informationen über die aktuelle Seite"

        side_data = self.select(
                select_items    = [
                        "name", "title", "content", "markup", "lastupdatetime","keywords","description"
                    ],
                from_table      = "pages",
                where           = ( "id", page_id )
            )[0]

        side_data["template"] = self.side_template_by_id(page_id)

        # None in "" konvertieren
        for key in ("content", "name", "keywords", "description"):
            if side_data[key] == None:
                side_data[key] = ""

        if side_data["title"] == None:
            side_data["title"] = side_data["name"]

        return side_data

    def side_template_by_id(self, page_id):
        "Liefert den Inhalt des Template-ID und Templates für die Seite mit der >page_id< zurück"
        template_id = self.select(
                select_items    = ["template"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["template"]

        try:
            page_template = self.select(
                    select_items    = ["content"],
                    from_table      = "templates",
                    where           = ("id",template_id)
                )[0]["content"]
        except Exception, e:
            # Fehlerausgabe
            self.page_msg(
                "Can't get Template: %s - Page-ID: %s, Template-ID: %s" % (
                    e, page_id, template_id
                )
            )
            self.page_msg("Please edit the page and change the template!")
            # Bevor garnichts geht, holen wir uns das erst beste Template
            try:
                page_template = self.select(
                        select_items    = ["content"],
                        from_table      = "templates",
                        limit           = (0,1)
                    )[0]["content"]
                return page_template
            except Exception, e:
                # Ist wohl überhaupt nicht's da, dann kommen wir jetzt zum
                # Hardcore Fehlermeldung :(
                self._error(
                    "Can't get Template: %s" % e,
                    "Page-ID: %s, Template-ID: %s" % (page_id, template_id)
                )

        if type(page_template) != str:
            self._type_error( "Template-Content", page_template )

        return page_template

    #~ def get_preferences(self):
        #~ "Die Preferences aus der DB holen. Wird verwendet in config.readpreferences()"
        #~ value = self.select(
                #~ select_items    = ["section", "varName", "value"],
                #~ from_table      = "preferences",
            #~ )



    def side_id_by_name(self, page_name):
        "Liefert die Side-ID anhand des >page_name< zurück"
        result = self.select(
                select_items    = ["id"],
                from_table      = "pages",
                where           = ("name",page_name)
            )
        if not result:
            return False

        if result[0].has_key("id"):
            return result[0]["id"]
        else:
            return False

    def side_name_by_id(self, page_id):
        "Liefert den Page-Name anhand der >page_id< zurück"
        return self.select(
                select_items    = ["name"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["name"]

    def parentID_by_name(self, page_name):
        """
        liefert die parend ID anhand des Namens zurück
        """
        # Anhand des Seitennamens wird die aktuelle SeitenID und den ParentID ermittelt
        return self.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("name",page_name)
            )[0]["parent"]

    def parentID_by_id(self, page_id):
        """
        Die parent ID zur >page_id<
        """
        return self.select(
                select_items    = ["parent"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["parent"]

    def side_title_by_id(self, page_id):
        "Liefert den Page-Title anhand der >page_id< zurück"
        return self.select(
                select_items    = ["title"],
                from_table      = "pages",
                where           = ("id",page_id)
            )[0]["title"]

    def side_style_by_id(self, page_id):
        "Liefert die CSS-ID und CSS für die Seite mit der >page_id< zurück"
        def get_id(page_id):
            return self.select(
                    select_items    = ["style"],
                    from_table      = "pages",
                    where           = ("id",page_id)
            )[0]["style"]
        try:
            CSS_id = get_id(page_id)
        except (IndexError, KeyError):
            # Beim löschen einer Seite kann es zu einem KeyError kommen
            print "/* Index Error with page_id = %s */" % page_id
            try:
                # versuchen wir es mit dem parent
                CSS_id = get_id(self.parentID_by_id(page_id))
                print "/* Use the styles from parent page! */"
            except (IndexError, KeyError):
                # Letzter Versuch
                CSS_id = get_id(self.get_first_page_id())
                print "/* Use the styles from the first page! */"

        CSS_content = self.select(
                select_items    = ["content"],
                from_table      = "styles",
                where           = ("id",CSS_id)
            )[0]["content"]

        return CSS_content

    def get_page_data_by_id(self, page_id):
        "Liefert die Daten zum Rendern der Seite zurück"
        data = self.select(
                select_items    = ["content", "markup"],
                from_table      = "pages",
                where           = ("id", page_id)
            )[0]

        data = self.db.None_convert(data, ("content",), "")

        return data

    def page_items_by_id(self, item_list, page_id):
        "Allgemein: Daten zu einer Seite"
        page_items = self.select(
                select_items    = item_list,
                from_table      = "pages",
                where           = ("id", page_id)
            )[0]
        for i in ("name", "title", "content", "keywords", "description"):
            if page_items.has_key(i) and page_items[i]==None:
                page_items[i]=""
        return page_items

    def get_all_preferences(self):
        """
        Liefert Daten aus der Preferences-Tabelle
        wird in PyLucid_system.preferences verwendet
        """
        return self.select(
                select_items    = ["section", "varName", "value"],
                from_table      = "preferences",
            )

    def get_page_link_by_id(self, page_id):
        """ Generiert den absolut-Link zur Seite """
        data = []
        while page_id != 0:
            result = self.select(
                    select_items    = ["name","parent"],
                    from_table      = "pages",
                    where           = ("id",page_id)
                )[0]
            page_id  = result["parent"]
            data.append( result["name"] )

        # Liste umdrehen
        data.reverse()

        data = [urllib.quote_plus(i) for i in data]

        return "/" + "/".join(data)

    def get_sitemap_data(self):
        """ Alle Daten die für`s Sitemap benötigt werden """
        return self.select(
                select_items    = ["id","name","title","parent"],
                from_table      = "pages",
                where           = [("showlinks",1), ("permitViewPublic",1)],
                order           = ("position","ASC"),
            )

    def get_sequencing_data(self):
        """ Alle Daten die für pageadmin.sequencing() benötigt werden """
        parend_id = self.parentID_by_id(self.CGIdata["page_id"])
        return self.select(
                select_items    = ["id","name","title","parent","position"],
                from_table      = "pages",
                where           = ("parent", parend_id),
                order           = ("position","ASC"),
            )

    #_____________________________________________________________________________
    ## Funktionen für Styles, Templates usw.

    def get_style_list(self):
        return self.select(
                select_items    = ["id","name","description"],
                from_table      = "styles",
                order           = ("name","ASC"),
            )

    def get_style_data(self, style_id):
        return self.select(
                select_items    = ["name","description","content"],
                from_table      = "styles",
                where           = ("id", style_id)
            )[0]

    def get_style_data_by_name(self, style_name):
        return self.select(
                select_items    = ["description","content"],
                from_table      = "styles",
                where           = ("name", style_name)
            )[0]

    def get_template_list(self):
        return self.select(
                select_items    = ["id","name","description"],
                from_table      = "templates",
                order           = ("name","ASC"),
            )

    def get_template_data(self, template_id):
        return self.select(
                select_items    = ["name","description","content"],
                from_table      = "templates",
                where           = ("id", template_id)
            )[0]

    def get_template_data_by_name(self, template_name):
        return self.select(
                select_items    = ["description","content"],
                from_table      = "templates",
                where           = ("name", template_name)
            )[0]

    #_____________________________________________________________________________
    ## InterneSeiten

    def get_internal_page_list(self):
        return self.select(
                select_items    = [
                    "name","plugin_id","description",
                    "markup","template_engine","markup"
                ],
                from_table      = "pages_internal",
            )

    def get_internal_page_dict(self):
        page_dict = {}
        for page in self.get_internal_page_list():
            page_dict[page["name"]] = page
        return page_dict

    def get_internal_category(self):
        return self.select(
                select_items    = ["id","module_name"],
                from_table      = "plugins",
                order           = ("module_name","ASC"),
            )

    def get_template_engine(self, id):
        """ Liefert den template_engine-Namen anhand der ID """
        if id==None:
            # Existiert auch als ID
            id = "None"

        try:
            return self.select(
                select_items    = ["name"],
                from_table      = "template_engines",
                where           = ("id", id)
            )[0]["name"]
        except IndexError:
            self.page_msg("Can't get template engine name for id '%s'. " % id)
            return "none"

    def get_template_engine_id(self, name):
        if type(name)==int:
            # Ist wohl schon die ID-Zahl
            return name

        if name==None:
            # None existiert auch als ID
            name="None"
        else:
            name = name.replace("_", " ")

        try:
            return self.select(
                select_items    = ["id"],
                from_table      = "template_engines",
                where           = ("name", name)
            )[0]["id"]
        except IndexError:
            self.page_msg("Warning: Can't get ID for template engine namend '%s'" % name)
            return None

    def get_internal_page_data(self, internal_page_name, replace=True):
        try:
            data = self.select(
                select_items    = ["template_engine","markup","content","description"],
                from_table      = "pages_internal",
                where           = ("name", internal_page_name)
            )[0]
        except Exception, e:
            import inspect
            raise KeyError(
                "Internal page '%s' not found (from '...%s' line %s): %s" % (
                    internal_page_name, inspect.stack()[1][1][-20:], inspect.stack()[1][2], e
                )
            )

        if replace==True:
            data["template_engine"] = self.get_template_engine(data["template_engine"])
            data["markup"] = self.get_markup_id(data["markup"])

        return data

    def get_internal_page(self, internal_page_name, page_dict={}):
        """
        Interne Seite aufgeüllt mit Daten ausgeben. Diese Methode sollte immer
        verwendet werden, weil sie eine gescheite Fehlermeldung anzeigt.
        """
        internal_page = self.get_internal_page_data(internal_page_name)

        try:
            internal_page["content"] = internal_page["content"] % page_dict
        except KeyError, e:
            import re
            placeholder = re.findall(r"%\((.*?)\)s", internal_page["content"])
            raise KeyError(
                "KeyError %s: Can't fill internal page '%s'. \
                placeholder in internal page: %s given placeholder for that page: %s" % (
                    e, internal_page_name, placeholder, page_dict.keys()
                )
            )
        return internal_page


    #~ def get_internal_group_id(self):
        #~ """
        #~ Liefert die ID der internen PyLucid Gruppe zurück
        #~ Wird verwendet für interne Seiten!
        #~ """
        #~ internal_group_name = "PyLucid_internal"
        #~ return self.select(
                #~ select_items    = ["id"],
                #~ from_table      = "groups",
                #~ where           = ("name", internal_group_name)
            #~ )[0]["id"]

    def get_internal_page_category_id(self, category_name):
        """
        Liefert die ID anhand des Kategorie-Namens zurück
        Existiert die Kategorie nicht, wird sie in die Tabelle eingefügt.
        """
        try:
            return self.select(
                select_items    = ["id"],
                from_table      = "pages_internal_category",
                where           = ("name", category_name)
            )[0]["id"]
        except IndexError:
            # Kategorier existiert noch nicht -> wird erstellt
            self.insert(
                table = "pages_internal_category",
                data  = {"name": category_name}
            )
            return self.cursor.lastrowid

    #_____________________________________________________________________________
    ## Userverwaltung

    def normal_login_userdata(self, username):
        "Userdaten die bei einem normalen Login benötigt werden"
        return self.select(
                select_items    = ["id", "password", "admin"],
                from_table      = "md5users",
                where           = ("name", username)
            )[0]

    def userdata(self, username):
        return self.select(
                select_items    = ["id", "name","realname","email","admin"],
                from_table      = "md5users",
                where           = ("name", username)
            )[0]

    def md5_login_userdata(self, username):
        "Userdaten die beim JS-md5 Login benötigt werden"
        return self.select(
                select_items    = ["id", "pass1", "pass2", "admin"],
                from_table      = "md5users",
                where           = ("name", username)
            )[0]

    def exists_admin(self):
        """
        Existiert schon ein Admin?
        """
        result = self.select(
            select_items    = ["id"],
            from_table      = "md5users",
            limit           = (1,1)
        )
        if result:
            return True
        else:
            return False

    def user_table_data(self):
        """ wird in userhandling verwendet """
        return self.select(
            select_items    = ["id","name","realname","email","admin"],
            from_table      = "md5users",
        )

    def user_info_by_id(self, id):
        return self.select(
            select_items    = ["id","name","realname","email","admin"],
            from_table      = "md5users",
            where           = ("id", id)
        )[0]

    #_____________________________________________________________________________
    ## Module / Plugins

    def get_active_module_data(self):
        """
        Module-Daten für den Modulemanager holen
        """
        select_items = ["id", "package_name", "module_name", "debug"]
        # Build-In Module holen
        data = self.select( select_items,
            from_table      = "plugins",
            where           = [("active", -1)],
        )
        # Sonstigen aktiven Module
        data += self.select( select_items,
            from_table      = "plugins",
            where           = [("active", 1)],
        )

        # Umformen zu einem dict mit dem Namen als Key
        result = {}
        for line in data:
            result[line['module_name']] = line

        return result

    def get_method_properties(self, plugin_id, method_name):

        def unpickle(SQL_result_list):
            for line in SQL_result_list:
                for item in ("CGI_laws", "get_CGI_data"):
                    if line[item] == None:
                        continue
                    #~ try:
                    line[item] = pickle.loads(line[item])
                    #~ except:
            return SQL_result_list


        data_items = [
            "must_login", "must_admin", "CGI_laws", "get_CGI_data", "menu_section",
            "menu_description","direct_out", "sys_exit", "has_Tags", "no_rights_error"
        ]
        # Daten der Methode holen
        method_properties = self.select(
            select_items    = ["id", "parent_method_id"] + data_items,
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id), ("method_name",method_name)],
        )
        method_properties = unpickle(method_properties)[0]

        return method_properties

    def get_method_id(self, plugin_id, method_name):
        """ Wird beim installieren eines Plugins benötigt """
        return self.select(
            select_items    = ["id"],
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id), ("method_name", method_name)],
        )[0]["id"]

    def get_plugin_id(self, package, module):
        """ Wird beim installieren eines Plugins benötigt """
        return self.select(
            select_items    = ["id"],
            from_table      = "plugins",
            where           = [("package_name", package), ("module_name", module)],
        )[0]["id"]

    def get_plugin_info_by_id(self, plugin_id):
        result = self.select(
            select_items    = ["package_name", "module_name"],
            from_table      = "plugins",
            where           = ("id", plugin_id),
        )[0]
        return result["package_name"], result["module_name"]

    def get_installed_modules_info(self):
        return self.select(
            select_items    = [
                "module_name", "package_name", "id","version","author","url","description","active"
            ],
            from_table      = "plugins",
            #~ debug = True,
        )

    def get_module_deinstall_info(self, id):
        deinstall_info = self.select(
            select_items    = [
                "module_name", "package_name", "SQL_deinstall_commands"
            ],
            from_table      = "plugins",
            where           = ("id", id),
        )[0]
        if deinstall_info["SQL_deinstall_commands"] != None:
            deinstall_info["SQL_deinstall_commands"] = pickle.loads(
                deinstall_info["SQL_deinstall_commands"]
            )

        return deinstall_info

    def get_plugindata(self, plugin_id):
        """
        Liefert plugindata Daten zurück.
        """
        return self.select(
            select_items    = ["*"],
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id)],
            #~ order           = ("parent_method_id","ASC"),
        )

    def get_plugin_menu_data(self, plugin_id):
        return self.select(
            select_items    = ["parent_method_id", "method_name", "menu_section", "menu_description"],
            from_table      = "plugindata",
            where           = [("plugin_id", plugin_id)]#,("parent_method_id", None)],
        )

    def get_internal_pages_info_by_module(self, plugin_id):
        """
        Informationen zu allen internen-Seiten von einem Plugin.
        Dabei werden die IDs von markup und lastupdateby direkt aufgelöst
        """
        pages_info = self.select(
            select_items    = [
                "name", "template_engine", "markup",
                "lastupdatetime", "lastupdateby", "description"
            ],
            from_table      = "pages_internal",
            where           = [("plugin_id", plugin_id)]
        )
        for page_info in pages_info:
            page_info["markup"] = self.get_markup_name(page_info["markup"])
            try:
                page_info["lastupdateby"] = self.user_info_by_id(page_info["lastupdateby"])["name"]
            except IndexError:
                pass
        return pages_info

    #_____________________________________________________________________________
    ## LOG

    def get_last_logs(self, limit=10):
        return self.select(
            select_items    = ["timestamp", "sid", "user_name", "domain", "message","typ","status"],
            from_table      = "log",
            order           = ("timestamp","DESC"),
            limit           = (0,limit)
        )

    #_____________________________________________________________________________
    ## Rechteverwaltung

    def get_permitViewPublic(self, page_id):
        return self.select(
                select_items    = [ "permitViewPublic" ],
                from_table      = "pages",
                where           = ("id", page_id),
            )[0]["permitViewPublic"]

    #_____________________________________________________________________________
    ## Markup

    def get_markup_name(self, id_or_name):
        """
        Liefert von der ID den Markup Namen. Ist die ID schon der Name, ist
        das auch nicht schlimm.
        """
        try:
            markup_id = int(id_or_name)
        except:
            # Die Angabe ist offensichtlich schon der Name des Markups
            return id_or_name
        else:
            # Die Markup-ID Auflösen zum richtigen Namen
            return self.get_markupname_by_id( markup_id )

    def get_markup_id(self, id_or_name):
        """
        Liefert vom Namen des Markups die ID, auch dann wenn es schon die
        ID ist
        """
        if id_or_name == None:
            # Kein Markup wird einfach als None gehandelt
            return None

        try:
            return int(id_or_name) # Ist eine Zahl -> ist also schon die ID
        except:
            pass

        try:
            return self.select(
                select_items    = ["id"],
                from_table      = "markups",
                where           = ("name",id_or_name)
            )[0]["id"]
        except IndexError, e:
            raise IndexError("Can't get markup-ID for the name '%s' type: %s error: %s" % (
                    id_or_name, type(id_or_name), e
                )
            )

    def get_markupname_by_id(self, markup_id):
        """ Markup-Name anhand der ID """
        try:
            return self.select(
                select_items    = ["name"],
                from_table      = "markups",
                where           = ("id",markup_id)
            )[0]["name"]
        except IndexError:
            self.page_msg("Can't get markupname from markup id '%s' please edit this page and change markup!" % markup_id)
            return "none"

    def get_available_markups(self):
        """
        Bildet eine Liste aller verfügbaren Markups. Jeder Listeneintrag ist wieder
        eine Liste aus [ID,name]. Das ist ideal für tools.html_option_maker().build_from_list()
        """
        markups = self.select(
            select_items    = ["id","name"],
            from_table      = "markups",
        )
        result = []
        for markup in markups:
            result.append([markup["id"], markup["name"]])

        return result

    def get_available_template_engines(self):
        """
        Bildet eine Liste aller verfügbaren template_engines. Jeder Listeneintrag ist wieder
        eine Liste aus [ID,name]. Das ist ideal für tools.html_option_maker().build_from_list()
        """
        markups = self.select(
            select_items    = ["id","name"],
            from_table      = "template_engines",
        )
        result = []
        for markup in markups:
            result.append([markup["id"], markup["name"]])

        return result



