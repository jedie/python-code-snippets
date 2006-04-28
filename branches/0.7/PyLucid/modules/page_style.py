#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""

"""

__version__="0.1.0"

__history__="""
v0.1.0
    -  erste Version
"""

import sys

class page_style:
    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        # shorthands
        self.db             = request.db
        self.URLs           = request.URLs
        self.preferences    = request.preferences
        self.session        = request.session

    def lucidTag(self):
        self.embed(self.session["page_id"])
        #self.response.write(
        #    '<link rel="stylesheet" type="text/css" \
        #    href="%s/page_style/print_current_style" />' % (
        #        self.preferences["commandURLprefix"]
        #    )
        #)

    def print_current_style(self):
        """
        Dies ist nur eine pseudo-Methode, denn die CSS anfrage wird direkt in der
        index.py mit check_CSS_request() beantwortet!
        """
        #self.response.write("Style!")
        self.embed(self.session["page_id"])

    def embed(self, page_id):
        self.response.write('<style type="text/css">')
        self.response.write(self.db.side_style_by_id(page_id))
        self.response.write('</style>')




