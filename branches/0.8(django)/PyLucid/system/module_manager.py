#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Module Manager

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""


#~ import sys, os, glob, imp, cgi, urllib

#~ from PyLucid.system.exceptions import PyLucidException



#~ debug = False
debug = True


from PyLucid.models import Plugin, Plugindata


def get_module_class(package_name, module_name):
    module = __import__(
        "%s.%s" % (package_name, module_name), {}, {}, [module_name]
    )
    module_class = getattr(module, module_name)
    return module_class

def make_instance(module_class, request, response):
    class_instance = module_class(request, response)
    return class_instance

def get_unbound_method(class_instance, method_name):
    unbound_method = getattr(
        class_instance, method_name
    )
    return unbound_method

def handleTag(module_name, request, response):

    method_name = "lucidTag"

    response.write("TAG: %s" % module_name)

    if module_name != "page_style":
        return

    print "-"*79
    print "TAG:", module_name
    try:
        plugin = Plugin.objects.get(module_name=module_name)
    except Plugin.DoesNotExist:
        print "Nicht da!"
        return

    print plugin.package_name
    #~ try:
    plugin_data = Plugindata.objects.get(plugin_id=plugin.id, method_name=method_name)
    #~ except Plugindata.DoesNotExist:
        #~ print "nicht da 2"
        #~ return

    print plugin_data

    try:
        module_class=get_module_class(plugin.package_name, module_name)
    except Exception, e:
        print "Import Error:", e
        return

    class_instance = make_instance(module_class, request, response)
    unbound_method = get_unbound_method(class_instance, method_name)
    unbound_method()

    return "OK"

def handleFunction(function, function_info):
    print "FUNCTION:", function, function_info
    return "OK"





