
"""
Display a PyLucid CMS Page
"""

import os, cgi

from django.http import HttpResponse
from django.http import Http404

from PyLucid.models import Page
from PyLucid.system.page_msg import put_page_msg, PageMsgBuffer
from PyLucid.system.template import get_template_content
from PyLucid.system.detect_page import get_current_page_obj


def display_page(request, url):

    request.page_msg = PageMsgBuffer(request)
    response = HttpResponse()

    current_page = get_current_page_obj(request, url)
    page = current_page.content

    template = get_template_content(response, current_page)

    page = template.replace("<lucidTag:page_body/>", page)

    page = put_page_msg(request, page)

    response.write(page)

    return response