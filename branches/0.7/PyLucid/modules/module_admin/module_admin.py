#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Admin

Einrichten/Konfigurieren von Modulen und Plugins
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

        self.data = data

    #_________________________________________________________________________

    def install(self, plugin_id):
        """
        Installiert die interne Seite mit zugehörigen CSS und JS Daten
        """
        self.plugin_id = plugin_id

        msg = (
            "<li>install internal page '<strong>%s</strong>'...<ul>\n"
        ) % self.name
        self.response.write(msg)

        lastupdatetime_list = []

        html, lastupdatetime = self._getAdditionFiles("html", "HTML")
        lastupdatetime_list.append(lastupdatetime)

        css, lastupdatetime = self._getAdditionFiles("css", "StyleSheet")
        lastupdatetime_list.append(lastupdatetime)

        js, lastupdatetime = self._getAdditionFiles("js", "JavaScript")
        lastupdatetime_list.append(lastupdatetime)

        # Als Grundlage dient das neuste Datum
        lastupdatetime = max(lastupdatetime_list)

        # Hinweis: template_engine und markup werden von self.db umgewandelt
        # in IDs!
        internal_page = {
            "name"              : self.name,
            "plugin_id"         : self.plugin_id,
            "category"          : self.module_name,
            "description"       : self.data["description"],
            "content_html"      : html,
            "content_css"       : css,
            "content_js"        : js,
            "template_engine"   : self.data["template_engine"],
            "markup"            : self.data["markup"],
        }

        try:
            self.db.new_internal_page(internal_page, lastupdatetime)
        except Exception, e:
            raise IntegrityError(
                "Can't save new internal page to DB: %s - %s" % (
                    sys.exc_info()[0], e
                )
            )
        else:
            self.response.write("</ul><li>internal page saved! OK</li>\n")

    def _getAdditionFiles(self, ext, name):
        filename = "%s/%s.%s" % (self.basePath, self.name, ext)
        if not os.path.isfile(filename):
            # Es gibt keine zusätzliche Datei ;)
            return "", 0

        msg = "<li>read %s '%s'..." % (name, filename)
        self.response.write(msg)
        try:
            lastupdatetime, content = self._getFiledata(filename)
        except Exception, e:
            self.response.write(
                "Error reading %s-File: %s</li>\n" % (
                    name, e
                )
            )
            return "", 0
        else:
            self.response.write("OK</li>\n")
            return content, lastupdatetime

    def _getFiledata(self, filename):
        try:
            lastupdatetime = os.stat(filename).st_mtime
        except:
            lastupdatetime = None

        f = file(filename, "rU")
        content = f.read()
        f.close()

        try:
            content = unicode(content, "utf8")
        except UnicodeError, e:
            self.response.write(
                "UnicodeError: Use 'replace' error handling..."
            )
            content = unicode(content, "utf8", errors='replace')

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
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = request.page_msg

    def add(self, package_dir_list, module_name, name):
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

        self.data.update(config)

    #_________________________________________________________________________

    def install(self, moduleID):
        """
        Installiert Methode in die DB
        """
        msg = (
            "<li>install method '<strong>%s</strong>'..."
        ) % self.name
        self.response.write(msg)

        # methode in DB eintragen
        self.db.register_plugin_method(moduleID, self.name, self.data)
        self.response.write("OK</li>\n")

        if self.internalPage != None:
            # zugehörige interne Seite in DB eintragen
            self.response.write('<li><ul class="install_ipages">\n')
            self.internalPage.install(moduleID)
            self.response.write("</ul></li>\n")

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
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # shorthands
        self.db             = request.db
        self.page_msg       = request.page_msg

    def add(self, name):
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
            "id", "version", "author", "description",
            "url", "SQL_deinstall_commands"
        )
        for key in keys:
            self.data[key] = RAWdict.get(key, None)

        # FIXME: must change in DB?!?!?
        self.data["module_name"] = RAWdict["module_name"]

        self.data["builtin"] = False

        if RAWdict.get("active",0) == 0:
            self.data["active"] = False
        elif RAWdict["active"] == -1:
            self.data["builtin"] = True
            self.data["active"] = True
        elif RAWdict["active"] == 1:
            self.data["active"] = True

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
            #~ cfg = module_cfg_object
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
            method = Method(self.request, self.response)
            method.add(self.data["package_dir_list"], self.name, methodName)
            method.assimilateConfig(methodData)
            self.methods.append(method)

    #_________________________________________________________________________

    def install(self, autoActivate=False):
        """
        Installiert das Modul und all seine Methoden
        """
        self.response.write("<h4>%s</h4>\n" % self.name)
        self.response.write(
            "\t<li>register Module '<strong>%s</strong>'..." % self.name
        )

        if autoActivate:
            self.data["active"] = True

        # Modul in DB eintragen
        id = self.db.install_plugin(self.data)
        self.response.write("OK</li>\n")

        self.response.write(
            '\t<li>register all Methodes:</li>\n'
            '\t<li><ul class="reg_methodes">\n'
        )
        # Alle Methoden in die DB eintragen
        for method in self.methods:
            method.install(id)

        self.response.write("\t</ul></li>\n")

    def first_time_install(self):
        """
        installiert nur Module die wichtig sind
        """
        if self.data["essential_buildin"] or self.data["important_buildin"]:
            self.install(autoActivate=True)

    #_________________________________________________________________________

    def deinstall(self):
        self.response.write(
            "delete Module '<strong>%s</strong>' in database..." % self.name
        )
        # Alle Methoden aus der DB löschen
        for method in self.methods:
            method.deinstall()

        self.db.delete_plugin(self.data["id"])

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

        module = Module(self.request, self.response)
        module.add(module_name)
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
        self.response.write(
            "<h3>install all essential and important buildin plugins</h3>"
        )
        try:
            for module_name, module in self.data.iteritems():
                self.response.write('<ul class="module_install">\n')
                module.first_time_install()
                self.response.write('</ul>\n')
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
    # DEinstall

    def deinstallModule(self, id):
        """
        Löscht das Module/Plugin mit der angegebenen ID
        """
        self.page_msg("Deinstall", id)

        RAWdict = self.db.get_plugin_data_by_id(id)
        self.addModule_fromDB(RAWdict)

        module = self.data[module_name]
        module.deinstall()

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
        if debug:
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
        self.response.write(
            "<h3>Install %s.<strong>%s</strong></h3>" % (
                package_name, module_name
            )
        )
        data = Modules(self.request, self.response)
        data.installModule(module_name, package_name)

    def first_time_install(self, simulation=True):
        """
        Installiert alle wichtigen Module/Plugins
        Das sind alle Module, bei denen:
        "essential_buildin" == True oder "important_buildin" == True
        """
        self.response.write("<h2>First time install:</h2>\n")

        self._truncateTables()

        data = Modules(self.request, self.response)
        data.read_packages() # Nur die Plugins von Platte laden
        if debug:
            data.debug()

        data.first_time_install()

    def _truncateTables(self):
        self.response.write("<hr />\n")
        self.response.write(
            "<h4>truncate tables:</h4>\n"
            "<ul>\n"
        )
        tables = ("plugins", "plugindata", "pages_internal")
        for table in tables:
            self.response.write("\t<li>truncate table %s..." % table)

            try:
                self.db.cursor.execute("TRUNCATE TABLE $$%s" % table)
            except Exception, e:
                msg = (
                    "<h4>%s: %s</h4>"
                    "<h5>(Have you first init the tables?)</h5>"
                    "</li></ul>"
                ) % (sys.exc_info()[0], e)
                self.response.write(msg)
                return
            else:
                self.response.write("OK</li>\n")
        self.response.write("</ul>\n")
        self.response.write("<hr />\n")

    #_________________________________________________________________________
    # DEinstall

    def deinstall(self, id):
        """
        Modul aus der DB löschen
        """
        data = Modules(self.request, self.response)

        #~ self.response.write(
            #~ "<h3>Deinstall %s.<strong>%s</strong></h3>" % (
                #~ package_name, module_name
            #~ )
        #~ )

        self.response.write("<pre>")
        data.deinstallModule(id)
        self.response.write("</pre>")
        return











