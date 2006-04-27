#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Menu Routinen für "install PyLucid"
"""

class ObjectApp_Base(object):
    """ Basisklasse von der jede ObjApp-Klasse ableitet """
    def _get_module_admin(self):
        self.request.URLs["action"] = "?action=module_admin&sub_action="

        from PyLucid.modules import module_admin

        module_admin = module_admin.module_admin(self.request, call_from_install_PyLucid = True)

        return module_admin

    def _write_info(self):
        #~ self.response.write("<pre>")
        try:
            stack_info = inspect.stack()[1]
            attr_name = stack_info[3]
            info = getattr(self, attr_name).__doc__
        except:
            pass
        else:
            self.response.write("<h3>%s</h3>" % info)

        self._write_backlink()

    def _write_backlink(self):
        url_info = ()
        self.response.write(
            '<p><a href="%s">%s</a></p>' % (
                self.request.environ["SCRIPT_ROOT"], "menu"
            )
        )