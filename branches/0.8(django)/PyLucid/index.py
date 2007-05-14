
"""
Display a PyLucid CMS Page
"""

from StringIO import StringIO

from django.http import Http404
from django.http import HttpResponse

from PyLucid.system.response import PyLucidResponse

from PyLucid import settings
from PyLucid.system.exceptions import *
from PyLucid.system.page_msg import PageMsgBuffer
from PyLucid.system.template import get_template_content
from PyLucid.system.detect_page import get_current_page_obj
from PyLucid.system.static_tags import StaticTags
from PyLucid.system import module_manager
from PyLucid.system.URLs import URLs
from PyLucid.system.tinyTextile import TinyTextileParser
from PyLucid.system.LocalModuleResponse import LocalModuleResponse

from PyLucid.models import Page, Template, Markup

#from django.contrib.sites.models import Site

def render_cms_page(request, response, page_content=None):
    request.static_tags = StaticTags(request)

    if not page_content:
        # get the current page data from the db
        page_content = request.current_page.content
        markup = request.current_page.markup
        markup = markup.name
        if markup == "textile":
            out_obj = StringIO()
            p = TinyTextileParser(out_obj, request, response)
            p.parse(page_content)
            page_content = out_obj.getvalue()

    request.static_tags["page_body"] = page_content

    template = request.current_page.template
    template_content = template.content

    response.write(template_content)

    return response

def index(request, url):
    """
    The main index method. Display a requested CMS Page.
    """
    request.page_msg = PageMsgBuffer(request)
    response = PyLucidResponse(request)

    request.current_page = get_current_page_obj(request, url)
    request.current_page_id = request.current_page.id

    request.URLs = URLs(request)
    request.URLs.debug()

    return render_cms_page(request, response)


def handle_command(request, page_id, module_name, method_name, url_info):
    """
    hanlde a _command request
    """
    request.page_msg = PageMsgBuffer(request)
    response = PyLucidResponse(request)

    # ToDo: Should i check here, if the page_id exists?!?
    request.current_page_id = int(page_id)

    request.URLs = URLs(request)

    if url_info=="":
        url_info = ()

    try:
        output = module_manager.handle_command(
            request, response, module_name, method_name, url_info
        )
    except AccessDeny:
        page_content = "[Permission Deny!]"
    else:
        if isinstance(output, HttpResponse):
            return output

        # It's a LocalModuleResponse object
        try:
            page_content = output.get()
        except AttributeError, e:
            page_content = "[Error: %s - output: %s]" % (e, repr(output))

    request.current_page = Page.objects.get(id=page_id)

    return render_cms_page(request, response, page_content)


