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


import os, sys, cgi, traceback

#~ from PyLucid.system.exceptions import PyLucidException


#~ debug = False
debug = True

from PyLucid import settings

if __name__ == "__main__": # init django for local test
    from django.core.management import setup_environ
    setup_environ(settings)

from django.http import HttpResponse

from PyLucid.system.exceptions import *
from PyLucid.system.LocalModuleResponse import LocalModuleResponse
from PyLucid.models import Plugin, Markup, PagesInternal

def _import(form_name, object_name):
    """
    from 'form_name' import 'object_name'
    """
    try:
        return __import__(form_name, {}, {}, [object_name])
    except ImportError, e:
        raise ImportError, "Can't import %s from %s: %s" % (
            object_name, form_name, e
        )

def get_module_class(package_name, module_name):
    """
    import the module/plugin and returns the class object
    """
    module = _import(
        form_name = ".".join([package_name, module_name, module_name]),
        object_name = module_name
    )
    module_class = getattr(module, module_name)
    return module_class

def get_module_config(package_name, module_name, dissolve_version_string=False,
                                                            print_debug=False):
    """
    imports the plugin and the config module and returns a merge config-object

    dissolve_version_string == True -> get the version string (__version__)
        from the module and put it into the config object
    """
    config_name = "%s_cfg" % module_name

    def get_module(object_name):
        from_name = ".".join([package_name, module_name, object_name])
        if print_debug:
            print "from %s import %s" % (from_name, object_name)
        return _import(from_name, object_name)

    config_module = get_module(config_name)

    if dissolve_version_string:
        plugin_module = get_module(module_name)

        module_version = getattr(plugin_module, "__version__", None)
        if module_version:
            # Cleanup a SVN Revision Number
            module_version = module_version.strip("$ ")
        config_module.__version__ = module_version

    return config_module

def _run(context, local_response, module_name, method_name, url_args, method_kwargs):
    """
    get the module and call the method
    """
    def error(msg):
        msg = "Error run module/plugin '%s.%s: %s" % (
            module_name, method_name, msg
        )
        context["page_msg"](msg)
        msg2 = '<i title="(Error details in page messages.)">["%s.%s" error.]</i>' % (
            module_name, method_name
        )
        local_response.write(msg2)

#    context["page_msg"](module_name, method_name)
    try:
        plugin = Plugin.objects.get(module_name=module_name)
    except Plugin.DoesNotExist:
        error("Plugin not exists in database.")
        return

    module_config = get_module_config(
        package_name = plugin.package_name,
        module_name = plugin.module_name,
        dissolve_version_string=False
    )
#    context["page_msg"](module_config.module_manager_data)
    try:
        method_cfg = module_config.module_manager_data[method_name]
    except KeyError:
        error("Can't get config for the method '%s'." % method_name)
        return

#    context["page_msg"](method_cfg)
    if method_cfg["must_login"]:
        # User must be login to use this method
        # http://www.djangoproject.com/documentation/authentication/

        context["request"].must_login = True # For static_tags an the robot tag

        if context["request"].user.username == "":
            # User is not logged in
            if method_cfg.get("no_rights_error", False) == True:
                return local_response
            else:
                raise AccessDeny

    module_class=get_module_class(plugin.package_name, module_name)
    class_instance = module_class(context, local_response)
    unbound_method = getattr(class_instance, method_name)

    output = unbound_method(*url_args, **method_kwargs)
    return output



def run(context, response, module_name, method_name, url_args=(), method_kwargs={}):
    """
    run the plugin with errorhandling
    """
    if settings.DEBUG:
        return _run(
            context, response, module_name, method_name,
            url_args, method_kwargs
        )
    else:
        try:
            return _run(
                context, response, module_name, method_name,
                url_args, method_kwargs
            )
        except Exception:
            msg = "Run Module %s.%s Error" % (module_name, method_name)
            context["page_msg"].red("%s:" % msg)
            import sys, traceback
            context["page_msg"]("<pre>%s</pre>" % traceback.format_exc())
            return msg + "(Look in the page_msg)"


#def handleTag(module_name, request, response):
#    """
#    handle a lucidTag
#    """
#    output = run(request, response, module_name, method_name = "lucidTag")
#    return output

def handle_command(context, response, module_name, method_name, url_args):
    """
    handle a _command url request
    """
    output = run(context, response, module_name, method_name, url_args)
    return output

#_____________________________________________________________________________
# some routines around modules/plugins

