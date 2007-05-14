#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
some needfull function around the cms pages

TODO: We need a caching for:
    page-ID  <-> parant-ID relation?
    url data for every page?
"""

from PyLucid.models import User, Page

def get_link_by_id(page_id):
    """ Create the absolute page link for the given ID """
    data = []

    while page_id != 0:
        page = Page.objects.get(id=page_id)
        data.append(page.shortcut)
        try:
            parent_page = page.parent
        except Page.DoesNotExist:
            # The parent id is 0 and there is no page with id 0
            break
        page_id = parent_page.id

    data.reverse()
    data.append("") # For add slash!

    link = "/".join(data)
    return link

def get_absolute_link_by_id(request, page_id):
    """
    return the absolute URL to the given page ID.
    """
    index = request.URLs["absoluteIndex"] # Has end-slash!
    url = get_link_by_id(page_id)
    return "".join((index, url))

def get_update_info(request, count=10):
    """
    get the last >count< page updates.
    Used by page_update_list and the RSSfeedGenerator
    """
    page_updates = Page.objects.filter(showlinks__exact=1)
    if request.user.username != "":
        page_updates = page_updates.filter(permitViewPublic__exact=1)

    page_updates = page_updates.order_by('-lastupdatetime')

    page_updates = page_updates.values(
        "id", "name", "title", "lastupdatetime", "lastupdateby"
    )[:count]

    userlist = list(set([item["lastupdateby"] for item in page_updates]))
    userlist = User.objects.in_bulk(userlist)

    for item in page_updates:
        item["link"] = get_absolute_link_by_id(request, item["id"])
#        item["absoluteLink"] = "/%s" % item["link"]#self.URLs.absoluteLink(item["link"])

        pageName = item["name"]
        pageTitle = item["title"]
        if pageTitle in (None, "", pageName):
            # Eine Seite muß nicht zwingent ein Title haben
            # oder title == name :(
            item["name_title"] = pageTitle
        else:
            item["name_title"] = "%s - %s" % (pageName, pageTitle)

        item["date"] = item["lastupdatetime"].strftime(_("%Y-%m-%d - %H:%M"))

        item["user"] = userlist.get("lastupdateby", "[%s]" % _("unknown"))

    return page_updates