#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid page update list plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a list of the latest page updates.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more detailsp

"""

__version__= "$Rev$"

from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.db.page import get_update_info

from django.core.cache import cache
# Same key used by the RSSfeedGenerator Plugin, too!!!
CACHE_KEY = "page_updates_data"

class page_update_list(PyLucidBaseModule):

    def lucidTag(self, count=10):
        try:
            count = int(count)
        except Exception, e:
            msg = "page_update_list error: count must be a integer (%s)" % e
            self.page_msg.red(msg)
            self.response.write("[%s]" % msg)
            return

        self.generate_list(count)

    def generate_list(self, count):
        cache_key = "%s_%s" % (CACHE_KEY, count)
        page_updates = cache.get(cache_key)

        context = {}

        if page_updates != None:
            context["from_cache"] = True
        else:
            page_updates = get_update_info(self.context, 10)
            cache.set(cache_key, page_updates, 120)

        context["page_updates"] = page_updates

        self._render_template("PageUpdateTable", context)













