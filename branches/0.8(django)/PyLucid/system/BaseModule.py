#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Basis Modul von den andere Module erben können

Bsp.:

from PyLucid.system.BaseModule import PyLucidBaseModule

class Bsp(PyLucidBaseModule):
    def __init__(self, *args, **kwargs):
        super(Bsp, self).__init__(*args, **kwargs)



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

import posixpath

from django.contrib.sites.models import Site

from PyLucid.db import DB_Wrapper


class PyLucidBaseModule(object):
    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        self.db = DB_Wrapper(request.page_msg)
        self.page_msg = request.page_msg

    #~ def absolute_link(self, url):
        #~ if isinstance(url, list):
            #~ url = "/".join(url)

        #~ url = posixpath.join(Site.objects.get_current().domain, url)

        #~ return 'http://%s' % url
