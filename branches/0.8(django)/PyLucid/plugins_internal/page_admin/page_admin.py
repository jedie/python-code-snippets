#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid plugin
    ~~~~~~~~~

    CMS page administration (edit, delete, make a new page etc.)

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:2007-06-18 16:07:16 +0200 (Mo, 18 Jun 2007) $
    $Rev:1070 $
    $Author:JensDiemer $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:1070 $"


import cgi

from django import newforms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect

from PyLucid.models import Page, Plugin
from PyLucid.db.page import flat_tree_list, get_sitemap_tree
from PyLucid.system.BaseModule import PyLucidBaseModule
from PyLucid.system.detect_page import get_default_page_id


class SelectEditPageForm(forms.Form):
    page_id = forms.IntegerField()


class page_admin(PyLucidBaseModule):

    def edit_page(self, edit_page_id=None, page_instance=None):
        """
        edit a existing page
        """
        if page_instance != None:
            # Edit a new page
            edit_page_id  = self.current_page.id
        elif edit_page_id != None:
            # Edit the page with the given ID. ("select page to edit" function)
            try:
                edit_page_id = int(edit_page_id.strip("/"))
                page_instance = Page.objects.get(id=edit_page_id)
            except Exception, e:
                self.page_msg("Wrong page ID! (%s)" % e)
                return
        else:
            # Edit the current cms page
            edit_page_id  = self.current_page.id
            page_instance = self.current_page

        PageForm = forms.models.form_for_instance(
            page_instance, fields=(
                "content", "parent",
                "name", "shortcut", "title",
                "keywords", "description", "markup",
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

        context = {
            "edit_page_form" : edit_page_form,
            "url_django_edit": url_django_edit,
            "url_abort": "#",
            "url_textile_help": self.URLs.methodLink("tinyTextile_help"),
            "url_taglist": self.URLs.methodLink("tag_list"),
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
                    "page_admin", "edit_page", page_id
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

    def _delete_page(self, id):
        """
        Delete one page with the given >id<.
        Error, if...
        ...this is the default page.
        ...this page has sub pages.
        """
        # The default page can't delete:
        default_page_id = get_default_page_id()
        if id == default_page_id:
            msg = _(
                    "Can't delete the page with ID:%s,"
                    " because this is the default page!"
            ) % id
            raise DeletePageError(msg)

        # Check if the page has subpages
        sub_pages_count = Page.objects.filter(parent=id).count()
        if sub_pages_count != 0:
            msg = _(
                    "Can't delete the page with ID:%s,"
                    " because it has %s sub pages!"
            ) % (id, sub_pages_count)
            raise DeletePageError(msg)

        # Delete the page:
        try:
            page = Page.objects.get(id=id)
            page.delete()
        except Exception, msg:
            msg = _("Can't delete the page with ID:%s: %s") % (
                id, cgi.escape(str(msg))
            )
            raise DeletePageError(msg)
        else:
            self.page_msg(_("Page with id: %s delete successful.") % id)


    def _process_delete_pages(self):
        """
        process a sended "delete pages" dialog.
        """
        if self.request.method != 'POST':
            # No form sended via POST
            return

        # create a list of the sended page IDs:
        id_list = self.request.POST.getlist("pages")
        try:
            # Convert the string list to a interger list
            id_list = [int(i) for i in id_list]
        except ValueError, msg:
            self.page_msg.red(_("Wrong data: %s") % cgi.escape(str(msg)))
            return

        # delete the pages, one by one:
        for id in id_list:
            try:
                self._delete_page(id)
            except DeletePageError, msg:
                self.page_msg.red(msg)


    def _get_html(self, sitemap_tree, default_page_id):
        """
        generate from the sitemap_tree a "checkbox-list" for the delete
        page html form dialog.
        The default page and pages with sub pages would get no checkbox.
        """
        result = ["<ul>\n"]
        for entry in sitemap_tree:
            result.append('<li>')

            if entry["id"]==default_page_id:
                html = (
                    '<span title="Can not delete this pages,'
                    ' because it the default page.">%(name)s</span>'
                )
            elif "subitems" in entry:
                html = (
                    '<span title="Can not delete this pages,'
                    ' because it has sub pages.">%(name)s</span>'
                )
            else:
                html = (
                    '<input name="pages" value="%(id)s"'
                    ' id="del_page_%(id)s" type="checkbox"'
                    ' title="delete page: %(name)s" />'
                    ' <label for="del_page_%(id)s">%(name)s</label>'
                )

            result.append(html % entry)
#            result.append(' <small>(id: %s)</small>' % entry["id"])

            if "subitems" in entry:
                result.append(
                    self._get_html(entry["subitems"], default_page_id)
                )

            result.append('</li>\n')

        result.append("</ul>\n")
        return "".join(result)


    def delete_pages(self):
        """
        Render the delete page html form dialog.
        A sended html form would be
        """
        # Process a sended POST formular:
        self._process_delete_pages()

        # Get the needed data for build the html form:
        page_tree = get_sitemap_tree()

        # The default page can't delete, so we need the ID of these page:
        default_page_id = get_default_page_id()

        # Generate the HTML form code:
        html = self._get_html(page_tree, default_page_id)

        # Render the Template:
        context = {
            "html_data": html,
        }
        self._render_template("delete_pages", context)

    #___________________________________________________________________________

    def tinyTextile_help(self):
        """
        Render the tinyTextile Help page.
        """
        html = self._get_rendered_template("tinyTextile_help", context={})
        return HttpResponse(html)

    #___________________________________________________________________________

    def tag_list(self):
        """
        Render a help page with a list of all available django template tags
        and all available lucidTag's (List of all available plugins).

        TODO: Find a way to put the tag parameter syntax into the plugin_list:
            e.g. without..: {{ lucidTag page_update_list }}
            e.g. with.....: {{ lucidTag page_update_list count=10 }}
            idea: Import the plugin class and use inspect?
        """

        def get_plugin_list():
            """
            Generate a list of all Plugins how are active.
            """
            plugin_list = Plugin.objects.values(
                "id", "plugin_name", "version", "author", "url", "description",
                "long_description",
            ).order_by('package_name')
            plugin_list = plugin_list.filter(active = True)
            return plugin_list

        def get_page_fields():
            """
            Generate a list of all PyLucid.models.Page fields.
            """
            page_fields = []
            opts = self.current_page._meta
            for field in opts.fields:
                page_fields.append({
                    "name": field.name,
                    "help_text": field.help_text
                })
            return page_fields

        # TODO: insert the extra context fields
        # e.g. from PyLucid.system.context_processors

        context = {
            "plugin_list": get_plugin_list(),
            "page_fields": get_page_fields(),
        }
        html = self._get_rendered_template("tag_list", context)
        return HttpResponse(html)


class DeletePageError(Exception):
    """
    Error while deleting one cms page.
    """
    pass



