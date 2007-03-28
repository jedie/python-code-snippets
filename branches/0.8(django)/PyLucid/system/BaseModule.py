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

import posixpath, os, pprint, cgi

from django.contrib.sites.models import Site
from django.template import Template, Context

from PyLucid import settings
from PyLucid.db import DB_Wrapper
from PyLucid.models import PagesInternal, TemplateEngine


class URLs(dict):
    def __init__(self, request):
        self.request = request
        self.page_msg = request.page_msg
              
        self.setup_URLs()
        
    def setup_URLs(self):
        """
        Pfad für Links festlegen
        """
        self["cwd"] = os.getcwdu()
        self["host"] = self.request.META['HTTP_HOST']
        self["hostname"] = "%s://%s" % (
            self.request.META.get('wsgi.url_scheme', "http"),
            self["host"],
        )

        self["scriptRoot"] = self.request.META.get("SCRIPT_NAME", "/")
        if self["scriptRoot"] == "": self["scriptRoot"] = "/"

        self["docRoot"] = self.addSlash(posixpath.split(self["scriptRoot"])[0])

        self["absoluteIndex"] = self["hostname"] + self["scriptRoot"]
        
        self["commandBase"] = posixpath.join(
            self["scriptRoot"], settings.COMMAND_URL_PREFIX, str(self.request.current_page_id)
        )

    #__________________________________________________________________________

    def commandLink(self, modulename, methodname="", args="", addSlash=True):
        args = self._prepage_args(args)
        link = posixpath.join(
            self["commandBase"], modulename, methodname, args
        )

        if addSlash:
            link = self.addSlash(link)
        return link

    #__________________________________________________________________________

    def addSlash(self, path):
        """
        >>> addSlash("/noSlash")
        '/noSlash/'
        >>> addSlash("/hasSlash/")
        '/hasSlash/'
        """
        if path=="" or path[-1]!="/":
            return path+"/"
        else:
            return path
            

    def _prepage_args(self, args):
        if isinstance(args, (list, tuple)):
            return "/".join([str(i) for i in args])
        else:
            return str(args)

    #__________________________________________________________________________

    def debug(self):
        self.page_msg("URLs debug:")
        for k,v in self.items():
            self.page_msg(" - %15s: '%s'" % (k,v))


#______________________________________________________________________________


class PyLucidBaseModule(object):
    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        self.db = DB_Wrapper(request.page_msg)
        self.page_msg = request.page_msg
        
        self.URLs = URLs(request)
#        self.URLs.debug()
    
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

    def _get_rendered_template(self, internal_page_name, context, debug=False):
        """
        return a rendered internal page
        """
        internal_page = PagesInternal.objects.get(name = internal_page_name)
        content = internal_page.content_html

        if debug: self._debug_context(context, content)

        engine_id = internal_page.template_engine
        engine_name = TemplateEngine.objects.get(id=engine_id).name
        if engine_name in ("django", "jinja"):
            try:
                t = Template(content)
                c = Context(context)
                html = t.render(c)
            except Exception, e:
                html = "[Error, render the django Template '%s': %s]" % (
                    internal_page_name, e
                )
        elif engine_name == "string formatting":
            html = content % context
        else:
            self.page_msg("Error: Template Engine '%s' unknown." % engine_name)
            html = content
            
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
        if debug: self._debug_context(context, template)
        
        c = Context(context)
        t = Template(template)
        html = t.render(c)
        self.response.write(html)

    #~ def absolute_link(self, url):
        #~ if isinstance(url, list):
            #~ url = "/".join(url)

        #~ url = posixpath.join(Site.objects.get_current().domain, url)

        #~ return 'http://%s' % url
