#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfache Suche in CMS Seiten

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


from django import newforms as forms

from PyLucid.system.BaseModule import PyLucidBaseModule

class SearchForm(forms.Form):
    # TODO: min und max should be saved in the prefereces.
    search_string = forms.CharField(min_length = 3, max_length = 50)

class search(PyLucidBaseModule):

    def lucidTag(self):
        if self.request.method == 'POST':
            search_form = SearchForm(self.request.POST)
            if search_form.is_valid():
                self.page_msg("OK")
        else:
            search_form = SearchForm()

        context = {
            "search_form" : search_form,
        }
        self._render_template("input_form", context)

#    def do_search(self):
#        start_time = time.time()
#        search_string