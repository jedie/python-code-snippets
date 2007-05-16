#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Display a PyLucid CMS Page
"""

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

#if __name__ == "__main__": # A local test. THIS SHOULD BE COMMENTED!!!
#    import os
#    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
#    from PyLucid import settings
#    from django.core import management
#    management.setup_environ(settings) # init django


from django.http import Http404, HttpResponse
from django.template import Template, RequestContext

from PyLucid import models, settings

from PyLucid.system import module_manager
from PyLucid.system.exceptions import *
from PyLucid.system.page_msg import PageMessages
from PyLucid.system.template import get_template_content
from PyLucid.system.detect_page import get_current_page_obj
from PyLucid.system.URLs import URLs
from PyLucid.system.LocalModuleResponse import LocalModuleResponse

from PyLucid.tools.content_processors import apply_markup, render_template

#from django.contrib.sites.models import Site

def render_cms_page(context, page_content=None):
    current_page = context["PAGE"]

    if page_content:
        # The page content comes e.g. from the _command module/plugin
        current_page.content = page_content
    else:
        # get the current page data from the db
        page_content = current_page.content

        markup_object = current_page.markup
        current_page.content = apply_markup(page_content, markup_object)

    current_page.content = render_template(current_page.content, context)

    template = current_page.template
    template_content = template.content

    t = Template(template_content)
    html = t.render(context)

#    import cgi, pprint
#    print context
#    debug = "<hr/><pre>%s</pre></html>" % cgi.escape(pprint.pformat(context))
#    html = html.replace("</html>", debug)

    return HttpResponse(html)

def index(request, url):
    """
    The main index method. Display a requested CMS Page.
    """
    context = RequestContext(request)
    context["page_msg"] = PageMessages(context)
    context["PAGE"] = get_current_page_obj(request, url)
    context["URLs"] = URLs(context)
#    context["URLs"].debug()

    return render_cms_page(context)


def handle_command(request, page_id, module_name, method_name, url_args):
    """
    hanlde a _command request
    """
    context = RequestContext(request)
    context["page_msg"] = PageMessages(context)

    # TODO: Should i check here, if the page_id exists?!?
    context["PAGE"] = models.Page.objects.get(id=int(page_id))

    context["URLs"] = URLs(context)
#    context["URLs"].debug()

    local_response = StringIO.StringIO()

    if url_args == "":
        url_args = ()
    else:
        url_args = (url_args,)

    try:
        output = module_manager.handle_command(
            context, local_response, module_name, method_name, url_args
        )
    except AccessDeny:
        page_content = "[Permission Deny!]"
    else:
        if output == None:
            # Plugin/Module has retuned the locale StringIO response object
            page_content = local_response.getvalue()
        elif isinstance(output, basestring):
            page_content = output
        elif isinstance(output, HttpResponse):
            # e.g. send a file directly back to the client
            return output
        else:
            import cgi
            msg = (
                "Error: Wrong output from Plugin!"
                " - It should be write into the response object"
                " or return a String/HttpResponse object!"
                " - But %s.%s has returned: %s (%s)"
            ) % (
                module_name, method_name,
                cgi.escape(repr(output)), cgi.escape(str(type(output)))
            )
            raise AssertionError(msg)

#    print module_name, method_name
#    print page_content
#    print "---"

    return render_cms_page(context, page_content)


