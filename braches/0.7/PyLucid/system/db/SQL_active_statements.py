#!/usr/bin/python
# -*- coding: UTF-8 -*-

# copyleft: jensdiemer.de (GPL v2 or above)

"""
Anbindung an die SQL-Datenbank
"""

__version__="0.1"

__history__="""
v0.1
    - erste Release
"""

from PyLucid.system.db.SQL_passive_statements import passive_statements

debug = False

class active_statements(passive_statements):
    """
    Erweitert den allgemeinen SQL-Wrapper (mySQL.py) um
    spezielle PyLucid-Funktionen.
    """
    def __init__(self, *args):
        super(active_statements, self).__init__(*args)

    #_____________________________________________________________________________
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

    #_____________________________________________________________________________
    ## Funktionen für das ändern des Looks (Styles, Templates usw.)

    def update_style( self, style_id, style_data ):
        self.update(
            table   = "styles",
            data    = style_data,
            where   = ("id",style_id),
            limit   = 1
        )

    def new_style( self, style_data ):
        self.insert(
            table   = "styles",
            data    = {
                "name"          : style_data["name"],
                "plugin_id"     : style_data.get("plugin_id", None),
                "description"   : style_data.get("description", None),
                "content"       : style_data["content"],
            },
        )

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
            table   = "styles",
            where   = ("plugin_id",plugin_id),
            limit   = 99,
        )
        style_names = [i["name"] for i in style_names]
        return style_names

    def update_template( self, template_id, template_data ):
        self.update(
            table   = "templates",
            data    = template_data,
            where   = ("id",template_id),
            limit   = 1
        )

    def new_template( self, template_data ):
        self.insert(
            table   = "templates",
            data    = template_data,
        )

    def delete_template( self, template_id ):
        self.delete(
            table   = "templates",
            where   = ("id",template_id),
            limit   = 1
        )

    def change_page_position( self, page_id, position ):
        self.update(
            table   = "pages",
            data    = {"position":position},
            where   = ("id",page_id),
            limit   = 1
        )

    #_____________________________________________________________________________
    ## InterneSeiten

    def print_internal_page(self, internal_page_name, page_dict={}):
        """
        Interne Seite aufgeüllt mit Daten ausgeben. Diese Methode sollte immer
        verwendet werden, weil sie eine gescheite Fehlermeldung anzeigt.

        Wird für template-engine = "None" und = "string formatting" verwendet.
        """

        try:
            internal_page_data = self.get_internal_page_data(internal_page_name)
        except Exception, e:
            import inspect
            print "[Can't print internal page '%s' (from '...%s' line %s): %s]" % (
                internal_page_name, inspect.stack()[1][1][-20:], inspect.stack()[1][2], e
            )
            if not self.config.system.ModuleManager_error_handling: raise
            return

        # Wenn kein oder ein leeres Dict angegeben wurde, kann es keine "string formatting" Seite sein.
        if page_dict=={}:
            template_engine = "None"
        else:
            template_engine = "string formatting"

        if internal_page_data["template_engine"] != template_engine:
            self.page_msg(
                "Warning: Internal page '%s' is not marked as a '%s' page! "
                "(Marked as:'%s')" % (
                    internal_page_name, template_engine, internal_page_data["template_engine"]
                )
            )

        content = internal_page_data["content"]
        try:
            print content % page_dict
        except UnicodeError, e:
            self.page_msg("UnicodeError: Can't render internal page: %s" % e)
            self.page_msg("(Try to go around.)")
            try:
                for k,v in page_dict.iteritems():
                    try:
                        page_dict[k] = v.encode("utf_8", 'replace')
                    except AttributeError: # z.B. bei Zahlen
                        pass

                print content.encode("utf_8", 'replace') % page_dict
            except:
                print "<h4>Can't go around the UnicodeError!</h4>"
                if not self.config.system.ModuleManager_error_handling: raise
        except Exception, e:
            self.page_msg("Error information:")

            s = self.tools.Find_StringOperators(content)
            if s.incorrect_hit_pos != []:
                self.page_msg(" -"*40)
                self.page_msg("There are incorrect %-chars in the internal_page:")
                self.page_msg("Text summary:")
                for line in s.get_incorrect_text_summeries():
                    self.page_msg(line)
                self.page_msg(" -"*40)

            l = s.correct_tags
            # doppelte Einträge löschen (auch mit Python >2.3)
            content_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            content_placeholder.sort()
            self.page_msg("*** %s content placeholder:" % len(content_placeholder))
            self.page_msg(content_placeholder)

            l = page_dict.keys()
            given_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            given_placeholder.sort()
            self.page_msg("*** %s given placeholder:" % len(given_placeholder))
            self.page_msg(given_placeholder)

            diff_placeholders = []
            for i in content_placeholder:
                if (not i in given_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)
            for i in given_placeholder:
                if (not i in content_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)

            diff_placeholders.sort()
            self.page_msg("*** placeholder diffs:", diff_placeholders)

            raise Exception(
                "%s: '%s': Can't fill internal page '%s'. \
                *** More information above in page message ***" % (
                    sys.exc_info()[0], e, internal_page_name,
                )
            )

    def print_internal_TAL_page(self, internal_page_name, context_dict):

        internal_page_data = self.get_internal_page_data(internal_page_name)
        internal_page_content = internal_page_data["content"]
        if internal_page_data["template_engine"] != "TAL":
            self.page_msg(
                "Warning: Internal page '%s' is not marked as a TAL page! "
                "(Marked as:'%s')" % (
                    internal_page_name, internal_page_data["template_engine"]
                )
            )

        if internal_page_data["markup"] != None:
            self.page_msg(
                "Warning: A TAL page should never have markup! "
                "(internal page name: '%s', Markup:'%s')" % (
                    internal_page_name, internal_page_data["markup"]
                )
            )

        from PyLucid_simpleTAL import simpleTAL, simpleTALES

        context = simpleTALES.Context(allowPythonPath=1)
        context.globals.update(context_dict) # context.addGlobal()

        template = simpleTAL.compileHTMLTemplate(internal_page_content, inputEncoding="UTF-8")
        template.expand(context, sys.stdout, outputEncoding="UTF-8")

    def update_internal_page( self, internal_page_name, page_data ):
        self.update(
            table   = "pages_internal",
            data    = page_data,
            where   = ("name",internal_page_name),
            limit   = 1
        )

    def delete_blank_pages_internal_categories(self):
        """
        Löscht automatisch überflüssige Kategorieren.
        d.h. wenn es keine interne Seite mehr gibt, die in
        der Kategorie vorkommt, wird sie gelöscht
        """
        used_categories = self.select(
            select_items    = ["category_id"],
            from_table      = "pages_internal",
        )
        used_categories = [i["category_id"] for i in used_categories]

        existing_categories = self.select(
            select_items    = ["id","name"],
            from_table      = "pages_internal_category",
        )

        deleted_categories = []
        for line in existing_categories:
            if not line["id"] in used_categories:
                self.delete(
                    table = "pages_internal_category",
                    where = ("id", line["id"]),
                    limit = 99,
                )
                deleted_categories.append(line["name"])
        return deleted_categories

    def new_internal_page(self, data, lastupdatetime=None):
        """
        Erstellt eine neue interne Seite.
        """

        markup_id = self.get_markup_id(data["markup"])
        category_id = self.get_internal_page_category_id(data["category"])
        template_engine_id = self.get_template_engine_id(data["template_engine"])
        #~ print "category_id:", category_id

        self.insert(
            table = "pages_internal",
            data  = {
                "name"              : data["name"],
                "plugin_id"         : data["plugin_id"],
                "category_id"       : category_id,
                "template_engine"   : template_engine_id,
                "markup"            : markup_id,
                "lastupdatetime"    : self.tools.convert_time_to_sql(lastupdatetime),
                "content"           : data["content"],
                "description"       : data["description"],
            },
        )

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
            table = "pages_internal",
            where = ("plugin_id", plugin_id),
            limit = 99,
        )
        page_names = [i["name"] for i in page_names]
        return page_names

    #_____________________________________________________________________________
    ## Userverwaltung

    def add_md5_User( self, name, realname, email, pass1, pass2, admin ):
        "Hinzufügen der Userdaten in die PyLucid's JD-md5-user-Tabelle"
        self.insert(
                table = "md5users",
                data  = {
                    "name"      : name,
                    "realname"  : realname,
                    "email"     : email,
                    "pass1"     : pass1,
                    "pass2"     : pass2,
                    "admin"     : admin
                }
            )

    def update_userdata(self, id, user_data):
        """ Editierte Userdaten wieder speichern """
        self.update(
            table   = "md5users",
            data    = user_data,
            where   = ("id",id),
            limit   = 1
        )

    def del_user(self, id):
        """ Löschen eines Users """
        self.delete(
            table   = "md5users",
            where   = ("id", id),
            limit   = 1
        )

    #_____________________________________________________________________________
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
        if module_data.has_key("essential_buildin") and module_data["essential_buildin"] == True:
            active = -1
        else:
            active = 0

        self.insert(
            table = "plugins",
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
            }
        )
        return self.cursor.lastrowid

    def register_plugin_method(self, plugin_id, method_name, method_cfg, parent_method_id=None):

        where= [("plugin_id", plugin_id), ("method_name", method_name)]

        if parent_method_id != None:
            where.append(("parent_method_id", parent_method_id))

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
            elif type(v) in (dict, list, tuple):
                method_cfg[k] = pickle.dumps(v)

        # Daten vervollständigen
        method_cfg.update({
            "plugin_id"     : plugin_id,
            "method_name"   : method_name,
        })

        if parent_method_id != None:
            method_cfg["parent_method_id"] = parent_method_id

        self.insert(
            table = "plugindata",
            data  = method_cfg
        )

    def delete_plugin(self, id):
        self.delete(
            table = "plugins",
            where = ("id", id),
            limit = 999,
        )

    def delete_plugindata(self, plugin_id):
        self.delete(
            table = "plugindata",
            where = ("plugin_id", plugin_id),
            limit = 999,
        )

