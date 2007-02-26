
"""
Display a PyLucid CMS Page
"""

#~ from django.http import HttpResponse
from PyLucid.system.response import PyLucidResponse

#from PyLucid.models import Page
from PyLucid.system.page_msg import PageMsgBuffer
from PyLucid.system.template import get_template_content
from PyLucid.system.detect_page import get_current_page_obj

#from django.contrib.sites.models import Site

def index(request, url):
    """
    The main index method. Display a requested CMS Page.
    """
    request.page_msg = PageMsgBuffer(request, handle_stdout=True)
    response = PyLucidResponse(request)

    request.current_page = get_current_page_obj(request, url)
    request.page_msg("Page ID:", request.current_page.id)

    page = request.current_page.content

    template = get_template_content(response, request.current_page)

    page = template.replace("<lucidTag:page_body/>", page)
    response.write(page)

    page_msg = request.page_msg.get_page_msg()
    response.replace_tag("page_msg", page_msg)

    return response