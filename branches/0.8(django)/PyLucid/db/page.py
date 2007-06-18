#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
    PyLucid.db.page
    ~~~~~~~~~~~~~~~

    some needfull function around the cms pages


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL, see LICENSE for more details
"""

#TODO: We need a caching for:
#      page-ID  <-> parant-ID relation?
#      url data for every page?

from PyLucid.models import User, Page
from PyLucid.tools.tree_generator import TreeGenerator

def get_link_by_id(page_id):
    """
    Create the absolute page link for the given ID
    TODO: This must be chached!
    """
    data = []

    while page_id != 0:
        page = Page.objects.get(id=page_id)
        data.append(page.shortcut)
        try:
            parent_page = page.parent
        except Page.DoesNotExist:
            # The parent id is 0 and there is no page with id 0
            break
        if parent_page == None:
            # No parent_page -> a root page
            break
        page_id = parent_page.id

    data.reverse()
    data.append("") # For add slash!

    link = "/".join(data)
    return link

def get_absolute_link_by_id(context, page_id):
    """
    return the absolute URL to the given page ID.
    """
    URLs = context["URLs"]
    index = URLs["absoluteIndex"] # Has end-slash!
    url = get_link_by_id(page_id)
    return "".join((index, url))

def get_update_info(context, count=10):
    """
    get the last >count< page updates.
    Used by page_update_list and the RSSfeedGenerator
    """
    request = context["request"]

    data = Page.objects.values(
        "id", "name", "title", "lastupdatetime", "lastupdateby"
    ).order_by('-lastupdatetime')

    data = data.filter(showlinks = True)

    if request.user.is_anonymous():
        data = data.exclude(permitViewPublic = False)

    data = data[:count]

    userlist = list(set([item["lastupdateby"] for item in data]))
    userlist = User.objects.in_bulk(userlist)

    for item in data:
        item["link"] = get_absolute_link_by_id(context, item["id"])

        pageName = item["name"]
        pageTitle = item["title"]
        if pageTitle in (None, "", pageName):
            # Eine Seite muß nicht zwingent ein Title haben
            # oder title == name :(
            item["name_title"] = pageName
        else:
            item["name_title"] = "%s - %s" % (pageName, pageTitle)

        item["date"] = item["lastupdatetime"].strftime(_("%Y-%m-%d - %H:%M"))

        item["user"] = userlist.get("lastupdateby", "[%s]" % _("unknown"))

    return data


def flat_tree_list():
    """
    Generate a flat page list.
    Usefull for a html select input, like this:
        <option value="1">___| about</option>
        <option value="2">______| features</option>
        <option value="3">_________| unicode</option>
        <option value="4">_________| unicode test</option>
        <option value="5">______| news</option>
        <option value="6">_________| SVN news</option>
    """
    page_data = Page.objects.values(
        "id", "parent", "name", "title", "shortcut"
    ).order_by("position")
    tree = TreeGenerator(page_data)
    tree.activate_all()
    page_list = tree.get_flat_list()

    for page in page_list:
        page["level_name"] = " %s| %s" % (
            "_"*((page["level"]*2)-2),
            page["name"]
        )

    return page_list

def get_sitemap_tree():
    """
    Generate a tree of all pages.
    """
    sitemap_data = Page.objects.values(
        "id", "parent", "name", "title", "shortcut"
    ).order_by("position")
    #self.page_msg(values)
    tree = TreeGenerator(sitemap_data)
    sitemap_tree = tree.get_sitemap_tree()
    return sitemap_tree

