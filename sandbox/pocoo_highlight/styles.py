# -*- coding: utf-8 -*-
"""
    pocoo.pkg.highlight.styles
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Builtin highlighting styles.

    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

#~ from pocoo.pkg.highlight.base import HighlightingStyle, \
from base import HighlightingStyle, \
     Keyword, Name, Comment, String, Error


class SimpleHighlightingStyle(HighlightingStyle):
    name = "simple"

    def get_style_for(self, ttype):
        if ttype == Comment:
            return "color: #008800"
        elif ttype == Keyword:
            return "color: #AA22FF; font-weight: bold"
        elif ttype == Name.Builtin:
            return "color: #AA22FF"
        elif ttype == String:
            return "color: #bb4444"
        elif ttype == Error:
            return "border: 1px solid red"
        return None
