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

from PyLucid.system.BaseModule import PyLucidBaseModule


class page_update_list(PyLucidBaseModule):

    def lucidTag(self):
        self.generate_list(10)

    def lucidFunction(self, count):
        try:
            count = int(count)
        except Exception, e:
            msg = "lucidFunction is not a int number: %s" % e
            self.page_msg(msg)
            self.response.write("[%s]" % msg)
            return

        self.generate_list(count)

    def generate_list(self, count):
        page_updates = self.db.page.get_update_info(self.request, 10)

        context = {
            "page_updates" : page_updates
        }
#        self.page_msg(context)

        self._render_template("PageUpdateTable", context)













