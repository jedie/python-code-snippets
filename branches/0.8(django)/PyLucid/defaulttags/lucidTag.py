
"""
    {% lucidTag ... %}
    ~~~~~~~~~~~~~~~~~~

    the special PyLucid tag who starts a plugin with the plugin manager.
    e.g.: {% lucidTag plugin_name.method_name key1="value1" key2="value2" %}

    registered in: ./PyLucid/defaulttags/__init__.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

import cgi

from PyLucid.system.plugin_manager import run
from PyLucid.system.response import SimpleStringIO

from django.conf import settings
from django import template


class lucidTagNodeError(template.Node):
    """
    display a error messages in the cms page for a wrong lucidTag.
    """
    def __init__(self, plugin_name, method_name, msg):
        self.plugin_name = plugin_name
        self.method_name = method_name
        self.msg = msg

    def render(self, context):
        txt = "[lucidTag %s.%s syntax error: %s]" % (
            self.plugin_name, self.method_name, self.msg
        )
        return txt


class lucidTagNode(template.Node):
    def __init__(self, plugin_name, method_name, method_kwargs):
        self.plugin_name = plugin_name
        self.method_name = method_name
        self.method_kwargs = method_kwargs

    def __repr__(self):
        return "<lucidTag node ('%s.%s' kwargs:%s)>" % (
            self.plugin_name, self.method_name, self.method_kwargs
        )

    def render(self, context):
#        print "lucidTag.render():", self.plugin_name, self.method_name

        local_response = SimpleStringIO()
        output = run(
            context, local_response,
            self.plugin_name, self.method_name,
            method_kwargs = self.method_kwargs
        )
        if output == None:
            content = local_response.getvalue()
        elif isinstance(output, basestring):
            content = output
        else:
            msg = (
                "Error: Wrong output from inline Plugin!"
                " - It should be write into the response object and return None"
                " or return a basestring!"
                " - But %s.%s has returned: %s (%s)"
            ) % (
                self.plugin_name, self.method_name,
                repr(output), type(output)
            )
            raise AssertionError(msg)

#        print content
#        print "---"

        return content


def lucidTag(parser, token):
    """
    Parse the lucidTags.

    syntax e.g.:
        {% lucidTag PluginName %}
        {% lucidTag PluginName kwarg1="value1" %}
        {% lucidTag PluginName kwarg1="value1" kwarg2="value2" %}
    """
#    print token.contents

    # split content:
    # e.g.: {% lucidTag PluginName kwarg1="value1" kwarg2="value2" %}
    # plugin_name = "PluginName"
    # kwargs = ['par1="value1"', 'par2="value2"']
    kwargs = token.contents.split()[1:]
    plugin_name = kwargs.pop(0)

    if "." in plugin_name:
        plugin_name, method_name = plugin_name.split(".")
    else:
        method_name = "lucidTag"

    # convert the kwargs list into a dict
    # in..: ['par1="value1"', 'par2="value2"']
    # out.: {'par1': 'value1', 'par2': 'value2'}
    method_kwargs = {}
    for no, arg in enumerate(kwargs):
        try:
            key, value = arg.split("=", 1)
            key = key.encode(settings.DEFAULT_CHARSET)
        except Exception, e:
            return lucidTagNodeError(
                plugin_name, method_name,
                "The key word argument %s is not in the right format. (%s)" % (
                    cgi.escape(repr(arg)), e
                )
            )
        value = value.strip('"')
        method_kwargs[key] = value

    return lucidTagNode(plugin_name, method_name, method_kwargs)

