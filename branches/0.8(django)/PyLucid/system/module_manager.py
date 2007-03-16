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


import sys, cgi, traceback

#~ from PyLucid.system.exceptions import PyLucidException


#~ debug = False
debug = True

from django.http import HttpResponse

from PyLucid.system.exceptions import *
from PyLucid.system.LocalModuleResponse import LocalModuleResponse
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