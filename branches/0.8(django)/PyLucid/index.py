
"""
Display a PyLucid CMS Page
"""

from django.http import Http404
from django.http import HttpResponse

from PyLucid.system.response import PyLucidResponse

from PyLucid import settings
from PyLucid.system.page_msg import PageMsgBuffer
from PyLucid.system.template import get_template_content
from PyLucid.system.detect_page import get_current_page_obj
from PyLucid.system.static_tags import StaticTags
from PyLucid.system import module_manager

#from django.contrib.sites.models import Site

def index(request, url):
    """
    The main index method. Display a requested CMS Page.
    """
    request.page_msg = PageMsgBuffer(request)
    response = PyLucidResponse(request)

    request.current_page = get_current_page_obj(request, url)
    request.page_msg("Page ID:", request.current_page.id)
    
    request.static_tags = StaticTags(request)

    page = request.current_page.content

    template = get_template_content(response, request.current_page)

    page = template.replace("<lucidTag:page_body/>", page)
    response.write(page)

    page_msg = request.page_msg.get_page_msg()
    response.replace_tag("page_msg", page_msg)

    return response

def handle_command(request, page_id, module_name, method_name, url_info):
    """
    hanlde a _command request
    """
    request.page_msg = PageMsgBuffer(request)
    response = PyLucidResponse(request)
    
    response.write("module_name: %s<br/>" % module_name)
    response.write("method_name: %s<br/>" % method_name)
    response.write("url_info: '%s'<br/>" % url_info)
    
    output = module_manager.handle_command(
        request, response, module_name, method_name, url_info
    )
    if isinstance(output, HttpResponse):
        return output

    page_msg = request.page_msg.get_page_msg()
    response.write(page_msg)
    
    return response

