#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid additional page content
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Replace some Tags after the cms page is completly created:

    ADD_DATA_TAG
    ~~~~~~~~~~~~
    The Stylesheet and JavaScript data from the internal pages are stored in
    a list: context["js_data"] and context["css_data"]
    The page_style Plugin insert the ADD_DATA_TAG into the response content.
    Here we replace the tag with the collected CSS/JS contents.


    PAGE_STAT_TAG
    ~~~~~~~~~~~~~
    A small page statistic middleware.
    -replace the >PAGE_STAT_TAG< with some stats. But only in HTML pages.

    Based on http://code.djangoproject.com/wiki/PageStatsMiddleware


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

from operator import add
from time import time
from django.db import connection

from PyLucid.db.internal_pages import get_internal_page
from PyLucid.tools.content_processors import render_string_template

start_overall = time()

PAGE_STAT_TAG = "<!-- script_duration -->"
ADD_DATA_TAG = "<!-- additional_data -->"

FMT = (
    'render time: %(total_time).3f -'
    ' overall: %(overall_time).1f -'
    ' Queries: %(queries)d'
)

class AdditionalContentMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        start_time = time()

        # get number of db queries before we do anything
        old_queries = len(connection.queries)

        # start the view
        response = view_func(request, *view_args, **view_kwargs)

        # Put only the statistic into HTML pages
        if not "html" in response.headers['Content-Type']:
            # No HTML Page -> do nothing
            return response

        content = response.content

        content = self._add_data(content, request)
        content = self._page_stat(content, start_time, old_queries)

        response.content = content

        return response


    def _add_data(self, content, request):
        """
        Replace the ADD_DATA_TAG
        add CSS/JS data from the Plugins into the page.
        Note: The ADD_DATA_TAG puts the page_style plugin into the content!
        """
        try:
            context = request.CONTEXT
        except AttributeError:
            # In the _install section, we need no add_data... There is no
            # CONTEXT object in the request object. -> Do nothing
            return content

        try:
            internal_page = get_internal_page("page_style", "add_data")
            internal_page_content = internal_page.content_html

            context = {
                "js_data": context["js_data"],
                "css_data": context["css_data"],
            }
            html = render_string_template(internal_page_content, context)
        except Exception, msg:
            html = "<!-- Replace the ADD_DATA_TAG error: %s -->" % msg

        content = content.replace(ADD_DATA_TAG, html)

        return content


    def _page_stat(self, content, start_time, old_queries):
        """
        Replace the PAGE_STAT_TAG
        """
        # compute the db time for the queries just run
        queries = len(connection.queries) - old_queries

        # replace the comment if found
        stat_info = FMT % {
            'total_time' : time() - start_time,
            'overall_time' : time() - start_overall,
            'queries' : queries,
        }

        content = content.replace(PAGE_STAT_TAG, stat_info)

        return content
