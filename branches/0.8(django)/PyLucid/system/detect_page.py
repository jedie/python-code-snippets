#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

#~ debug = True
debug = False

from PyLucid.models import Page

def get_current_page_obj(request, url_info):
    #~ response.write("<p>url: [%s]</p>" % repr(url_info))

    # /bsp/und%2Foder/ -> bsp/und%2Foder
    page_name = url_info.strip("/")

    if page_name == "":
        # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
        set_default_page()
        return

    # bsp/und%2Foder -> ['bsp', 'und%2Foder']
    shortcuts = page_name.split("/")
    #~ response.write("<p>shortcuts: %s</p>" % shortcuts)
    shortcuts.reverse()
    wrong_shutcuts = []
    for shortcut in shortcuts:
        #~ print shortcut
        try:
            page = Page.objects.get(shortcut__exact=shortcut)
        except Page.DoesNotExist:
            msg = "Page '%s' doesn't exists." % shortcut
            #~ request.user.message_set.create(message=msg)
            request.page_msg(msg)
        else:
            return page

    raise Http404