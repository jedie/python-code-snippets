#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles, get_style_by_name

def lexer_list(request, response):
    """
    Liste alle vorhandener pygments Lexer erstellen
    """
    lexers = []
    no = 0
    for longname, aliases, patterns, mimetypes in get_all_lexers():
        no += 1
        lexers.append({
            "no"        : no,
            "longname"  : longname,
            "aliases"   : aliases,
            "patterns"  : patterns,
            "mimetypes" : mimetypes,
        })
    context = {
        "lexers": lexers,
        "menu_link": request.URLs.actionLink("menu"),
    }
    #~ response.page_msg(context)
    request.templates.write("pygments_lexer_list", context, debug=False)

#_____________________________________________________________________________

def style_info(request, response, function_info):
    """
    Listet alle Stylesheet-Namen auf und zwigt die jeweiligen Styles an.
    """
    style_list = list(get_all_styles())

    selected_style = None
    if function_info!=None:
        selected_style = function_info[0]
        if not selected_style in style_list:
            self.page_msg.red("Name Error!")
            selected_style = None

    context = {
        "styles": style_list,
        "selected_style": selected_style,
        "menu_link": request.URLs.actionLink("menu"),
    }
    request.templates.write("pygments_css", context, debug=False)

    if selected_style == None:
        # Es wurde kein Style ausgewählt
        return

    # CSS zum Style anzeigen
    stylesheet = HtmlFormatter(style=selected_style)
    stylesheet = stylesheet.get_style_defs('.pygments_code')

    request.render.highlight(
        ".css", stylesheet, pygments_style=selected_style
    )













