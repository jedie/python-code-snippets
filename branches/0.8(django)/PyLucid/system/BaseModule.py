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

        self.current_page = self.context["PAGE"]

    def _debug_context(self, context, template):
        import pprint, cgi
        self.response.write("<fieldset><legend>template debug:</legend>")
        self.response.write("<legend>context:</legend>")
        self.response.write("<pre>")
        pprint_context = pprint.pformat(context)
        self.response.write(cgi.escape(pprint_context))
        self.response.write("</pre>")
        self.response.write("<legend>template:</legend>")
        self.response.write("<pre>")
        template = cgi.escape(template)
        # Escape all django template tags
        template = template.replace("{", "&#x7B;").replace("}", "&#x7D;")
        self.response.write(template)
        self.response.write("</pre></fieldset>")


    def _get_template(self, internal_page_name):
        module_name = self.__class__.__name__ # Get the superior class name

        internal_page_name = ".".join([module_name, internal_page_name])

        # django bug work-a-round
        # http://groups.google.com/group/django-developers/browse_thread/thread/e1ed7f81e54e724a
        internal_page_name = internal_page_name.replace("_", " ")

        try:
            return PagesInternal.objects.get(name = internal_page_name)
        except PagesInternal.DoesNotExist, err:
            msg = "internal page '%s' not found! (%s)" % (internal_page_name, err)
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

        html = self.__render(content_html, context, debug)

        markup_object = internal_page.markup
        html = apply_markup(html, self.context, markup_object)

        return html

    def _render_template(self, internal_page_name, context, debug=False):
        """
        render a template and write it into the response object
        """
        html = self._get_rendered_template(internal_page_name, context, debug)
        self.response.write(html)

    def _render_string_template(self, template, context, debug=False):
        """
        Render a string-template with the given context.
        Should be only used for developing. The normal way is: Use a internal
        page for templates.
        """
        html = self.__render(template, context, debug)

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