class module_manager:
    def __init__(self):
        # Alle Angaben werden bei run_tag oder run_function ausgefüllt...
        self.module_name    = "undefined"
        self.method_name    = "undefined"

    def init2(self, request, response):
        self.request        = request
        self.response       = response

        # shorthands
        self.environ        = request.environ
        self.staticTags     = request.staticTags
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences
        self.URLs           = request.URLs
        self.log            = request.log
        self.module_manager = request.module_manager
        self.tools          = request.tools
        self.render         = request.render
        self.templates      = request.templates

        self.page_msg       = response.page_msg

        self.plugin_data = plugin_data(request, response)

        self.isadmin = self.session.get("isadmin", False)
        if self.preferences["ModuleManager_error_handling"] == False or \
                                                        self.isadmin == True:
            # Fehler führen zu einem CGI-Traceback
            self.error_handling = False
        else:
            # Fehler werden in einem Satz zusammen gefasst
            self.error_handling = True

    #_________________________________________________________________________

    def run_tag(self, tag):
        """
        Ausführen von:
        <lucidTag:'tag'/>
        """

        if tag in self.staticTags:
            return self.staticTags[tag]

        if tag.find(".") != -1:
            self.module_name, self.method_name = tag.split(".",1)
        else:
            self.module_name = tag
            self.method_name = "lucidTag"

        return self._run_module_method()


    def run_function(self, function_name, function_info):
        """
        Ausführen von:
        <lucidFunction:'function_name'>'function_info'</lucidFunction>
        """
        self.module_name = function_name
        self.method_name = "lucidFunction"

        return self._run_module_method(function_info = function_info)


    def run_command(self):
        """
        ein Kommando ausführen.
        """
        pathInfo = self.environ["PATH_INFO"].split("&")[0]
        pathInfo = pathInfo.strip("/")
        pathInfo = pathInfo.split("/")[1:]

        try:
            self.module_name = pathInfo[1]
            self.method_name = pathInfo[2]
        except IndexError:
            self.page_msg("Wrong command path!")
            return

        title = "%s.%s" % (self.module_name, self.method_name)
        title = title.replace(".", " / ").replace("_", " ")
        self.request.staticTags["page_title"] = title

        function_info = pathInfo[3:]

        if function_info == []:
            return self._run_module_method()
        else:
            return self._run_module_method(function_info = function_info)

    def run_direkt(self, module_name, method_name, *args, **kwargs):
        """
        Führt direkt eine Methode eines Plugin/Modul aus.
        """
        self.module_name = module_name
        self.method_name = method_name

        return self._run_module_method(*args, **kwargs)


    #_________________________________________________________________________

    def _run_module_method(self, *args, **kwargs):
        """
        Führt eine Methode eines Module aus.
        Kommt es irgendwo zu einem Fehler, ist es die selbsterstellte
        "RunModuleError"-Exception mit einer passenden Fehlermeldung.
        """
        if debug: self.page_msg("*args, **kwargs:", *args, **kwargs)
        try:
            self.plugin_data.setup_module(self.module_name, self.method_name)
        except PluginMethodUnknown, e:
            # Fehler nur anzeigen
            msg = "run %s.%s, error '%s'" % (
                self.module_name, self.method_name,e
            )
            self.page_msg(msg)
            return msg
        except RunModuleError, e:
            msg = "[setup module '%s.%s' unknown Error: %s]" % (
                self.module_name, self.method_name, e
            )
            if self.error_handling == False:
                # Traceback erzeugen
                raise RunModuleError(msg)
            else:
                # Fehler nur anzeigen
                self.page_msg(msg)
                return str(msg)

        #~ self.page_msg(self.module_name, self.method_name, self.plugin_data.keys())

        try:
            self.plugin_data.check_rights()
        except RightsError, e:
            if self.plugin_data["no_rights_error"] == 1:
                # Rechte Fehler sollen nicht angezeigt werden
                return ""
            else:
                self.page_msg(e)
                return ""

        self.plugin_data.setup_URLs()

        try:
            moduleOutput = self._run_method(*args, **kwargs)
        except RunModuleError, e:
            self.page_msg(e)
            moduleOutput = ""

        self.plugin_data.restore_URLs()

        return moduleOutput


    def _run_with_error_handling(self, unbound_method, *args, **kwargs):
        if self.plugin_data.plugin_debug == True:
            self.page_msg(
                "function_info for method '%s': %s" % (
                    self.method_name, function_info
                )
            )
        try:
            # Dict-Argumente übergeben
            return unbound_method(*args, **kwargs)
        except SystemExit:
            # Module dürfen zum Debugging auch einen sysexit machen...
            pass
        except TypeError, e:
            if not str(e).startswith(unbound_method.__name__):
                # Der Fehler ist nicht hier, bei der Dict übergabe zur
                # unbound_method() aufgetretten, sondern irgendwo im
                # Modul selber!
                raise # Vollen Traceback ausführen

            # Ermitteln der Argumente die wirklich von der unbound_method()
            # verlangt werden
            import inspect
            args = inspect.getargspec(unbound_method)
            real_function_info = args[0][1:]
            real_function_info.sort()
            argcount = len(real_function_info)

            msg = "ModuleManager 'function_info' error: "
            msg += "%s() takes exactly %s arguments %s, " % (
                unbound_method.__name__, argcount, real_function_info
            )
            msg += "and I have given *args: %s - **kwargs: %s " % (
                args, kwargs
            )

            raise RunModuleError(msg)


    def _run_method(self, *args, **kwargs):
        """
        Startet die Methode und verarbeitet die Ausgaben
        """
        def run_error(msg):
            msg = "[Can't run '%s.%s': %s]" % (
                self.module_name, self.method_name, msg
            )
            if self.error_handling == True:
                # Fehler nur anzeigen
                raise RunModuleError(msg) # Wird später abgefangen
            else:
                # Traceback erzeugen
                raise Exception(msg)


        self.request.module_data = {
            "id": self.plugin_data.module_id,
            "module_name": self.plugin_data.module_name,
            "method_name": self.plugin_data.method_name
        }

        module_class = self._get_module_class()
        class_instance = self._get_class_instance(
            self.request, module_class
        )
        unbound_method = self._get_unbound_method(class_instance)

        self.setup_sys_path()

        # Methode "ausführen"
        if self.error_handling == True: # Fehler nur anzeigen
            try:
                output = self._run_with_error_handling(
                    unbound_method, *args, **kwargs
                )
            except KeyError, e:
                run_error("KeyError: %s" % e)
            except PyLucidException, e:
                # Interne Fehlerseite wurde geforfen, aber Fehler sollen
                # als Satz zusammen gefasst werden.
                # Bei config.ModuleManager_error_handling = True
                raise RunModuleError(e.get_error_page_msg())
            except Exception, e:
                run_error(e)
        else:
            output = self._run_with_error_handling(
                unbound_method, *args, **kwargs
            )

        if hasattr(class_instance, "plugin_cfg"):
            # Das Modul benutzt plugin_cfg.
            # Speichern der evtl. geänderten Plugin config.
            class_instance.plugin_cfg.commit()

        self.reset_sys_path()

        return output

    #_________________________________________________________________________

    def setup_sys_path(self):
        """
        Fügt den Path zum aktuell auszuführenden Module/Plugin in den
        sys.path ein
        """
        package_path = self.plugin_data.package_name
        package_path = package_path.replace(".",os.sep)
        #~ self.page_msg(package_path)
        sys.path.insert(0,package_path)

    def reset_sys_path(self):
        """
        Nach dem Ausführen des Modules/Plugins wird der eingefügte Path wieder
        aus dem sys.path gelöscht
        """
        sys.path = sys.path[1:]

    #_________________________________________________________________________

    def _get_module_class(self):
        """
        Importiert das Modul und liefert die Klasse als Objekt zurück
        Nutzt dazu:
            - self.module_name
            - self.plugin_data.package_name
        """
        if self.plugin_data.plugin_debug():
            msg = (
                "Import module mit error handling: %s"
            ) % self.preferences["ModuleManager_error_handling"]
            self.page_msg(msg)

        def _import(package_name, module_name):
            return __import__(
                "%s.%s" % (package_name, module_name), {}, {}, [module_name]
            )

        if self.preferences["ModuleManager_error_handling"] == False:
            import_object = _import(
                self.plugin_data.package_name, self.module_name
            )

        try:
            import_object = _import(
                self.plugin_data.package_name, self.module_name
            )
        except Exception, e:
            raise RunModuleError(
                "[Can't import Modul '%s': %s]" % (self.module_name, e)
            )

        try:
            return getattr(import_object, self.module_name)
        except Exception, e:
            raise RunModuleError(
                "[Can't get class '%s' from module '%s': %s]" % (
                    self.module_name, self.module_name, e
                )
            )

    def _get_class_instance(self, request_obj, module_class):
        """
        Instanziert die Module/Plugin Klasse und liefert diese zurück
        """
        if self.error_handling == True:
            # Fehler nur anzeigen
            try:
                class_instance = module_class(request_obj, self.response)
            except Exception, e:
                raise RunModuleError(
                    "[Can't make class intance from module '%s': %s]" % (
                        self.module_name, e
                    )
                )
        else:
            # Traceback erzeugen
            try:
                class_instance = module_class(request_obj, self.response)
            except TypeError, e:
                try:
                    import inspect
                    all_args = inspect.getargspec(module_class.__init__)
                except Exception, e:
                    all_args = "[Error: %s]" % e
                msg = (
                    "TypeError, module '%s.%s': %s"
                    " --- module-class must received: (request, response) !"
                    " --- all args: %s"
                ) % (self.module_name, self.method_name, e, all_args)
                raise TypeError(msg)

        return class_instance

    def _get_unbound_method(self, class_instance):
        """
        Holt die zu startende Methode aus der Modul/Plugin-Klasse herraus,
        liefert diese als 'unbound method' zurück.
        """
        ##____________________________________________________________________
        ## Methode per getattr holen
        if self.error_handling == True: # Fehler nur anzeigen
            try:
                unbound_method = getattr(
                    class_instance, self.plugin_data.method_name
                )
            except Exception, e:
                raise RunModuleError(
                    "[Can't get method '%s' from module '%s': %s]" % (
                        self.plugin_data.method_name, self.module_name, e
                    )
                )
        else:
            unbound_method = getattr(
                class_instance, self.plugin_data.method_name
            )

        return unbound_method

    #_________________________________________________________________________
    # Zusatz Methoden für die Module selber

    def build_menu(self):
        result = ""
        if debug:
            result += "module_manager.build_menu():"
            result += self.plugin_data.package_name
            result += self.module_name
            result += "self.plugin_data:", self.plugin_data.debug()

        menu_data = self.plugin_data.get_menu_data()
        result += '<ul class="module_manager_menu">'
        for menu_section, section_data in menu_data.iteritems():
            result += "<li><h5>%s</h5><ul>" % menu_section
            for item in section_data:
                result += '<li><a href="%s">%s</a></li>' % (
                    self.URLs.commandLink(self.module_name, item["method_name"]),
                    item["menu_description"]
                )
            result += "</ul>"
        result += "</ul>"

        return result

    #_________________________________________________________________________
    # page_msg debug

    def debug(self):
        self.page_msg("Module Manager debug:")
        self.page_msg(self.plugin_data.debug())


class ModuleManagerError(Exception):
    pass

class RunModuleError(ModuleManagerError):
    pass

class PluginMethodUnknown(ModuleManagerError):
    """
    Das Module/Plugin oder die Methode ist unbekannt, steht nicht in der DB
    """
    pass

class RightsError(ModuleManagerError):
    """
    Ausführungsrechte Stimmen nicht
    """
    pass
















