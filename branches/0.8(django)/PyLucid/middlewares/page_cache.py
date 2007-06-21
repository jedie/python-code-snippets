#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid cms page cache
    ~~~~~~~~~~~~~~~~~~~~~~

    PageCache():
    A modified django CacheMiddleware who only cache the normal cms page view.

    DebugPageCache():
    A hackish debugger: Append information if the response was cached or not.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

from django.middleware.cache import CacheMiddleware

class PageCache(CacheMiddleware):
    """
    change a little bit the operation method of the django CacheMiddleware:
    -Cache only the normal cms page view.
    So the _install and _command view would be not cached.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.func_name != "index":
            # Cache only the normal cms page view
            request._cache_update_cache = False


class DebugPageCache(object):
    """
    Debug for the cache system.
    Append the information in every normal response, if the view was cached or
    not cached.
    """
    def __init__(self):
        self.func_name = None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Save the view function name.
        """
        self.func_name = view_func.func_name

    def process_response(self, request, response):
        """
        Append the "was cached?" info.
        """
        if self.func_name == None:
            # Not a normal response (e.g. Redirect) -> do nothing.
            return response

        if hasattr(request, '_cache_update_cache'):
            cache_update_cache = request._cache_update_cache
        else:
            cache_update_cache = None

        info = "'%s' view " % self.func_name
        if cache_update_cache == True:
            info += "was cached."
        else:
            info += "is not cached."

        content = response.content
        if "html" in response.headers['Content-Type']:
            # Try to insert the info into a html valid way.
            old_content = content
            content = content.replace("</body>", "<h1>%s</h1></body>" % info)
            if content == old_content:
                # replacement not successful
                content += "\n\n" + info
        else:
            # Append only the info on every other request type (e.g. css
            content += "\n\n" + info

        response.content = content

        return response

