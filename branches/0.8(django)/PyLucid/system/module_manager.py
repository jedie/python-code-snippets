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


import sys, traceback

#~ from PyLucid.system.exceptions import PyLucidException


#~ debug = False
debug = True


from PyLucid.models import Plugin, Plugindata


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
    
    try:
        plugin = Plugin.objects.get(module_name=module_name)
    except Plugin.DoesNotExist:
        msg = "[Error Plugin %s not exists!]" % module_name
        return msg
        request.page_msg(msg)
        return

    plugin_data = Plugindata.objects.get(
        plugin_id=plugin.id, method_name=method_name
    )
    module_class=get_module_class(plugin.package_name, module_name)
    class_instance = module_class(request, response)
    unbound_method = getattr(class_instance, method_name)
    
    output = unbound_method(*args)
    return output


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
        return "[%s]" % msg


def handleTag(module_name, request, response):
    """
    handle a lucidTag
    """
    output = run(request, response, module_name, method_name = "lucidTag")
    return output

def handleFunction(function, function_info):
    """
    handle a lucidFunction
    """
    output = run(request, response, module_name, method_name, function_info)
    return output

def handle_command(request, response, module_name, method_name, url_info):
    """
    handle a _command url request
    """
    output = run(request, response, module_name, method_name, url_info)
    return output