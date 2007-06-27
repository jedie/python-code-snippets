#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid.index
    ~~~~~~~~~~~~~

    - Display a PyLucid CMS Page
    - Answer a _command Request

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

#if __name__ == "__main__": # A local test. THIS SHOULD BE COMMENTED!!!
#    import os
#    os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"
#    from PyLucid import settings
#    from django.core import management
#    management.setup_environ(settings) # init django

import datetime, md5

from django.http import HttpResponse
from django.template import RequestContext
from django.core.cache import cache

from PyLucid import models, settings

from PyLucid.system import plugin_manager
from PyLucid.system.response import SimpleStringIO
from PyLucid.system.exceptions import AccessDeny
from PyLucid.system.page_msg import PageMessages
from PyLucid.system.detect_page import get_current_page_obj
from PyLucid.system.URLs import URLs

from PyLucid.tools.content_processors import apply_markup, render_template


def _render_cms_page(context, page_content=None):
    """
    render the cms page.
    - render a normal cms request
    - render a _command request: The page.content is the output from the plugin.
    """
    current_page = context["PAGE"]

    if page_content:
        # The page content comes e.g. from the _command plugin
        current_page.content = page_content
    else:
        # get the current page data from the db
        page_content = current_page.content

        markup_object = current_page.markup
        current_page.content = apply_markup(
            page_content, context, markup_object
        )

    current_page.content = render_template(current_page.content, context)

    template = current_page.template
    template_content = template.content

    html = render_template(template_content, context)

#    import cgi, pprint
#    print context
#    debug = "<hr/><pre>%s</pre></html>" % cgi.escape(pprint.pformat(context))
#    html = html.replace("</html>", debug)

    return HttpResponse(html)


def _get_context(request, current_page_obj):
    """
    Setup the context with PyLucid objects.
    For index() and handle_command() views.
    """
    try:
        context = RequestContext(request)
    except AttributeError, err:
        if str(err) == "'WSGIRequest' object has no attribute 'user'":
            # The auth middleware is not
            msg = (
                "The auth middleware is not activatet in your settings.py"
                " - Did you install PyLucid correctly?"
                " Please look at: %s"
                " - Original Error: %s"
            ) % (settings.INSTALL_HELP_URL, err)
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(msg)
        else:
            # other error
            raise AttributeError(err)

    context["page_msg"] = PageMessages(context)
    context["PAGE"] = current_page_obj
    context["URLs"] = URLs(context)
#    context["URLs"].debug()

    # For additional JavaScript and StyleSheet information.
    # JS+CSS from internal_pages or CSS data for pygments
    context["js_data"] = []
    context["css_data"] = []

    return context


def patch_response_headers(response, cache_timeout, ETag,
                                                                                    last_modified=None):
    """
    Adds some useful headers to the given HttpResponse object:
        ETag, Last-Modified, Expires and Cache-Control

    Original version: django.utils.cache.patch_response_headers()
    """
    now = datetime.datetime.utcnow()
    if not response.has_header('ETag'):
        response['ETag'] = ETag
    if not response.has_header('Last-Modified'):
        if not last_modified:
            last_modified = now
        response['Last-Modified'] = last_modified.strftime(
            '%a, %d %b %Y %H:%M:%S GMT'
        )
    if not response.has_header('Expires'):
        expires = now + datetime.timedelta(0, cache_timeout)
        response['Expires'] = expires.strftime(
            '%a, %d %b %Y %H:%M:%S GMT'
        )


def index(request, url):
    """
    The main index method.
    Return a normal cms page request.
    Every Request will be cached for anonymous user.
    """
    if request.user.is_authenticated():
        # Don't cache for users how are log-in. Otherwise they don't see the
        # admin menu.
        use_cache = False
    else:
        use_cache = True
        # Try to get the cms page request from the cache
        cache_key = ["PyLucid_index_view"]
        if url == "":
            cache_key.append("/")
        else:
            cache_key.append(url)
        cache_key = "_".join(cache_key)
        cache_key = md5.new(cache_key).hexdigest()

        response = cache.get(cache_key)
        if response:
            # This page has been cached in the past, use the cache data:
            return response

    # Get the response for the requested cms page:
    current_page_obj = get_current_page_obj(request, url)
    context = _get_context(request, current_page_obj)
    response = _render_cms_page(context)

    if use_cache:
        # Cache the cms page
        cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        lastupdatetime = current_page_obj.lastupdatetime
        patch_response_headers(
            response, cache_timeout, cache_key, lastupdatetime
        )
        cache.set(cache_key, response, cache_timeout)
    return response


def handle_command(request, page_id, module_name, method_name, url_args):
    """
    handle a _command request
    """
    current_page_obj = models.Page.objects.get(id=int(page_id))
    context = _get_context(request, current_page_obj)

    local_response = SimpleStringIO()

    if url_args == "":
        url_args = ()
    else:
        url_args = (url_args,)

    try:
        output = plugin_manager.handle_command(
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

    return _render_cms_page(context, page_content)


