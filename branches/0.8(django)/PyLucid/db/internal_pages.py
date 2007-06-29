#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid internal pages
    ~~~~~~~~~~~~~~~~~~~~~~

    Some shared function around the internal pages access.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate:$
    $Rev:$
    $Author: JensDiemer $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

from PyLucid.models import PagesInternal


def get_internal_page(plugin_name, internal_page_name):
    """
    returned the internal page object.
    """
    internal_page_name = ".".join([plugin_name, internal_page_name])

    # django bug work-a-round
    # http://groups.google.com/group/django-developers/browse_thread/thread/e1ed7f81e54e724a
    internal_page_name = internal_page_name.replace("_", " ")

    try:
        return PagesInternal.objects.get(name = internal_page_name)
    except PagesInternal.DoesNotExist, err:
        msg = "internal page '%s' not found! (%s)" % (internal_page_name, err)
        raise PagesInternal.DoesNotExist(msg)