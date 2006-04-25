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
    def __init__(self, request):
        # shorthands
        self.request    = request
        self.db         = request.db
        self.URLs       = request.URLs

    def lucidTag(self):
        #~ self.request.write(
        print '<link rel="stylesheet" type="text/css" href="static_serve_handler.py" />'
        #~ )
        #~ self.request.write(
            #~ '<link rel="stylesheet" type="text/css" href="%s%s" />' % (self.URLs["action"], "print_current_style")
        #~ )

    def print_current_style(self):
        """
        Dies ist nur eine pseudo-Methode, denn die CSS anfrage wird direkt in der
        index.py mit check_CSS_request() beantwortet!
        """
        self.page_msg("print_current_style() ERROR!!!")

    def embed(self, page_id):
        print '<style type="text/css">'
        print self.db.side_style_by_id(page_id)
        print '</style>'
