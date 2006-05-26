#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Admin

Einrichten/Konfigurieren von Modulen und Plugins

CREATE TABLE `lucid_plugindata` (
  `id` int(11) NOT NULL auto_increment,
  `plugin_id` int(11) NOT NULL default '0',
  `method_name` varchar(50) NOT NULL default '',
  `internal_page_info` varchar(255) default NULL,
  `menu_section` varchar(128) default NULL,
  `menu_description` varchar(255) default NULL,
  `must_admin` int(11) NOT NULL default '1',
  `must_login` int(11) NOT NULL default '1',
  `has_Tags` int(11) NOT NULL default '0',
  `no_rights_error` int(11) NOT NULL default '0',
  `direct_out` int(11) NOT NULL default '0',
  `sys_exit` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `combinedKey` (`plugin_id`,`method_name`)
);

CREATE TABLE `lucid_plugins` (
  `id` int(11) NOT NULL auto_increment,
  `package_name` varchar(30) NOT NULL default '',
  `module_name` varchar(30) NOT NULL default '',
  `version` varchar(15) default NULL,
  `author` varchar(50) default NULL,
  `url` varchar(128) default NULL,
  `description` varchar(255) default NULL,
  `long_description` text,
  `active` int(1) NOT NULL default '0',
  `debug` int(1) NOT NULL default '0',
  `SQL_deinstall_commands` text,
  PRIMARY KEY  (`id`)
);
"""

__version__="0.3"

__history__="""
v0.3
    - Anpassung an PyLucid v0.7
v0.2
    - NEU: debug_installed_modules_info() - Für einen besseren Überblick, welche Methoden
        in der DB registriert sind.
v0.1.1
    - NEU: reinit
v0.1
    - erste Version
"""

__todo__="""
    - CSS deinstallation
    - Fehlerausgabe bei check_module_data
