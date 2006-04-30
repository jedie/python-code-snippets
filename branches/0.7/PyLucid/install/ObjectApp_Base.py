#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Menu Routinen für "install PyLucid"
"""

import inspect, sys, posixpath


class ObjectApp_Base(object):
    """ Basisklasse von der jede ObjApp-Klasse ableitet """
    def _get_module_admin(self):
        self.request.URLs["action"] = "?action=module_admin&sub_action="

        from PyLucid.modules import module_admin

        module_admin = module_admin.module_admin(self.request, call_from_install_PyLucid = True)

        return module_admin

    def _write_info(self):
        try:
            stack_info = inspect.stack()
            #~ self.response.echo(stack_info)
            stack_info = stack_info[1]
            attr_name = stack_info[3]
            info = getattr(self, attr_name).__doc__
        except:
            info = self.request.environ['PATH_INFO']

        self.response.write("<h3>%s</h3>" % info)

        self._write_backlink()

    def _write_backlink(self):
        url = posixpath.join(
            self._environ["SCRIPT_ROOT"], self._preferences["installURLprefix"]
        )
        self.response.write('<p><a href="%s">menu</a></p>' % url)


    def _get_module_admin(self):
        self._URLs["action"] = "?action=module_admin&sub_action="

        from PyLucid.modules import module_admin

        module_admin = module_admin.module_admin(self.request, self.response)

        return module_admin