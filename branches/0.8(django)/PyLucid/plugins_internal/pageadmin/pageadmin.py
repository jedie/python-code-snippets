#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Alles was mit dem ändern von Inhalten zu tun hat:
    -edit_page

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

__version__= "$Rev$"


# Python-Basis Module einbinden
#import sys, cgi, time, pickle, urllib, datetime



from django import newforms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect

from PyLucid.models import Page
from PyLucid.db.page import flat_tree_list
from PyLucid.system.BaseModule import PyLucidBaseModule


class SelectEditPageForm(forms.Form):
    page_id = forms.IntegerField()


class pageadmin(PyLucidBaseModule):

    def edit_page(self, page_instance=None, edit_page_id=None):
        """
        edit a existing page
        """
        if page_instance:
            # Edit a new page
            edit_page_id  = self.current_page.id
        elif edit_page_id == None:
            # Edit the current cms page
            edit_page_id  = self.current_page.id
            page_instance = self.current_page
        else:
            # Edit the page with the given ID. ("select page to edit" function)
            try:
                edit_page_id = int(edit_page_id.strip("/"))
                page_instance = Page.objects.get(id__exact=edit_page_id)
            except Exception, e:
                self.page_msg("Wrong page ID! (%s)" % e)
                return

        PageForm = forms.models.form_for_instance(
            page_instance, fields=(
                "content", "parent",
                "name", "shortcut", "title",
                "keywords", "description",
            ),
        )

        if self.request.method == 'POST':
            html_form = PageForm(self.request.POST)
            if html_form.is_valid():
                # save the new page data
                html_form.save()
                self.current_page = html_form
                self.page_msg("page updated.")
                return
        else:
            html_form = PageForm()

        edit_page_form = html_form.as_p()

        # FIXME: Quick hack 'escape' Template String.
        # So they are invisible to the django template engine;)
        edit_page_form = edit_page_form.replace("{", "&#x7B;")\
                                                        .replace("}", "&#x7D;")

        url_django_edit = self.URLs.adminLink(
            "PyLucid/page/%s/" % edit_page_id
        )
        url_textile_help = self.URLs.commandLink(
            "pageadmin", "tinyTextile_help"
        )

        context = {
            "edit_page_form" : edit_page_form,
            "url_django_edit": url_django_edit,
            "url_abort": "#",
            "url_textile_help": url_textile_help,
            "url_taglist": "#",
        }
        self._render_template("edit_page", context)

    def select_edit_page(self):
        """
        A html select box for editing a cms page.
        If the form was sended, return a redirect to the edit_page method.
        """
        if self.request.method == 'POST':
            form = SelectEditPageForm(self.request.POST)
            if form.is_valid():
                form_data = form.cleaned_data
                page_id = form_data["page_id"]
                new_url = self.URLs.commandLink(
                    "pageadmin", "edit_page", page_id
                )
#                self.page_msg(new_url)
                return HttpResponseRedirect(new_url)

        page_list = flat_tree_list()

        context = {
            "page_list": page_list,
        }
        self._render_template("select_edit_page", context)

    #___________________________________________________________________________

    def new_page(self):
        """
        make a new CMS page.
        """
        parent = self.current_page
        # make a new page object:
        new_page = Page(
            name             = "New Page",
            shortcut         = "NewPage",
            template         = parent.template,
            style            = parent.style,
            markup           = parent.markup,
            createby         = self.request.user,
            lastupdateby     = self.request.user,
            showlinks        = parent.showlinks,
            permitViewPublic = parent.permitViewPublic,
            permitViewGroup  = parent.permitViewGroup,
            permitEditGroup  = parent.permitEditGroup,
            parent           = parent,
        )
        # display the normal edit page dialog for the new cms page:
        self.edit_page(page_instance=new_page)

    #___________________________________________________________________________

    def tinyTextile_help(self):
        """
        Render the tinyTextile Help page.
        """
        html = self._get_rendered_template("tinyTextile_help", context={})
        return HttpResponse(html)




