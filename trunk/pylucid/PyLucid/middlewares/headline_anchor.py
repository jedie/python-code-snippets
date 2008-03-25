#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid headline anchor
    ~~~~~~~~~~~~~~~~~~~~~~~

    A middleware to add a human readable, url safe anchor to all html headlines.
    Every anchor is a permalink to the page. So you can easy copy&paste the
    links for several use.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import string, re

from PyLucid.tools.shortcuts import makeUnique

HEADLINE_RE = re.compile(r"<h(\d)>(.+?)</h(\d)>(?iusm)")

HEADLINE = (
    '<h%(no)s id="%(anchor)s">'
    '<a title="Link to this section" href="%(link)s#%(anchor)s" class="anchor">'
    '%(txt)s</a>'
    '</h%(no)s>\n'
)


class HeadlineAnchor(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Add
        """
        # start the view
        response = view_func(request, *view_args, **view_kwargs)

        # Put only the statistic into HTML pages
        if not "html" in response._headers["content-type"][1]:
            # No HTML Page
            return response

        try:
            context = request.CONTEXT
        except AttributeError:
            # No cms page request (e.g. the _install section) -> do nothing
            return response

        # Get the permalink to the current page
        current_page = context["PAGE"]
        self.permalink = current_page.get_permalink()

        # A list of all existing anchors, used in self.add_anchor()
        self.anchor_list = []

        # add the anchor with re.sub
        content = response.content
        new_content = HEADLINE_RE.sub(self.add_anchor, content)
        response.content = new_content

        return response

    def add_anchor(self, matchobj):
        """
        add a unique anchor to a html headline.
        """
        txt = matchobj.group(2)

        # Strip all non-ASCII and make the anchor unique
        anchor = makeUnique(txt, self.anchor_list)

        # Remember the current anchor. So makeUnique can add a number on double
        # anchors.
        self.anchor_list.append(anchor)

        result = HEADLINE % {
            "no": matchobj.group(1),
            "txt": txt,
            "link": self.permalink,
            "anchor": anchor,
        }
        return result
