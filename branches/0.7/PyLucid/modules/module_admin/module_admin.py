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
    - NEU: debug_installed_modules_info() - Für einen besseren Überblick,
        welche Methoden in der DB registriert sind.
v0.1.1
    - NEU: reinit
v0.1
    - erste Version
"""

__todo__="""
    - CSS deinstallation
    - Fehlerausgabe bei check_moduleData
"""


import sys, os, glob, imp, cgi, urllib, pickle


debug = False
#~ debug = True

error_handling = False
package_basedir = "PyLucid"
available_packages = ("modules","buildin_plugins","plugins")
# Wenn es von _install Aufgerufen wird, wird das Template von Platte gelesen:
internal_page_file = "PyLucid/modules/module_admin/administation_menu.html"
internal_page_css = "PyLucid/modules/module_admin/administation_menu.css"

from PyLucid.system.exceptions import *
from PyLucid.system.BaseModule import PyLucidBaseModule


class InternalPage(object):
    """
    Alle Daten zusammenhängent mit der internenSeite
    """
    def __init__(self, request, response, package_dir_list, module_name, data):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = request.page_msg

        self.plugin_id = None

        self.package_dir_list = package_dir_list
        self.module_name = module_name

        self.basePath = os.sep.join(self.package_dir_list)

        self.name = data["name"]
        del(data["name"])

        self.data = data

    #_________________________________________________________________________

    def install(self, plugin_id):
        """
        Installiert die interne Seite mit zugehörigen CSS und JS Daten
        """
        self.plugin_id = plugin_id

        # Hinweis: template_engine und markup werden von self.db umgewandelt
        # in IDs!
        self.response.write("\t\tinstall internal page '%s'..." % self.name)
        internal_page = {
            "name"              : self.name,
            "plugin_id"         : self.plugin_id,
            "category"          : self.module_name,
            "description"       : self.data["description"],
            "template_engine"   : self.data["template_engine"],
            "markup"            : self.data["markup"],
        }

        internal_page_filename = "%s/%s.html" % (self.basePath, self.name)
        print internal_page_filename


        self.response.write("%s..." % internal_page_filename)
        try:
            lastupdatetime, content = self._getFiledata(internal_page_filename)
        except Exception, e:
            self.response.write("Error reading Template-File: %s\n" % e)
            return

        internal_page["content"] = content

        try:
            self.db.new_internal_page(internal_page, lastupdatetime)
        except Exception, e:
            raise IntegrityError(
                "Can't save new internal page to DB: %s - %s" % (
                    sys.exc_info()[0], e
                )
            )
        else:
            self.response.write("OK\n")
            print "OK"

        # Evtl. vorhandene CSS Datei auch in die DB bringen
        self.installCSS()

    def installCSS(self):
        CSS_filename = "%s/%s.css" % (self.basePath, self.name)
        if not os.path.isfile(CSS_filename):
            # Es gibt keine zusätzlichen Styles ;)
            return

        print CSS_filename

        self.response.write("\t\tinstall CSS '%s'..." % CSS_filename)
        try:
            lastupdatetime, content = self._getFiledata(CSS_filename)
        except Exception, e:
            self.response.write("Error reading CSS-File: %s\n" % e)
            return

        style = {
            "name"          : self.name,
            "plugin_id"     : self.plugin_id,
            "description"   : "module/plugin stylesheet",
            "content"       : content,
        }

        try:
            self.db.new_style(style)
        except Exception, e:
            raise IntegrityError(
                "Can't save new Style to DB: %s - %s" % (
                    sys.exc_info()[0], e
                )
            )


    def _getFiledata(self, filename):
        try:
            lastupdatetime = os.stat(filename).st_mtime
        except:
            lastupdatetime = None

        f = file(filename, "rU")
        content = f.read()
        f.close()

        return lastupdatetime, content

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("<ul>")
        self.page_msg("<strong>internal Page</strong> '%s':" % self.name)
        for k,v in self.data.iteritems():
            self.page_msg("<li>%s: %s</li>" % (k,v))
        self.page_msg("</ul>")


class Method(object):
    """
    Daten einer Methode von einem Module/Plugin
    """
    def __init__(self, request, response, package_dir_list, module_name, name):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = request.page_msg

        self.package_dir_list = package_dir_list
        self.module_name = module_name
        self.name = name

        self.data = {}

        # defaults
        self.internalPage = None
        self.data["must_login"] = True
        self.data["must_admin"] = True

    def assimilateConfig(self, config):
        if 'internal_page_info' in config:
            internal_page_info = config['internal_page_info']

            # Eine interne Seite muß keinen speziellen Namen haben, dann nehmen
            # wir einfach den Namen der Methode:
            internal_page_info["name"] = internal_page_info.get(
                "name", self.name
            )

            self.internalPage = InternalPage(
                self.request, self.response,
                self.package_dir_list, self.name, internal_page_info
            )
            del(config['internal_page_info'])

        self.data.update(config)

    #_________________________________________________________________________

    def install(self, moduleID):
        """
        Installiert Methode in die DB
        """
        self.response.write("\tinstall method '%s'..." % self.name)
        # methode in DB eintragen
        self.db.register_plugin_method(moduleID, self.name, self.data)
        self.response.write("OK\n")

        if self.internalPage != None:
            # zugehörige interne Seite in DB eintragen
            self.internalPage.install(moduleID)

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("<ul>")
        self.page_msg("Debug for method '<strong>%s</strong>':" % self.name)
        for k,v in self.data.iteritems():
            self.page_msg("<li>%s: %s</li>" % (k,v))
        if self.internalPage != None:
            self.internalPage.debug()
        self.page_msg("</ul>")


class Module(object):
    """
    Daten eines Modules
    """
    def __init__(self, request, response, name):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = request.page_msg

        self.name = name

        # defaults setzten:
        self.data = {
            "module_name": self.name,
            "installed": False,
            "active": False,
            "essential_buildin": False,
            "important_buildin": False,
        }
        self.methods = []

    def add_fromDisk(self, package_dir_list):
        self.data["config_name"] = "%s_cfg" % self.name
        self.data["package_dir_list"] = package_dir_list
        self.data["package_name"] = ".".join(package_dir_list)

        configObject = self._readConfigObject()
        self._assimilateConfig(configObject)
        self._setupMethods(configObject)
        self.data["version"] = self._getVersionInfo()

    def add_fromDB(self, RAWdict):
        #~ print RAWdict
        package_dir_list = RAWdict['package_name']
        package_dir_list = package_dir_list.split("/")

        self.data["installed"] = True

        keys = (
            "id", "version",
            "author", "description", "url"
        )
        for key in keys:
            self.data[key] = RAWdict[key]

        # FIXME: must change in DB?!?!?
        self.data["module_name"] = RAWdict["module_name"]

        self.data["builtin"] = False
        if RAWdict["active"] == -1:
            self.data["builtin"] = True
            self.data["active"] = True
        elif RAWdict["active"] == 1:
            self.data["active"] = True
        else:
            self.data["active"] = False

    #_________________________________________________________________________
    # Config-Daten von Platte lesen

    def _readConfigObject(self):
        """
        Liefert alle Daten zu einem Modul, aus der zugehörigen config-Datei.
        """
        package_dir_list = self.data["package_dir_list"][:] # Kopie der Liste
        package_dir_list.append(self.data["config_name"])
        packagePath = ".".join(package_dir_list)

        try:
            module_cfg_object = __import__(
                packagePath, {}, {}, [self.data["config_name"]]
            )
        except SyntaxError, e:
            msg = "Can't import %s.%s: %s" % (
                packagePath, self.data["module_name"], e
            )
            raise SyntaxError, msg
        else:
            return module_cfg_object

    def _getVersionInfo(self):
        package_dir_list = self.data["package_dir_list"]
        package_dir_list.append(self.name)
        packagePath = ".".join(package_dir_list)

        try:
            version = __import__(
                packagePath, {}, {}, [self.name]
            ).__version__
        except ImportError, e:
            msg = "Can't import __version__ from Module '%s' (Error: %s)" % (
                packagePath, e
            )
            raise ImportError, msg

        return version

    def _assimilateConfig(self, configObject):
        def getattrStriped(object, attr):
            result = getattr(object, attr)
            if type(result) == str:
                return result.strip()
            return result

        # Metadaten verarbeiten, die immer da sein müßen!
        keys = (
            "author", "url", "description", "long_description",
        )
        for key in keys:
            keyTag = "__%s__" % key
            try:
                self.data[key] = getattrStriped(configObject, keyTag)
            except AttributeError, e:
                msg = (
                    "Module/plugin config file '...%s' has no Entry for '%s'!"
                ) % (configObject.__file__[-35:], keyTag)
                raise AttributeError, msg

        # Optionale Einstellungsdaten
        self.data["module_manager_debug"] = getattr(
            configObject, "module_manager_debug", False
        )

        keys = (
            "SQL_install_commands", "SQL_deinstall_commands",
        )
        for key in keys:
            self.data[key] = getattr(configObject, key, None)

        keys = (
            "essential_buildin", "important_buildin"
        )
        for key in keys:
            keyTag = "__%s__" % key
            self.data[key] = getattr(configObject, keyTag, False)

    def _setupMethods(self, configObject):
        module_manager_data = configObject.module_manager_data
        for methodName, methodData in module_manager_data.iteritems():
            method = Method(
                self.request, self.response,
                self.data["package_dir_list"], self.name, methodName
            )
            method.assimilateConfig(methodData)
            self.methods.append(method)

    #_________________________________________________________________________

    def install(self, autoActivate=False):
        """
        Installiert das Modul und all seine Methoden
        """
        self.response.write(
            "register Module '<strong>%s</strong>'..." % self.name
        )

        if autoActivate:
            self.data["active"] = True

        # Modul in DB eintragen
        id = self.db.install_plugin(self.data)
        self.response.write("OK\n")

        self.response.write("register all Methodes:\n")
        # Alle Methoden in die DB eintragen
        for method in self.methods:
            method.install(id)

    def first_time_install(self):
        """
        installiert nur Module die wichtig sind
        """
        if self.data["essential_buildin"] or self.data["important_buildin"]:
            self.install(autoActivate=True)

    #_________________________________________________________________________

    def getData(self):
        return self.data

    #_________________________________________________________________________

    def debug(self):
        self.page_msg("<ul>")
        self.page_msg("Module '<strong>%s</strong>' debug:" % self.name)
        for k,v in self.data.iteritems():
            self.page_msg("<li><em>%s</em>: %s</li>" % (k,v))
        for method in self.methods:
            method.debug()
        self.page_msg("</ul>")






class Modules(object):
    """
    Daten aller Module
    """
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = request.page_msg

        self.data = {}

    def readAllModules(self):
        self._get_from_db()
        self.read_packages()

    def addModule(self, module_name, package_dir_list):
        if self.data.has_key(module_name):
            # Daten sind schon aus der DB da.
            return

        module = Module(self.request, self.response, module_name)
        module.add_fromDisk(package_dir_list)
        self.data[module_name] = module

    def addModule_fromDB(self, moduledata):
        module_name = moduledata['module_name']
        module = Module(self.request, self.response, module_name)
        module.add_fromDB(moduledata)
        self.data[module_name] = module

    #_________________________________________________________________________

    def getModuleStatusList(self):
        "Liste alle vorhandenden Module"
        result = []
        for module_name, moduleData in self.data.iteritems():
            data = moduleData.getData()
            result.append(data)

        return result

    #_________________________________________________________________________

    def read_packages(self):
        """
        Alle verfügbaren packages durch scannen.
        """
        for package in available_packages:
            self._read_one_package(package)

    def _read_one_package(self, package_name):
        """
        Dateiliste eines packages erstellen.
        """
        packageDir = os.path.join(package_basedir, package_name)
        for item in os.listdir(packageDir):
            itemDir = os.path.join(package_basedir, package_name, item)

            if not os.path.isdir(itemDir):
                continue

            init = os.path.join(itemDir, "__init__.py")
            if not os.path.isfile(init):
                # Verz. hat keine init-Datei
                continue

            module_cfg = os.path.join(itemDir, "%s_cfg.py" % item)
            if not os.path.isfile(module_cfg):
                # Kein Config-Datei vorhanden -> kein PyLucid-Module
                continue

            module = os.path.join(itemDir, "%s.py" % item)
            if os.path.isfile(module):
                self.addModule(
                    module_name = item,
                    package_dir_list = [package_basedir, package_name, item]
                )

    #_________________________________________________________________________
    # install

    def installModule(self, module_name, package_name):
        """
        Installieren eines bestimmten Modules/Plugins
        """
        package_name = package_name.split(".")
        self.addModule(module_name, package_name)

        module = self.data[module_name]
        module.install()

    def first_time_install(self):
        """
        Alle wichtigen Module installieren
        """
        try:
            for module_name, module in self.data.iteritems():
                module.first_time_install()
        except IntegrityError, e:
            msg = (
                "install all modules failed!"
                " make DB rollback"
                " Error: %s"
            ) % e
            self.response.write(msg)
            self.db.rollback()
        else:
            self.db.commit()

    #_________________________________________________________________________
    # Informationen über in der DB installierte Module / Plugins

    def _get_from_db(self):
        try:
            installed_modules_info = self.db.get_installed_modules_info()
        except Exception, e:
            self.response.write(
                "<h1>Can't get installed module data from DB:</h1>"
            )
            self.response.write("<h4>%s</h4>" % e)
            self.response.write("<h3>Did you run install_PyLucid.py ???</h3>")
            raise #FIXME!
        for moduleData in installed_modules_info:
            self.addModule_fromDB(moduleData)

    #_________________________________________________________________________
    # Debug

    def debug(self):
        self.page_msg("Module Debug:")
        oldPageMsgRaw = self.page_msg.raw
        self.page_msg.raw = True

        self.page_msg("<ul>")
        for module_name, module in self.data.iteritems():
            self.page_msg("<li>%s:" % module_name)
            module.debug()
            self.page_msg("</li>")
        self.page_msg("</ul>")

        self.page_msg.raw = oldPageMsgRaw









class ModuleAdmin(PyLucidBaseModule):
    #~ def __init__(self, *args, **kwargs):
        #~ super(ModuleAdmin, self).__init__(*args, **kwargs)

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
        moduleData = Modules(self.request, self.response)
        moduleData.readAllModules()
        #~ if debug:
        moduleData.debug()

        moduleData = moduleData.getModuleStatusList()

        context_dict = {
            "version"       : __version__,
            "moduleData"    : moduleData,
            "action_url"    : self.URLs.currentAction(),
        }

        if self.request.runlevel == "install":
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

            from PyLucid.system.template_engines import render_jinja
            content = render_jinja(install_template, context_dict)
            self.response.write(content)

            # CSS Daten einfach rein schreiben:
            try:
                f = file(internal_page_css, "rU")
                cssData = f.read()
                f.close()
            except:
                pass
            else:
                self.response.write('<style type="text/css">')
                self.response.write(cssData)
                self.response.write('</style>')

        else:
            # Normal als Modul aufgerufen
            self.db.print_internal_TAL_page(
                "module_admin_administation_menu", context_dict
            )
            self.link("menu")

    #_________________________________________________________________________
    # install

    def install(self, package_name, module_name):
        """
        Modul in die DB eintragen
        """
        data = Modules(self.request, self.response)

        self.response.write(
            "<h3>Install %s.<strong>%s</strong></h3>" % (
                package_name, module_name
            )
        )

        self.response.write("<pre>")
        data.installModule(module_name, package_name)
        self.response.write("</pre>")
        return

    def first_time_install(self, simulation=True):
        """
        Installiert alle wichtigen Module/Plugins
        Das sind alle Module, bei denen:
        "essential_buildin" == True oder "important_buildin" == True
        """
        self.response.write("<h2>First time install:</h2>\n")
        self.response.write("<pre>\n")

        self._truncateTables()

        data = Modules(self.request, self.response)
        data.read_packages() # Nur die Plugins von Platte laden
        if debug:
            data.debug()

        data.first_time_install()

    def _truncateTables(self):
        self.response.write("<strong>truncate tables:</strong>\n")
        tables = (
            "plugins", "plugindata", "pages_internal",
            "pages_internal_category"
        )
        for table in tables:
            self.response.write("\t* truncate table %s..." % table)

            try:
                self.db.cursor.execute("TRUNCATE TABLE $$%s" % table)
            except Exception, e:
                self.response.write(sys.exc_info()[0],":", e)
                self.response.write("(Have you first init the tables?)")
                return
            else:
                self.response.write("OK\n")

        self.response.write("<strong>Cleanup Stylesheet table:</strong>\n")
        self.db.delete_all_plugin_styles()






class muell:

    #_________________________________________________________________________

    def register_methods(self, package, module_name, moduleData, simulation):
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
        for method_name in moduleData["module_manager_data"]:
            self.response.write("\t* %s " % method_name)
            method_cfg = moduleData["module_manager_data"][method_name]

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

        #~ for parent_method in moduleData["module_manager_data"]:
            #~ method_cfg = moduleData["module_manager_data"][parent_method]

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

    def install(self, package_name, module_name):
        """
        Modul in die DB eintragen
        """
        data = Modules(self.request, self.response)

        self.response.write(
            "<h3>Install %s.<strong>%s</strong></h3>" % (
                package_name, module_name
            )
        )

        self.response.write("<pre>")
        data.installModule(module_name, package_name)
        self.response.write("</pre>")
        return

        print module_name
        self.link("administation_menu")
        package = moduleData["packagePath"]


        if self.check_moduleData(moduleData) == True:
            self.response.write("<h3>Error</h3>")
            self.response.write(
                "<h4>module config data failed. Module was not installed!!!</h4>"
            )
            self.debug_package_data([moduleData])
            return

        #~ self.debug_package_data([moduleData])

        ##_____________________________________________
        # In Tabelle "plugins" eintragen
        self.response.write("register plugin %s.%s..." % (package, module_name),)
        #~ self.response.write(package, module_name)
        #~ self.response.write(moduleData)
        #~ try:
        self.registered_plugin_id = self.db.install_plugin(
            moduleData, simulation
        )
        #~ except Exception, e:
            #~ self.response.write("%s: %s\n" % (sys.exc_info()[0], e))
            #~ # Evtl. ist das Plugin schon installiert.
            #~ try:
                #~ self.registered_plugin_id = self.db.get_plugin_id(
                    #~ moduleData['package_name'], moduleData['module_name']
                #~ )
            #~ except Exception, e:
                #~ raise IntegrityError("Can't get Module/Plugin ID: %s\n" % e)
        #~ else:
        self.response.write("OK\n")

        ##_____________________________________________
        # Stylesheets
        if moduleData["styles"] != None:
            self.response.write("install stylesheet:\n")
            for style in moduleData["styles"]:
                self.response.write("\t* %-25s" % style["name"])
                css_filename = os.path.join(
                    moduleData['package_name'],
                    "%s_%s.css" % (moduleData['module_name'], style["name"])
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
        # SQL Kommandos ausführen
        if moduleData["SQL_install_commands"] != None:
            self.execute_SQL_commands(
                moduleData["SQL_install_commands"], simulation
            )

        self.register_methods(package, module_name, moduleData, simulation)

        self.response.write("</pre>")
        #~ self.response.write(
            #~ 'activate this Module? <a href="%s/activate/%s">yes, enable it</a>' % (
                #~ self.URLs["action"], self.registered_plugin_id
            #~ )
        #~ )
        self.link("administation_menu")




    def check_moduleData(self, data):

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

    def is_installed(self, package, module):
        for line in self.installed_modules_info:
            if line["package_name"] == package and line["module_name"] == module:
                return True
        return False

    #~ def _filter_cfg(self, package_data):
        #~ """
        #~ Nur Module/Plugins herrausfiltern zu denen es auch Konfiguration-Daten gibt.
        #~ """
        #~ not_installed_data = {}
        #~ installed_data = []
        #~ filelist = package_data.keys()
        #~ for module_name, moduleData in package_data.iteritems():
            #~ if not module_name.endswith("_cfg"):
                #~ continue

            #~ clean_module_name = module_name[:-4]
            #~ if not clean_module_name in filelist:
                #~ # Zur Config-Datei gibt's kein Module?!? -> Wird ausgelassen
                #~ continue

            #~ if self.is_installed(moduleData["package"], clean_module_name):
                #~ # Schon installierte Module auslassen
                #~ continue

            #~ # Das Modul ist noch nicht installiert!
            #~ not_installed_data[clean_module_name] = moduleData
            #~ not_installed_data[clean_module_name]["cfg_file"] = module_name

        #~ return not_installed_data

    def _read_all_moduledata(self, package_data):
        """
        Einlesen der Einstellungsdaten aus allen Konfigurationsdateien
        """
        result = []
        for module_name, moduleData in package_data.iteritems():
            #~ self.response.write(module_name)
            try:
                moduleData.update(
                    self._get_moduleData(moduleData["package"], module_name)
                )
            except Exception, e:
                self.page_msg(
                    "Can't get Data for %s.%s: %s" % (
                        moduleData["package"], module_name, e
                    )
                )
                continue

            moduleData["module_name"] = module_name
            result.append(moduleData)
        return result

    def _prepare_moduleData(self, moduleData):
        """
        Aufbereiten der Daten für die installation:
            - Deinstallationsdaten serialisieren
        """
        # Deinstallationsdaten serialisieren
        if moduleData["SQL_deinstall_commands"] != None:
            moduleData["SQL_deinstall_commands"] = pickle.dumps(
                moduleData["SQL_deinstall_commands"]
            )

        return moduleData



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
        for moduleData in data:
            keys = moduleData.keys()
            keys.sort()
            self.response.write("<h3>%s</h3>" % moduleData["module_name"])
            self.response.write("<pre>")
            for key in keys:
                value = moduleData[key]
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




