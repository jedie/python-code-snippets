#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid stylesheets
    ~~~~~~~~~~~~~~~~~~~

    - Put the css html tag into the cms page.
    - Send the current stylesheet directly to the client.

    Note:
    The page_style.lucidTag() method adds the additional_content ADD_DATA_TAG
    into the page.
    The middleware PyLucid.middlewares.additional_content replace the tag and
    puts the collected CSS/JS contents into the page.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""


__version__= "$Rev$"


import sys, os, datetime

from django.http import HttpResponse

from PyLucid.middlewares.additional_content import ADD_DATA_TAG
from PyLucid.models import Style
from PyLucid.system.BaseModule import PyLucidBaseModule

class page_style(PyLucidBaseModule):

    def lucidTag(self):
        """
        -Put a link to sendStyle into the page.
        -Insert the ADD_DATA_TAG for the additional_content middleware
        """
        self.response.write(ADD_DATA_TAG)

        current_page = self.context["PAGE"]
        style_name = current_page.style.name
        style_filename = "%s.css" % style_name

        url = self.URLs.methodLink(
            "sendStyle", style_filename, addSlash=False
        )
        cssTag = '<link rel="stylesheet" type="text/css" href="%s" />\n' % url
        self.response.write(cssTag)


    def print_current_style(self):
        """
        -Write the stylesheet directly into the page.
        -Insert the ADD_DATA_TAG for the additional_content middleware
        Used with the tag: {% lucidTag page_style.print_current_style %}
        """
        self.response.write(ADD_DATA_TAG)

        current_page = self.context["PAGE"]
        stylesheet = current_page.style

        context = {
            "content": stylesheet.content,
        }
        self._render_template("write_styles", context)#, debug=True)


    def sendStyle(self, css_filename):
        """
        send the stylesheet as a file to the client.
        It's the request started with the link tag from self.lucidTag() ;)
        TODO: Should insert some Headers for the browser cache.
        """
        css_name = css_filename.split(".",1)[0]

        try:
            style = Style.objects.get(name=css_name)
        except Style.DoesNotExist:
            raise Http404("Stylesheet '%s' unknown!" % cgi.escape(css_filename))

        content = style.content

        response = HttpResponse()
        response['Content-Type'] = 'text/css; charset=utf-8'
        response.write(content)

        return response