"""


import sys, os, glob, imp, cgi, urllib, pickle


debug = False
#~ debug = True
error_handling = False
available_packages = (
    "PyLucid/modules","PyLucid/buildin_plugins","PyLucid/plugins"
)
internal_page_file = "PyLucid/modules/module_admin_administation_menu.html"

from PyLucid.system.exceptions import *
from PyLucid.system.BaseModule import PyLucidBaseModule


class module_admin(PyLucidBaseModule):

    def menu(self):
        self.response.write(
            "<h4>Module/Plugin Administration v%s</h4>" % __version__
        )
        self.module_manager.build_menu()

    def link(self, action):
        if self.request.runlevel != "install":
            # Nur wenn nicht im "install" Bereich
            self.response.write(
                '<p><a href="%s%s">%s</a></p>' % (
                    self.URLs["action"], action, action
                )
            )

    def administation_menu(self, print_link=True):
        """
        Module/Plugins installieren
        """
        self.installed_modules_info = self.get_installed_modules_info()
        if debug:
            self.page_msg(self.installed_modules_info)

        data = self._read_packages()
        data = self._filter_cfg(data)
        data = self._read_all_moduledata(data)

        context_dict = {
            "version"       : __version__,
            "package_data"  : data,
            "installed_data": self.installed_modules_info,
            #~ "action_url"    : self.URLs["action"],
            "action_url"    : self.URLs.currentAction(),
        }

        if self.request.runlevel == "install":
            # Wurde von install_PyLucid.py aufgerufen.
            from PyLucid.simpleTAL import simpleTAL, simpleTALES

            context = simpleTALES.Context(allowPythonPath=1)
            #~ self.page_msg(context_dict)
            context.globals.update(context_dict) # context.addGlobal()

            try:
                f = file(internal_page_file,"rU")
                install_template = f.read()
                f.close()
            except Exception, e:
                self.response.write(
                    "Can't read internal_page file '%s': %s" % (
                        internal_page_file, e
                    )
                )
                return

            template = simpleTAL.compileHTMLTemplate(install_template, inputEncoding="UTF-8")
            template.expand(context, self.response, outputEncoding="UTF-8")
        else:
            # Normal als Modul aufgerufen
            self.db.print_internal_TAL_page("module_admin_administation_menu", context_dict)
            self.link("menu")

    #~ def print_tags_information(self):


    #________________________________________________________________________________________

    def first_time_install(self, simulation=True):
        """
        Installiert alle wichtigen Module/Plugins
        Das sind alle Module, bei denen:
        "essential_buildin" == True oder "important_buildin" == True
        """
        self.response.write("<h2>First time install:</h2>\n")
        self.response.write("<pre>\n")
        self.response.write("<strong>truncate tables:</strong>\n")
        tables = (
            "plugins", "plugindata", "pages_internal",
            "pages_internal_category"
        )
        for table in tables:
            self.response.write("\t* truncate table %s..." % table)

            if simulation:
                self.response.write("\n")
                continue

            try:
                self.db.cursor.execute("TRUNCATE TABLE $$%s" % table)
            except Exception, e:
                self.response.write(sys.exc_info()[0],":", e)
                self.response.write("(Have you first init the tables?)")
                return
            else:
                self.response.write("OK\n")

        # Wir tun mal so, als wenn es keine installierten Module gibt:
        self.installed_modules_info = []
        data = self._read_packages()
        data = self._filter_cfg(data)
        data = self._read_all_moduledata(data)

        sorted_data = []
        for module in data:
            if (module["essential_buildin"] != True) and \
                                    (module["important_buildin"] != True):
                continue

            try:
                self.install(
                    module['package_name'], module['module_name'],
                    simulation
                )
            except IntegrityError, e:
                self.response.write("*** Error: '%s'" % e)
                self.response.write("make a db rollback!")
                self.db.rollback()
                break

            # essential_buildin werden automatisch aktiviert mit active = -1
            # important_buildin müßen normal aktiviert werden (active = 1)
            if module["important_buildin"] == True:
                self.response.write(
                    "Activate plugin with ID: %s\n" % self.registered_plugin_id
                )
                if simulation:
                    continue
                self.activate(self.registered_plugin_id, print_info=False)

        self.db.commit()
        self.response.write("</pre>")


    #_________________________________________________________________________

    def register_methods(self, package, module_name, module_data, simulation):
        """
        Das module_manager_data Dict aufbereitet in die DB schreiben
        """
        def register_method(plugin_id, method, method_data):
            for k,v in method_data.iteritems():
                self.response.write("***", k, "-", v)

        self.response.write("Find id for %s.%s..." % (package, module_name),)
        #~ try:
        plugin_id = self.db.get_plugin_id(package, module_name)
        #~ except Exception, e:
            #~ if not error_handling: raise Exception(e)
            #~ self.response.write(sys.exc_info()[0],":", e)
        #~ else:
        self.response.write("OK, id is: %s\n" % plugin_id)

        # module_manager_data in Tabelle "plugindata" eintragen
        self.response.write("register methods:\n")
        for method_name in module_data["module_manager_data"]:
            self.response.write("\t* %s " % method_name)
            method_cfg = module_data["module_manager_data"][method_name]

            if type(method_cfg) != dict:
                self.response.write(
                    "- Error, %s-value, in module_manager_data, is not typed dict!!!" % method_name
                )
                continue

            #~ method_cfg = method_cfg.copy()

            #~ if method_cfg.has_key('CGI_dependent_actions'):
                #~ del method_cfg['CGI_dependent_actions']

            try:
                self.db.register_plugin_method(
                    plugin_id, method_name, method_cfg, simulation
                )
            except Exception, e:
                msg = "%s: '%s'\n" % (sys.exc_info()[0], e)
                raise IntegrityError(msg)
            else:
                self.response.write("OK\n")

        #~ for parent_method in module_data["module_manager_data"]:
            #~ method_cfg = module_data["module_manager_data"][parent_method]

            #~ if type(method_cfg) != dict:
                #~ self.response.write("Error in data!!!")
                #~ continue

            #~ if not method_cfg.has_key('CGI_dependent_actions'):
                #~ continue

            #~ dependent_cfg = method_cfg['CGI_dependent_actions']

            #~ parent_cfg = method_cfg
            #~ del parent_cfg['CGI_dependent_actions']

            #~ try:
                #~ parent_method_id = self.db.get_method_id(plugin_id, parent_method)
            #~ except Exception, e:
                #~ self.response.write(
                    #~ "ERROR: Can't get parent method ID for plugin_id '%s' and method_name '%s'" % (
                        #~ plugin_id, parent_method
                    #~ )
                #~ )
                #~ continue

            #~ self.response.write(
                #~ "register CGI_dependent_actions for method '%s' with id '%s':" % (
                    #~ parent_method, parent_method_id
                #~ )
            #~ )

            #~ for method_name, cfg in dependent_cfg.iteritems():
                #~ self.response.write("\t* %s" % method_name)

                #~ try:
                #~ self.db.register_plugin_method(
                    #~ plugin_id, method_name, cfg, parent_method_id, simulation
                #~ )
                #~ except Exception, e:
                    #~ self.response.write(sys.exc_info()[0],":", e)
                #~ else:
                #~ self.response.write("OK\n")

    #________________________________________________________________________________________
    # install

    def install(self, package, module_name, simulation=False):
        """
        Modul in die DB eintragen
        """
        self.link("administation_menu")
        self.response.write(
            "<h3>Install %s.<strong>%s</strong></h3>" % (
                package, module_name
            )
        )
        self.response.write("<pre>")

        module_data = self._get_module_data(package, module_name)

        if self.check_module_data(module_data) == True:
            self.response.write("<h3>Error</h3>")
            self.response.write(
                "<h4>module config data failed. Module was not installed!!!</h4>"
            )
            self.debug_package_data([module_data])
            return

        #~ self.debug_package_data([module_data])

        ##_____________________________________________
        # In Tabelle "plugins" eintragen
        self.response.write("register plugin %s.%s..." % (package, module_name),)
        #~ self.response.write(package, module_name)
        #~ self.response.write(module_data)
        #~ try:
        if not simulation:
            self.registered_plugin_id = self.db.install_plugin(
                module_data, simulation
            )
        #~ except Exception, e:
            #~ self.response.write("%s: %s\n" % (sys.exc_info()[0], e))
            #~ # Evtl. ist das Plugin schon installiert.
            #~ try:
                #~ self.registered_plugin_id = self.db.get_plugin_id(
                    #~ module_data['package_name'], module_data['module_name']
                #~ )
            #~ except Exception, e:
                #~ raise IntegrityError("Can't get Module/Plugin ID: %s\n" % e)
        #~ else:
        self.response.write("OK\n")

        ##_____________________________________________
        # Stylesheets
        if module_data["styles"] != None:
            self.response.write("install stylesheet:\n")
            for style in module_data["styles"]:
                self.response.write("\t* %-25s" % style["name"])
                css_filename = os.path.join(
                    module_data['package_name'],
                    "%s_%s.css" % (module_data['module_name'], style["name"])
                )
                self.response.write("%s...\n" % css_filename,)
                try:
                    f = file(css_filename, "rU")
                    style["content"] = f.read()
                    f.close()
                except Exception, e:
                    raise IntegrityError("Error reading CSS-File: %s\n" % e)

                if simulation:
                    self.response.write("\n")
                    continue

                try:
                    style["plugin_id"] = self.registered_plugin_id
                    self.db.new_style(style)
                except Exception, e:
                    raise IntegrityError(
                        "Can't save new Style to DB: %s - %s" % (
                            sys.exc_info()[0], e
                        )
                    )
                else:
                    self.response.write("OK\n")

        ##_____________________________________________
        # internal_pages
        self.response.write("install internal_page:\n")
        data = module_data["module_manager_data"]
        for method_name, method_data in data.iteritems():
            self._install_internal_page(
                method_data, package, module_name, method_name,
                simulation
            )

        ##_____________________________________________
        # SQL Kommandos ausführen
        if module_data["SQL_install_commands"] != None:
            self.execute_SQL_commands(
                module_data["SQL_install_commands"], simulation
            )

        self.register_methods(package, module_name, module_data, simulation)

        self.response.write("</pre>")
        #~ self.response.write(
            #~ 'activate this Module? <a href="%s/activate/%s">yes, enable it</a>' % (
                #~ self.URLs["action"], self.registered_plugin_id
            #~ )
        #~ )
        self.link("administation_menu")

    def _install_internal_page(self, method_data, package, module_name,
                                                    method_name, simulation):
        """
        Eintragen der internal_page
        Wird von self.install() benutzt
        """
        if type(method_data) != dict or \
                            method_data.has_key("internal_page_info") != True:
            return

        data = method_data["internal_page_info"]

        # Hinweis: template_engine und markup werden von self.db umgewandelt in IDs!
        name = "%s_%s" % (module_name, data.get("name",method_name))
        internal_page = {
            "name"              : name,
            "plugin_id"         : self.registered_plugin_id,
            "category"          : module_name,
            "description"       : data["description"],
            "template_engine"   : data["template_engine"],
            "markup"            : data["markup"],
        }

        self.response.write("\t* %-25s " % internal_page["name"])

        # .replace(".","/")
        internal_page_filename = os.path.join(
            package, "%s.html" % internal_page["name"]
        )
        self.response.write("%s..." % internal_page_filename)
        try:
            lastupdatetime = os.stat(internal_page_filename).st_mtime
        except:
            lastupdatetime = None

        try:
            f = file(internal_page_filename, "rU")
            internal_page["content"] = f.read()
            f.close()
        except Exception, e:
            self.response.write("Error reading Template-File: %s\n" % e)
            return

        if simulation:
            self.response.write("\n")
            return

        try:
            self.db.new_internal_page(internal_page, lastupdatetime)
        except Exception, e:
            raise IntegrityError("Can't save new internal page to DB: %s - %s" % (
                    sys.exc_info()[0], e
                )
            )
        else:
            self.response.write("OK\n")


    def check_module_data(self, data):

        def check_dict_list(dict_list, type, must_have_keys):
            errors = False
            for item in dict_list:
                for key in must_have_keys:
                    if not item.has_key(key):
                        self.page_msg("&nbsp;-&nbsp;KeyError in %s: %s" % (type, key))
                        errors = True
            return errors

        has_errors = False
        if data["styles"] != None:
            status = check_dict_list(
                data["styles"], "styles",
                ("name", "description")
            )
            if status == True: has_errors=True

        return has_errors

    #~ def install_abort(self):
        #~ self.response.write("Aborted!\n")
        #~ self.db.rollback() # Alle vorherigen Transaktionen rückgängig machen

    #________________________________________________________________________________________
    # DEinstall

    def deinstall(self, id, print_info=True):
        """
        Modul aus der DB löschen
        """
        try:
            deinstall_info = self.db.get_module_deinstall_info(id)
        except IndexError:
            raise IntegrityError(
                "Can't get plugin with id '%s'! Is this Plugin is installed?!?!" % id
            )
            #~ self.administation_menu()
            #~ return

        if print_info:
            self.response.write("<h3>DEinstall Plugin %s.%s (ID %s)</h3>" % (
                    deinstall_info["package_name"], deinstall_info["module_name"], id
                )
            )

            self.link("administation_menu")
            self.response.write("<pre>")

        ##_____________________________________________
        # Einträge in Tabelle 'plugindata' löschen
        self.response.write("delete plugin-data...",)
        try:
            self.db.delete_plugindata(id)
        except Exception, e:
            raise IntegrityError(
                    "Can't delete plugindata! ID: %s (%s: %s)" % (
                    id, sys.exc_info()[0],":", e
                )
            )
        else:
            self.response.write("OK\n")

        ##_____________________________________________
        # Einträge in Tabelle 'plugin' löschen
        self.response.write("delete plugin registration...",)
        #~ try:
        self.db.delete_plugin(id)
        #~ except Exception, e:
            #~ raise IntegrityError(
                    #~ "Can't delete plugin! ID: %s (%s: %s)" % (
                    #~ id, sys.exc_info()[0],":", e
                #~ )
            #~ )
        #~ else:
        self.response.write("OK\n")

        ##_____________________________________________
        # Stylesheets löschen
        self.response.write("delete stylesheet...",)
        try:
            deleted_styles = self.db.delete_style_by_plugin_id(id)
        except Exception, e:
            raise IntegrityError(
                    "Can't delete plugin style! ID: %s (%s: %s)" % (
                    id, sys.exc_info()[0], e
                )
            )
        else:
            self.response.write("OK, deleted: %s\n" % deleted_styles)

        ##_____________________________________________
        # internal_pages löschen
        self.response.write("delete internal_pages...",)
        try:
            deleted_pages = self.db.delete_internal_page_by_plugin_id(id)
        except Exception, e:
            raise IntegrityError(
                    "Can't delete plugin internal page! ID: %s (%s: %s)" % (
                    id, sys.exc_info()[0], e
                )
            )
        else:
            self.response.write("OK, deleted pages: %s\n" % deleted_pages)

        self.response.write("Cleanup internal page categories...",)
        #~ try:
        deleted_categories = self.db.delete_blank_pages_internal_categories()
        #~ except Exception, e:
            #~ raise IntegrityError(
                    #~ "Cleanup internal page! (%s: %s)" % (
                    #~ sys.exc_info()[0], e
                #~ )
            #~ )
        #~ else:
        self.response.write("deleted_categories: %s" % deleted_categories)

        ##_____________________________________________
        # SQL Kommandos ausführen
        if deinstall_info["SQL_deinstall_commands"] != None:
            self.execute_SQL_commands(deinstall_info["SQL_deinstall_commands"])

        if print_info:
            self.response.write("</pre>")
            self.link("administation_menu")

    #________________________________________________________________________________________
    # REinit (Ein Modul/Plugin deinstallieren und direkt wieder Installieren)

    def reinit(self, id):
        self.link("administation_menu")

        try:
            package_name, module_name = self.db.get_plugin_info_by_id(id)
        except Exception, e:
            raise IntegrityError(
                "Can't get plugin information (ID %s): %s" % (id, e)
            )

        self.response.write("<h3>reinit Plugin %s.%s (ID %s)</h3>" % (package_name, module_name, id))

        self.response.write("<pre>")

        self.response.write(" *** deinstall ***")
        self.deinstall(id, print_info=False)

        self.response.write(" *** install ***")
        self.install(package_name, module_name)#, print_info=False)

        self.response.write("</pre>")
        self.link("administation_menu")

    #________________________________________________________________________________________
    # Activate / Deactivate

    def activate(self, id, print_info=True):
        id = int(id)
        self.db.activate_module(id)
        if print_info==True:
            self.page_msg("Enable Module/Plugin (ID: %s)" % id)
            self.administation_menu()

    def deactivate(self, id):
        id = int(id)
        self.db.deactivate_module(id)
        self.page_msg("Disable Module/Plugin (ID: %s)" % id)
        self.administation_menu()

    #________________________________________________________________________________________
    # Information über nicht installierte Module / Plugins

    def _read_one_package(self, package_name):
        """
        Dateiliste eines packages erstellen.
        """
        filelist = []
        #~ self.page_msg("%s/*.py" % package_name)
        for module_path in glob.glob("%s/*.py" % package_name):
            filename = os.path.split( module_path )[1]
            if filename[0] == "_": # Dateien wie z.B. __ini__.py auslassen
                continue
            module_name = os.path.splitext( filename )[0]
            filelist.append(module_name)
        return filelist

    def _read_packages(self):
        """
        Alle verfügbaren packages durch scannen.
        """
        data = {}
        for package in available_packages:
            filelist = self._read_one_package(package)
            for filename in filelist:
                if data.has_key(filename):
                    self.page_msg("Error: duplicate Module/Pluginname '%s'!" % filename)
                data[filename] = {"package": package}
        return data

    def is_installed(self, package, module):
        for line in self.installed_modules_info:
            if line["package_name"] == package and line["module_name"] == module:
                return True
        return False

    def _filter_cfg(self, package_data):
        """
        Nur Module/Plugins herrausfiltern zu denen es auch Konfiguration-Daten gibt.
        """
        not_installed_data = {}
        installed_data = []
        filelist = package_data.keys()
        for module_name, module_data in package_data.iteritems():
            if not module_name.endswith("_cfg"):
                continue

            clean_module_name = module_name[:-4]
            if not clean_module_name in filelist:
                # Zur Config-Datei gibt's kein Module?!? -> Wird ausgelassen
                continue

            if self.is_installed(module_data["package"], clean_module_name):
                # Schon installierte Module auslassen
                continue

            # Das Modul ist noch nicht installiert!
            not_installed_data[clean_module_name] = module_data
            not_installed_data[clean_module_name]["cfg_file"] = module_name

        return not_installed_data

    def _get_module_data(self, package, module_name):
        """
        Liefert alle Daten zu einem Modul, aus der zugehörigen config-Datei.
        """
        def _import(package_name, module_name):
            #~ package_name = package_name.replace("_",".") #FIXME
            package_name = package_name.replace("/",".") #FIXME
            full_modulename = "%s.%s" % (package_name, module_name)
            #~ self.page_msg("full_modulename:", full_modulename)
            return __import__(
                full_modulename,
                globals(), locals(),
                [module_name]
            )

        try:
            module_cfg_object = _import(package, module_name+"_cfg")
        except SyntaxError, e:
            raise SyntaxError("Can't import %s.%s: %s" % (package, module_name, e))

        result = {
            "package_name"  : package,
            "module_name"   : module_name,
        }

        try:
            result["module_manager_data"] = getattr(
                module_cfg_object, "module_manager_data"
            )
        except AttributeError, e:
            self.page_msg(
                "Can't get module_manager_data from %s: %s" % (
                    module_name+"_cfg",e
                )
            )
            # Die ModuleManager-Daten _müßen_ vorhanden sein, deswegen wird jetzt das
            # ganze Module ausgelassen
            return

        def get_striped_attr(object, attr):
            result = getattr(object, attr, None)
            if type(result) == str:
                return result.strip()
            return result

        result["module_manager_debug"] = getattr(
            module_cfg_object, "module_manager_debug", False
        )

        # Normale Attribute holen
        items = (
            "SQL_install_commands", "SQL_deinstall_commands",
            "styles", "internal_pages"
        )
        for attr in items:
            result[attr] = get_striped_attr(module_cfg_object, attr)

        # meta Attribute holen
        items = (
            "author", "url", "description", "long_description",
            "essential_buildin", "important_buildin"
        )
        for attr in items:
            result[attr] = get_striped_attr(
                module_cfg_object, "__%s__" % attr
            )

        # Versions-Information aus dem eigentlichen Module holen
        module_cfg_object = _import(package, module_name)
        result["version"] = get_striped_attr(
            module_cfg_object, "__version__"
        )

        result = self._prepare_module_data(result)

        return result

    def _read_all_moduledata(self, package_data):
        """
        Einlesen der Einstellungsdaten aus allen Konfigurationsdateien
        """
        result = []
        for module_name, module_data in package_data.iteritems():
            #~ self.response.write(module_name)
            try:
                module_data.update(
                    self._get_module_data(module_data["package"], module_name)
                )
            except Exception, e:
                self.page_msg(
                    "Can't get Data for %s.%s: %s" % (
                        module_data["package"], module_name, e
                    )
                )
                continue

            module_data["module_name"] = module_name
            result.append(module_data)
        return result

    def _prepare_module_data(self, module_data):
        """
        Aufbereiten der Daten für die installation:
            - Deinstallationsdaten serialisieren
        """
        # Deinstallationsdaten serialisieren
        if module_data["SQL_deinstall_commands"] != None:
            module_data["SQL_deinstall_commands"] = pickle.dumps(
                module_data["SQL_deinstall_commands"]
            )

        return module_data

    #________________________________________________________________________________________
    # Informationen über in der DB installierte Module / Plugins

    def get_installed_modules_info(self):
        try:
            installed_modules_info = self.db.get_installed_modules_info()
        except Exception, e:
            self.response.write("<h1>Can't get installed module data from DB:</h1>")
            self.response.write("<h4>%s</h4>" % e)
            self.response.write("<h3>Did you run install_PyLucid.py ???</h3>")
            return None
        else:
            return installed_modules_info

    #________________________________________________________________________________________
    # Hilfs methoden

    def execute_SQL_commands(self, command_list):
        """
        Wird beim installalieren und deinstallieren verwendet.
        """
        for command in command_list:
            self.response.write("execute '%s...'" % cgi.escape(" ".join(command.split(" ",3)[:3])),)
            try:
                self.db.get(command)
            except Exception, e:
                self.response.write("Error: %s" % e)
            else:
                self.response.write("OK")

    def debug_installed_modules_info(self, module_id=None):
        """
        Listet alle Module/Plugins, mit ihren registrierten Methoden und CGI-depent-Daten auf
        """
        self.response.write("<h3>Registered Methods of all installed Plugins</h3>")
        self.response.write("<p>select Module to get more Infomation</p>")

        self.link("menu")

        plugins_data = self.get_installed_modules_info()

        data_dict = {}

        self.response.write("<ul>")
        for plugin in plugins_data:
            data_dict[plugin['id']] = plugin["package_name"], plugin['module_name']
            url = self.URLs.make_current_action_link(str(plugin['id']))
            self.response.write('<li><a href="%s">' % url)
            self.response.write(
                '%s.<strong style="color:blue">%s</strong></a>' % (
                    plugin["package_name"], plugin['module_name']
                )
            )
            self.response.write('<small style="color:grey">(plugin id: %s)</small>' % plugin['id'])
            self.response.write("</li>")
        self.response.write("</ul>")

        self.response.write("<pre>")
        if module_id:
            try:
                self.response.write(
                    '%s.<strong>%s</strong> <small>(plugin id:%s)</small>\n' % (
                        data_dict[module_id][0], data_dict[module_id][1], module_id
                    )
                )
            except KeyError, e:
                self.response.write("KeyError, Module with id '%s' not found" % e)

            self.debug_module_info(module_id)

        self.response.write("</pre>\n")

    def debug_module_info(self, module_id):

        plugindata = self.db.get_plugindata(module_id)

        if plugindata == []:
            self.response.write("Module with id: '%s' unknown!" % module_id)
            return

        keyfilter = ["internal_page_info"]
        self.tools.writeDictListTable(plugindata, self.response, keyfilter)

        self.response.write("<em>Internal pages info:</em>\n")
        internal_pages = self.db.get_internal_pages_info_by_module(module_id)
        if internal_pages == []:
            self.response.write("<small>Module has no internal pages.</small>\n")
            return

        for page_info in internal_pages:
            txt = (
                "<strong>%s</strong> - %s\n"
                "   ^- <small>markup: '%s',"
                " updated by: %s,"
                "last update: %s</small>\n\n"
            ) % (
                    page_info['name'], page_info['description'],
                    page_info['markup'],
                    page_info['lastupdateby'],
                    page_info['lastupdatetime']
            )

            self.response.write(txt)


    def debug_package_data(self, data):
        self.response.write("<h3>Debug package data:</h3>")
        for module_data in data:
            keys = module_data.keys()
            keys.sort()
            self.response.write("<h3>%s</h3>" % module_data["module_name"])
            self.response.write("<pre>")
            for key in keys:
                value = module_data[key]
                if type(value) == dict: # module_manager_data
                    self.response.write(" -"*40)
                    self.response.write("%22s :" % key)
                    keys2 = value.keys()
                    keys2.sort()
                    for key2 in keys2:
                        self.response.write("\t%20s : %s" % (key2,cgi.escape(str(value[key2]).encode("String_Escape"))))
                    self.response.write(" -"*40)
                else:
                    self.response.write("%22s : %s" % (key,cgi.escape(str(value).encode("String_Escape"))))
            self.response.write("</pre>")




