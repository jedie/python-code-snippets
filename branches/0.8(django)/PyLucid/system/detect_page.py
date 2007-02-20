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

from PyLucid.models import Page, Preference

from django.http import Http404

def get_default_page_id():
    """
    returns the default page id
    """
    default_page = Preference.objects.get(varName__exact="defaultPage")
    id = default_page.value
    return id

def get_current_page_obj(request, url_info):
    """
    returns the page object
    use:
     - the shortcut in the requested url
    or:
     - the default page (stored in the Preference table)
    """
    # /bsp/und%2Foder/ -> bsp/und%2Foder
    page_name = url_info.strip("/")

    if page_name == "":
        # Index Seite wurde aufgerufen. Zumindest bei poor-modrewrite
        page_id = get_default_page_id()
        page = Page.objects.get(id__exact=page_id)
        return page

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
            request.page_msg(_("Page '%s' doesn't exists.") % shortcut)
        else:
            return page

    raise Http404