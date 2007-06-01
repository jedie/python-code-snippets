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

from PyLucid.models import Page
from PyLucid.system.BaseModule import PyLucidBaseModule


class pageadmin(PyLucidBaseModule):

    def edit_page(self):
        """
        edit a existing page
        """
        current_page_id  = self.current_page.id
        edit_link = self.URLs.adminLink("PyLucid/page/%s/" % current_page_id)
        self.response.write('<a href="%s">django panel edit</a>' % edit_link)

        PageForm = forms.models.form_for_instance(
            self.current_page, fields=(
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
                self.page_msg("page updated.")
        else:
            html_form = PageForm()

        html_form = html_form.as_p()

        # FIXME: Quick hack. 'escape' Template String, so they are invisible ;)
        html_form = html_form.replace("{", "&#x7B;").replace("}", "&#x7D;")
        html = (
            '<form method="post">'
            '  <table class="form">'
            '    %s'
            '  </table>'
            '  <input type="submit" value="speichern" />'
            '</form>'
        ) % html_form
        self.response.write(html)


