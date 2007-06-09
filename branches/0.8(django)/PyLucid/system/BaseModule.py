#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Basis Modul von den andere Module erben können

Bsp.:

from PyLucid.system.BaseModule import PyLucidBaseModule

class Bsp(PyLucidBaseModule):
    def __init__(self, *args, **kwargs):
        super(Bsp, self).__init__(*args, **kwargs)



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

import os, pprint, cgi

from django.contrib.sites.models import Site

from PyLucid import settings
from PyLucid.models import PagesInternal
from PyLucid.tools.content_processors import apply_markup, render_template


#______________________________________________________________________________


class PyLucidBaseModule(object):

    def __init__(self, context, response):
        self.context    = context
        self.response   = response

        self.request    = context["request"]
        self.page_msg   = context["page_msg"]
        self.URLs       = context["URLs"]
#        self.URLs.debug()

        self.current_page = self.context["PAGE"]

    def _debug_context(self, context, template):
        import pprint
        self.response.write("<fieldset><legend>template debug:</legend>")
        self.response.write("<legend>context:</legend>")
        self.response.write("<pre>")
        pprint_context = pprint.pformat(context)
        self.response.write(cgi.escape(pprint_context))
        self.response.write("</pre>")
        self.response.write("<legend>template:</legend>")
        self.response.write("<pre>")
        self.response.write(cgi.escape(template))
        self.response.write("</pre></fieldset>")

    def _get_template(self, internal_page_name):
        module_name = self.__class__.__name__ # Get the superior class name

        internal_page_name = ".".join([module_name, internal_page_name])

        try:
            return PagesInternal.objects.get(name = internal_page_name)
        except PagesInternal.DoesNotExist, e:
            msg = "internal page '%s' not found! (%s)" % (internal_page_name, e)
            raise PagesInternal.DoesNotExist(msg)

    def _add_js_css_data(self, internal_page):
        """
        insert the additional JavaScript and StyleSheet data into the global
        context.
        """
        def add(attr_name, key):
            content = getattr(internal_page, attr_name)
            if content == "":
                # Nothig to append ;)
                return

            if not key in self.context:
                self.context[key] = []

            self.context[key].append({
                "from_info": "internal page: '%s'" % internal_page.name,
                "data": content,
            })

        # append the JavaScript data
        add("content_js", "js_data")

        # append the StyleSheet data
        add("content_css", "css_data")


    def _get_rendered_template(self, internal_page_name, context, debug=False):
        """
        return a rendered internal page
        """
        internal_page = self._get_template(internal_page_name)

        content_html = internal_page.content_html

        self._add_js_css_data(internal_page)

        html = self.__render(content_html, context)

        markup_object = internal_page.markup
        html = apply_markup(html, markup_object)

        return html

    def _render_template(self, internal_page_name, context, debug=False):
        """
        render a template and write it into the response object
        """
        html = self._get_rendered_template(internal_page_name, context, debug)
        self.response.write(html)

    def _render_string_template(self, template, context, debug=False):
        """
        Render a string-template with the given context and
        returns the result as a HttpResponse object.
        """
        html = self.__render(template, context)

        self.response.write(html)

    def __render(self, content, context, debug=False):
        """
        render the string with the given context
        -debug the context, if debug is on.
        -prepare the context
        -retunted the rendered page
        """
        if debug:
            self._debug_context(context, content)

        html = render_template(content, self.context, context)
        return html

#        try:
        t = Template(content)
        c = self.__prepare_context(context)
        html = t.render(c)
#        except Exception, e:
#            html = "[Error, render the django Template '%s': %s]" % (
#                internal_page_name, e
#            )
        return html

    def __prepare_context(self, context):
        """
        -transfer some objects from the global context into the local dict
        -returns a django context object
        """
        for key in self.TRANSFER_KEYS:
            context[key] = self.context[key]

        c = Context(context)
        return c