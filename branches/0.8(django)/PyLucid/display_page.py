
"""
Display a PyLucid CMS Page
"""

import os, cgi

#~ from django.http import HttpResponse
from PyLucid.system.response import PyLucidResponse


from PyLucid.models import Page
from PyLucid.system.page_msg import PageMsgBuffer
from PyLucid.system.template import get_template_content
from PyLucid.system.detect_page import get_current_page_obj

from django.contrib.sites.models import Site

def display_page(request, url):
    request.page_msg = PageMsgBuffer(request, handle_stdout=True)
    response = PyLucidResponse(request)

    current_page = get_current_page_obj(request, url)
    page = current_page.content

    template = get_template_content(response, current_page)

    page = template.replace("<lucidTag:page_body/>", page)

    page = request.page_msg.put_into_page(page)

    response.write(page)

    return response