def file_check(module_path, dir_item):
    """
    Test if the given module_path/dir_item can be a PyLucid Plugin.
    """
    for item in ("__init__.py", "%s.py", "%s_cfg.py"):
        if "%s" in item:
            item = item % dir_item
        item = os.path.join(module_path, dir_item, item)
        if not os.path.isfile(item):
            return False
    return True

def get_module_list(module_path):
    """
    Return a dict-list with module_info for the given path.
    """
    module_list = []
    for dir_item in os.listdir(module_path):
        abs_path = os.path.join(module_path, dir_item)
        if not os.path.isdir(abs_path) or not file_check(module_path, dir_item):
            continue

        module_list.append(dir_item)

    return module_list

def get_all_modules():
    module_paths = settings.PYLUCID_MODULE_PATHS

    module_info = {}
    for path in module_paths:
        module_info[path] = get_module_list(path)

    return module_info

def install_module(package_name, module_name, module_config, active=False):
    """
    insert a module/plugin in the 'plugin' table
    """
    print "Install %s.%s..." % (package_name, module_name),
    plugin = Plugin.objects.create(
        package_name = package_name,
        module_name = module_name,
        version = module_config.__version__,
        author = module_config.__author__,
        url = module_config.__url__,
        description = module_config.__description__,
        long_description = module_config.__long_description__,
        active = active,
    )
    print "OK, ID:", plugin.id
    return plugin

def get_internalpage_files(package_name, module_name, internal_page_name):
    """
    read html, js, css files for the internal page.
    If there exist no file, it returns "".
    """
    basepath = os.path.join(
        package_name.replace(".",os.sep), module_name, internal_page_name
    )
    def read_file(ext):
        try:
            f = file(basepath + ext, "r")
            content = f.read()
            f.close()
        except IOError:
            return ""
        else:
            return content

    html = read_file(".html")
    js = read_file(".js")
    css = read_file(".css")

    return html, js, css


def install_internalpage(plugin, package_name, module_name, module_config):
    """
    install all internal pages for the given module.

    TODO: Befor create: check if page is in db
    """
#    try:
#        internal_page = PagesInternal.objects.get(name = internal_page_name)
#    except PagesInternal.DoesNotExist, e:

    module_manager_data = module_config.module_manager_data

    for method, cfg in module_manager_data.iteritems():
        if not "internal_page_info" in cfg:
            # module method has no internal page
            continue

        internal_page_info = cfg["internal_page_info"]

        # complete name:
        internal_page_name = internal_page_info.get("name", method)

        html, js, css = get_internalpage_files(
            package_name, module_name, internal_page_name
        )

        markup_name = internal_page_info.get("markup", None)
        if markup_name == None:
            markup_name = "None"
        markup = Markup.objects.get(name=markup_name)

        template_engine = internal_page_info.get("template_engine", None)
        if template_engine:
            print "*** INFO: ***"
            print " - 'template_engine' key in internal_page_info is obsolete!"
            print " - Only django template engine is supported!"

        internal_page_name = ".".join([module_name, internal_page_name])
        print "install internal page '%s'..." % internal_page_name,
        internal_page = PagesInternal.objects.create(
            name = internal_page_name,
            plugin = plugin, # The associated plugin
            markup = markup,

            content_html = html,
            content_js = js,
            content_css = css,
            description = internal_page_info['description'],
        )
        print "OK"

def install_base_modules():
    """
    Install all modules/plugin how are markt as important or essential.
    """
    Plugin.objects.all().delete()    # delete all installed Plugins

    module_dict = get_all_modules()
    for module_path in module_dict:
        print "---", module_path
        package_name = module_path.replace("/", ".")
        for module_name in module_dict[module_path]:
            print "\n\ninstall module: *** %s ***\n" % module_name
            try:
                module_config = get_module_config(
                    package_name, module_name,
                    dissolve_version_string=True, print_debug=True
                )
            except ImportError, e:
                print "ImportError:", e
                continue

            must_install = (
                getattr(module_config, "__important_buildin__", False) or
                getattr(module_config, "__essential_buildin__", False)
            )
            if not must_install:
                print "module is not important or essential, skip."
                continue

            plugin = install_module(
                package_name, module_name, module_config, active=True
            )
            install_internalpage(
                plugin, package_name, module_name, module_config
            )
            print "OK, module/plugin installed."

if __name__ == "__main__":
    os.chdir("../..") # go into root dir
    install_base_modules()

