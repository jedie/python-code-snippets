#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:page_update_list />
oder
<lucidFunction:page_update_list>20</lucidFunction>
Generiert eine Liste der "letzten Änderungen"

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



from django.template import Template, Context
from django.template.loader import get_template

from PyLucid.system.BaseModule import PyLucidBaseModule


class page_update_list(PyLucidBaseModule):

    def lucidTag(self):
        return self.generate_list(10)

    def lucidFunction(self, count):
        try:
            count = int(count)
        except Exception, e:
            msg = "lucidFunction is not a int number: %s" % e
            self.page_msg(msg)
            return "[%s]" % msg

        return self.generate_list(count)

    def generate_list(self, count):
        page_updates = self.db.get_page_update_info(self.request, 10)

        context = {
            "page_updates" : page_updates
        }
        #~ self.page_msg(context)

        #~ self.templates.write("PageUpdateTable", context)

        t = get_template("PyLucid/buildin_plugins/page_update_list/PageUpdateTable.html")
        c = Context(context)
        html = t.render(c)
        return html













