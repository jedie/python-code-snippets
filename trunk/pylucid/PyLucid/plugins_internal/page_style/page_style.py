# -*- coding: utf-8 -*-

"""
    PyLucid stylesheets
    ~~~~~~~~~~~~~~~~~~~

    - Put the css html tag into the cms page.
    - Send the current stylesheet directly to the client.

    Note:
    1. The page_style plugin insert the temporary ADD_DATA_TAG *before* the
        global Stylesheet inserted. So the global Stylesheet can override CSS
        properties from every internal page.
        The ADD_DATA_TAG would be replaced with the collected CSS/JS contents
        in PyLucid.index *after* the page rendered with the django template
        engine.
    2. In CGI environment you should use print_current_style() instead of
        lucidTag! Because the lucidTag insert only the link to the stylesheet.
        Every page request causes a stylesheet request, in addition!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


__version__= "$Rev$"


import sys, os, datetime

from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404
from django.conf import settings

from PyLucid.models import Style
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.content_processors import render_string_template

class page_style(PyLucidBasePlugin):

    def lucidTag(self):
        """
        -Put a link to sendStyle into the page.
        -Insert ADD_DATA_TAG *before* the global Stylesheet link
        """
        self.response.write(settings.ADD_DATA_TAG)

        current_page = self.context["PAGE"]
        current_style = current_page.style

        style_filepath = current_style.get_filepath()
        if os.path.isfile(style_filepath):
            # The stylesheet was stored into a static file
            url = current_style.get_absolute_url()
        else:
            # _command fake-file request
#            self.page_msg("file '%s' not found." % style_filepath)

            style_name = current_style.name
            style_filename = "%s.css" % style_name

            url = self.URLs.methodLink("sendStyle")
            url = url + style_filename

        cssTag = '<link rel="stylesheet" type="text/css" href="%s" />\n' % url
        self.response.write(cssTag)


    def print_current_style(self):
        """
        -Write the stylesheet directly into the page.
        -Insert ADD_DATA_TAG *before* the global Stylesheet content.

        Used with the tag: {% lucidTag page_style.print_current_style %}
        """
        self.response.write(settings.ADD_DATA_TAG)

        current_page = self.context["PAGE"]
        stylesheet = current_page.style

        context = {
            "content": stylesheet.content,
        }
        self._render_template("write_styles", context)#, debug=True)


    def sendStyle(self, css_filename=None):
        """
        send the stylesheet as a file to the client.
        It's the request started with the link tag from self.lucidTag() ;)
        TODO: Should insert some Headers for the browser cache.
        """
        if not css_filename:
            raise Http404(_("Wrong stylesheet url!"))

        css_name = css_filename.rsplit(".",1)[0]

        try:
            style = Style.objects.get(name=css_name)
        except Style.DoesNotExist:
            raise Http404(_("Stylesheet '%s' unknown!") % css_filename)

        content = style.content

        response = HttpResponse()
        response['Content-Type'] = 'text/css; charset=utf-8'
        response.write(content)

        return response

from PyLucid.system.internal_page import get_internal_page, InternalPageNotFound
def replace_add_data(context, content):
    """
    Replace the temporary inserted "add data" tag, with all collected CSS/JS
    contents, e.g. from the internal pages.
    Note: The tag added in PyLucid.plugins_internal.page_style
    """
    internal_page_content = get_internal_page(context, "page_style", "add_data")

    context = {
        "js_data": context["js_data"],
        "css_data": context["css_data"],
    }
    html = render_string_template(
        internal_page_content, context, autoescape=False
    )

    content = content.replace(settings.ADD_DATA_TAG, html)
    return content