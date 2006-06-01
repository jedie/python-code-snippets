#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Editor für alles was mit aussehen zu tun hat:
    - edit_style
    - edit_template
    - edit_internal_page
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.3"

__history__="""
v0.3
    - Anpassung an PyLucid v0.7
v0.2
    - Bug 1308063: Umstellung von <button> auf <input>, weil's der IE nicht
        kann s. http://www.python-forum.de/viewtopic.php?t=4180
    - NEU: Styles und Template könnne nur dann gelöscht werden, wenn keine
        Seite diese noch benutzten
v0.1.1
    - edit_internal_page_form: markups sind nun IDs aus der Tabelle markups
v0.1.0
    - Komplettumbau für neuen Module-Manager
v0.0.4
    - Bug: Internal-Page Edit geht nun wieder
v0.0.3
    - Bug: Edit Template:
        http://sourceforge.net/tracker/index.php?func=detail&aid=1273348&group_id=146328&atid=764837
v0.0.2
    - NEU: Clonen von Stylesheets und Templates nun möglich
    - NEU: Löschen von Stylesheets und Templates geht nun
    - Änderung der "select"-Tabellen, nun Anpassung per CSS möglich
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import sys, cgi



from PyLucid.system.BaseModule import PyLucidBaseModule


class edit_look(PyLucidBaseModule):
    #_______________________________________________________________________
    ## Stylesheet

    def stylesheet(self):
        """ Es wird die internal_page 'select_style' zusammen gebaut """
        from colubrid.debug import debug_info
        self.page_msg(debug_info(self.request))
        if self.request.form.has_key("clone"):
            self.clone_style()
        elif self.request.form.has_key("del"):
            self.del_style()
        elif self.request.form.has_key("edit"):
            self.edit_style()
            return

        self.select_table(
            type        = "style",
            table_data  = self.db.get_style_list()
        )

    def edit_style(self):
        """ Seite zum editieren eines Stylesheet """
        id = self.request.form["id"]
        id = int(id)

        try:
            edit_data = self.db.get_style_data(id)
        except IndexError:
            print "bad style id!"
            return

        self.make_edit_page(
            edit_data   = edit_data,
            name        = "edit_style",
            order       = "select_style",
            id          = id,
        )

    def clone_style(self):
        """ Ein Stylesheet soll kopiert werden """
        clone_name = self.request.form["clone_name"]
        new_name = self.request.form.get("new_name", "NoName")
        new_name = self.db.get_UniqueStylename(new_name)

        style_content = self.db.get_style_data_by_name( clone_name )["content"]

        style_data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : style_content,
        }
        try:
            self.db.new_style( style_data )
        except Exception, e:
            self.page_msg("Error clone Style '%s' to '%s': %s" % (clone_name, new_name, e) )
        else:
            self.page_msg( "style '%s' duplicated to '%s'" % (clone_name, new_name) )


    def save_style(self, id, name, description="", content=""):
        """ Speichert einen editierten Stylesheet """
        try:
            self.db.update_style( id, {"name": name, "content": content, "description": description} )
        except Exception, e:
            self.page_msg("Error saving style with id '%s' (use browser back button!): %s" % (id, e))
        else:
            self.page_msg( "Style saved!" )


    def del_style( self ):
        """ Lösche ein Stylesheet """
        id = self.request.form["id"]
        id = int(id)

        page_names = self.db.select(
            select_items    = ["name"],
            from_table      = "pages",
            where           = ("style", id)
        )
        if page_names:
            names = [cgi.escape(i["name"]) for i in page_names]
            self.page_msg("Can't delete stylesheet, the following pages used it: %s" % names)
        else:
            try:
                self.db.delete_style( id )
            except Exception, e:
                self.page_msg("Error deleting style with id '%s': %s" % (id, e))
            else:
                self.page_msg( "Delete Style (id:'%s')" % id )


    #_______________________________________________________________________
    ## Template

    def template(self):
        """ Es wird die internal_page 'select_template' zusammen gebaut """
        self.select_table(
            type        = "template",
            table_data  = self.db.get_template_list()
        )

    def edit_template(self, id):
        """ Seite zum editieren eines template """
        try:
            edit_data = self.db.get_template_data(id)
        except IndexError:
            print "bad template id!"
            return

        self.make_edit_page(
            edit_data   = edit_data,
            name        = "edit_template",
            order       = "edit_template",
            id          = id,
        )

    def clone_template(self, clone_name, new_name="NoName"):
        """ Ein Template soll kopiert werden """
        template_content = self.db.get_template_data_by_name( clone_name )["content"]

        template_data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : template_content,
        }
        try:
            self.db.new_template( template_data )
        except Exception, e:
            self.page_msg("Error cloning %s to %s: %s" % (clone_name, new_name, e))
        else:
            self.page_msg("template '%s' duplicated to '%s'" % (clone_name, new_name))

        self.template() # Auswahlseite wieder anzeigen

    def save_template(self, id, name, description="", content=""):
        """ Speichert einen editierten template """
        try:
            self.db.update_template( id, {"name": name, "description": description, "content": content} )
        except Exception, e:
            self.page_msg("Can't update template: %s" % e)
        else:
            self.page_msg("template with ID %s saved!" % id)

        self.template() # Auswahlseite wieder anzeigen

    def del_template(self, id):
        """ Lösche ein Template """
        page_names = self.db.select(
            select_items    = ["name"],
            from_table      = "pages",
            where           = ("template", id)
        )
        if page_names:
            names = [cgi.escape(i["name"]) for i in page_names]
            self.page_msg("Can't delete template, the following pages used it: %s" % names)
        else:
            try:
                self.db.delete_template(id)
            except Exception, e:
                self.page_msg("Error deleting template with id '%s': %s" % (id, e))
            else:
                self.page_msg("Delete Template (id:'%s')" % id)

        self.template() # Auswahlseite wieder anzeigen

    #_______________________________________________________________________
    ## Methoden für Stylesheet- und Template-Editing

    def make_edit_page(self, edit_data, name, order, id):
        """ Erstellt die Seite zum Stylesheet/Template editieren """
        internal_page_name = "edit_look_%s" % name
        context = {
            "name"          : edit_data["name"],
            "url"           : self.URLs["current_action"],
            "content"       : cgi.escape( edit_data["content"] ),
            "description"   : cgi.escape( edit_data["description"] ),
            "back"          : "%s%s" % (self.URLs["action"], order),
            "id"            : id,
        }
        self.templates.write(internal_page_name, context)

    def select_table(self, type, table_data):
        """ Erstellt die Tabelle zum auswählen eines Style/Templates """

        nameList = [i["name"] for i in table_data]

        #~ option_maker = self.tools.html_option_maker()
        #~ clone_select = option_maker.build_from_list(itemsDict)

        context = {
            "url": self.URLs.currentAction(),
            "nameList": nameList,
            "itemsDict": table_data,
        }
        internalPageName = "select_%s" % type

        #~ self.page_msg(context)

        # Seite anzeigen
        self.templates.write(internalPageName, context)

    #_______________________________________________________________________
    ## Interne Seiten editieren

    def internal_page(self):
        """
        Tabelle zum auswählen einer Internen-Seite zum editieren

        jinja context:

        context = [
            {
                "package":"buildin_plugins",
                "data": [
                    {
                        "module_name":"plugin1",
                        "data": [
                            {"name": "internal page1",
                            ...},
                            {"name": "internal page2",
                            ...},
                        ],
                    {
                        "module_name":"plugin2",
                        "data": [...]
                    },
                ]
            },
            {
                "package":"modules",
                "data": [...]
            }
        ]
        """
        if "save" in self.request.form:
            # Zuvor editierte interne Seite speichern
            self.save_internal_page()

        select_items = [
            "name","plugin_id","description","lastupdatetime","lastupdateby"
        ]
        internal_pages = self.db.internalPageList(select_items)

        select_items = ["id", "package_name", "module_name"]
        plugin_data = self.db.pluginsList(select_items)

        users = self.db.userList(select_items=["id", "name"])

        # Den ID Benzug auflösen und Daten zusammenfügen
        for page_name, data in internal_pages.iteritems():
            # Username ersetzten. Wenn die Daten noch nie editiert wurden,
            # dann ist die ID=0 und der user existiert nicht in der DB!
            lastupdateby = data["lastupdateby"]
            user = users.get(lastupdateby, {"name":"<em>[nobody]</em>"})
            data["lastupdateby"] = user["name"]

            # Plugindaten
            plugin_id = data["plugin_id"]
            plugin = plugin_data[plugin_id]

            data.update(plugin)

        # Baut ein Dict zusammen um an alle Daten über die Keys zu kommen
        contextDict = {}
        for page_name, data in internal_pages.iteritems():
            package_name = data["package_name"]
            package_name = package_name.split(".")
            package_name = package_name[1]
            data["package_name"] = package_name
            module_name = data["module_name"]

            if not package_name in contextDict:
                contextDict[package_name] = {}

            if not module_name in contextDict[package_name]:
                contextDict[package_name][module_name] = []

            contextDict[package_name][module_name].append(data)

        # Baut eine Liste für jinja zusammen
        context_list = []
        package_list = contextDict.keys()
        package_list.sort()
        for package_name in package_list:
            package_data = contextDict[package_name]

            plugins_keys = package_data.keys()
            plugins_keys.sort()

            plugin_list = []
            for plugin_name in plugins_keys:
                plugin_data = package_data[plugin_name]

                internal_page_list = []
                for internal_page in plugin_data:
                    module_name = internal_page["module_name"]
                    del(internal_page["module_name"])
                    del(internal_page["package_name"])
                    del(internal_page["plugin_id"])
                    del(internal_page["id"])
                    internal_page_list.append(internal_page)

                internal_page = {
                    "module_name": module_name,
                    "data": internal_page_list
                }
                plugin_list.append(internal_page)

            context_list.append({
                "package_name": package_name,
                "data": plugin_list
            })

        context = {
            "version": __version__,
            "itemsList": context_list,
            #~ "url": self.URLs.currentAction(),
            "url": self.URLs.actionLink("edit_internal_page"),
        }

        # Seite anzeigen
        self.templates.write("select_internal_page", context)

    def edit_internal_page(self, function_info):
        """ Formular zum editieren einer internen Seite """
        #~ from colubrid.debug import debug_info
        #~ self.page_msg(debug_info(self.request))

        #~ internal_page_name = self.request.form['internal_page_name']
        internal_page_name = function_info[0]

        try:
            # Daten der internen Seite, die editiert werden soll
            edit_data = self.db.get_internal_page_data( internal_page_name )
        except IndexError:
            self.page_msg( "bad internal-page name: '%s' !" % cgi.escape(internal_page_name) )
            self.internal_page() # Auswahl wieder anzeigen lassen
            return

        css = self.db.get_internal_page_addition_CSS(internal_page_name)
        if css == None: css = ""
        js = self.db.get_internal_page_addition_JS(internal_page_name)
        if js == None: js = ""

        OptionMaker = self.tools.html_option_maker()
        markup_option = OptionMaker.build_from_list(
            self.db.get_available_markups(), edit_data["markup"], select_value=False
        )
        template_engine_option = OptionMaker.build_from_list(
            self.db.get_available_template_engines(), edit_data["template_engine"], select_value=False
        )

        context = {
            "name"          : internal_page_name,
            "back_url"      : self.URLs.actionLink("internal_page"),
            "url"           : self.URLs.actionLink("internal_page"),
            "content_html"  : cgi.escape(edit_data["content"]),
            "content_css"   : cgi.escape(css),
            "content_js"    : cgi.escape(js),
            #FIXME description von CSS und JS werden ignoriert. Oder sollten
            # die auch keine Beschreibung haben???
            "description"            : cgi.escape(edit_data["description"]),
            "template_engine_option" : template_engine_option,
            "markup_option"          : markup_option,
        }

        self.templates.write("edit_internal_page", context)

    def save_internal_page(self):
        """ Speichert einen editierte interne Seite """
        from colubrid.debug import debug_info
        self.page_msg(debug_info(self.request))

        internal_page_name = self.request.form['internal_page_name']

        page_data = self.get_filteredFormDict(
            strings = (
                "content_html", "content_css", "content_js", "description"
            ),
            numbers = ("markup", "template_engine"),
            default = ""
        )

        # HTML abspeichern
        html_dict = {
            "content"           : page_data["content_html"],
            "description"       : page_data["description"],
            "markup"            : page_data["markup"],
            "template_engine"   : page_data["template_engine"],
        }
        self._save_internal_page_data(
            internal_page_name, "html", html_dict
        )

        # CSS abspeichern
        css_dict = { "content": page_data["content_css"]}
        self._save_internal_page_data(
            internal_page_name, "css", css_dict
        )

        # JS abspeichern
        js_dict = { "content": page_data["content_js"]}
        self._save_internal_page_data(
            internal_page_name, "js", js_dict
        )

    def _save_internal_page_data(self, internal_page_name, typ, data):
        escaped_name = cgi.escape(internal_page_name)
        if typ in ("css","js") and data["content"] == "":
            # Keine css/js Daten -> Kann in db gelöscht werden!
            #~ try:
            status = self.db.delete_internal_page_addition(
                internal_page_name, typ
            )
            #~ except Exception, e:
                #~ self.page_msg(
                    #~ "Delete error '%s'-%s-code from db: %s" % (
                        #~ typ, escaped_name, e
                    #~ )
                #~ )
            #~ else:
                #~ if status != True:
                    #~ # Es gab keinen Tabelleneintrag ;)
                    #~ return
                #~ self.page_msg(
                    #~ "Clean %s-code for internal page '%s' in db" % (
                        #~ typ, escaped_name
                    #~ )
                #~ )
        else:
            # HTML-Daten speichern
            try:
                self.db.update_internal_page(
                    internal_page_name, typ, data
                )
            except Exception, e:
                self.page_msg(
                    "Error saving %s-code from internal page '%s': %s" % (
                        typ, escaped_name, e
                    )
                )
            else:
                self.page_msg(
                    "%s-code for internal page '%s' saved!" % (
                        typ, escaped_name
                    )
                )

    #_______________________________________________________________________
    ## Allgemeine Funktionen

    def error( *msg ):
        page  = "<h2>Error.</h2>"
        page += "<p>%s</p>" % "<br/>".join( [str(i) for i in msg] )
        return page

    def get_filteredFormDict(self, strings=None, numbers=None, default=False):
        result = {}
        for name in strings:
            if default!=False:
                result[name] = self.request.form.get(name, default)
            else:
                result[name] = self.request.form[name]
        for name in numbers:
            result[name] = int(self.request.form[name])

        return result

