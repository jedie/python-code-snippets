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
from PyLucid.models import Plugin


def get_module_class(package_name, module_name):
    """
    import the module/plugin and returns the class object
    """
    module = __import__(
        "%s.%s" % (package_name, module_name), {}, {}, [module_name]
    )
    module_class = getattr(module, module_name)
    return module_class

def _run(request, response, module_name, method_name, args=()):
    """
    get the module and call the method
    """
    if isinstance(args, basestring):
        args = (args,)
    
    local_response = LocalModuleResponse()
    
    try:
        plugin = Plugin.objects.get(module_name=module_name)
    except Plugin.DoesNotExist:
        msg = "[Error Plugin %s not exists!]" % module_name
        request.page_msg(msg)
        local_response.write(msg)
        return local_response

    plugin_data = Plugindata.objects.get(
        plugin_id=plugin.id, method_name=method_name
    )
    
    if plugin_data.must_login == True:
        # User must be login to use this method
        # http://www.djangoproject.com/documentation/authentication/
        
        request.must_login = True # For static_tags an the robot tag
        
        if request.user.username == "":
            # User is not logged in
            if plugin_data.no_rights_error == True:
                return local_response
            else:
                raise AccessDeny
    
    module_class=get_module_class(plugin.package_name, module_name)
    class_instance = module_class(request, local_response)
    unbound_method = getattr(class_instance, method_name)
    
    output = unbound_method(*args)
    if output == None:
        return local_response
    elif isinstance(output, HttpResponse):
        return output
    else:
        msg = (
            "Error: A Plugin sould return None or a HttpResponse object!"
            " But %s.%s has returned: %s (%s)"
        ) % (
            module_name, method_name,
            cgi.escape(repr(output)), cgi.escape(str(type(output)))
        )
        AssertionError(msg)
    
    


def run(request, response, module_name, method_name, args=()):
    """
    run the plugin with errorhandling
    """
    try:
        return _run(request, response, module_name, method_name, args)
    except Exception:
        msg = "Run Module %s.%s Error" % (module_name, method_name)
        request.page_msg.red("%s:" % msg)
        etype, value, tb = sys.exc_info()
        tb = tb.tb_next
        tb_lines = traceback.format_exception(etype, value, tb)
        request.page_msg("-"*50, "<pre>")
        request.page_msg.data += tb_lines
        request.page_msg("</pre>", "-"*50)
        return msg + "(Look in the page_msg)"


def handleTag(module_name, request, response):
    """
    handle a lucidTag
    """
    output = run(request, response, module_name, method_name = "lucidTag")
    return output

def handle_command(request, response, module_name, method_name, url_info):
    """
    handle a _command url request
    """
    output = run(request, response, module_name, method_name, url_info)
    return output

#_____________________________________________________________________________
# some routines aound modules/plugins

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

def get_module_config(package_name, module_name):
    """
    imports the plugin and the config module and returns a merge config-object
    """
    config_name = "%s_cfg" % module_name  
    
    def _import(name, from_name):
        print "from %s import %s" % (name, from_name)
        try:
            return __import__(name, {}, {}, [from_name])
        except ImportError, e:
            raise ImportError, "Can't import %s from %s: %s" % (
                from_name, name, e
            )
    
    plugin_module = _import(
        name = ".".join([package_name, module_name, module_name]),
        from_name = module_name
    )
    config_module = _import(
        name = ".".join([package_name, module_name, config_name]),
        from_name = config_name
    )
    module_version = getattr(plugin_module, "__version__", None)
    if module_version:
        module_version = module_version.strip("$ ") # SVN Revision
    config_module.__version__ = module_version
    
    return config_module

def install_module(package_name, module_name, module_config, active=False):  
    print package_name, module_name
    m = Plugin.objects.create(
        package_name = package_name,
        module_name = module_name,
        version = module_config.__version__,
        author = module_config.__author__,
        url = module_config.__url__,
        description = module_config.__description__,
        long_description = module_config.__long_description__,
        active = active,
    )
    print "ID:", m.id
#    print "save...",
#    m.save()
#    print "OK"
    
def install_base_modules():
    Plugin.objects.all().delete()    # delete all installed Plugins
    
    module_dict = get_all_modules()
    for module_path in module_dict:
        print "---", module_path
        package_name = module_path.replace("/", ".")
        for module_name in module_dict[module_path]:
            print module_name,
            try:
                module_config = get_module_config(package_name, module_name)
            except ImportError, e:
                print "ImportError:", e
                continue
            
            print
            print getattr(module_config, "__important_buildin__", False)
            print getattr(module_config, "__essential_buildin__", False)
            must_install = (
                getattr(module_config, "__important_buildin__", False) or
                getattr(module_config, "__essential_buildin__", False)
            )
            if not must_install:
                print "module is not important or essential, skip."
                continue
            
            install_module(
                package_name, module_name, module_config, active=True
            )

if __name__ == "__main__":
    os.chdir("../..") # go into root dir
    install_base_modules()

