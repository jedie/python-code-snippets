#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

"""
Erzeugt das Administration-Menü
(ehemals front_menu aus dem alten page-renderer)

<lucidTag:admin_menu/>
Sollte im Template für jede Seite eingebunden werden.
"""

__version__="0.0.4"

__history__="""
v0.0.4
    - nutzt nun self.db.print_internal_page()
v0.0.3
    - Anpassung an wegfall von apply_markup
v0.0.2
    - lucidTag ist nicht mehr front_menu sondern admin_menu
v0.0.1
    - erste Version
"""

__todo__ = """
"""



from PyLucid.system.BaseModule import PyLucidBaseModule

class admin_menu(PyLucidBaseModule):

    #~ def __init__(self, *args, **kwargs):
        #~ super(main_menu, self).__init__(*args, **kwargs)

    def lucidTag( self ):
        """
        Front menu anzeigen
        """
        context = {
            "login"             : self.request.staticTags['script_login'],
            "edit_page_link"    : self.URLs.make_command_link("pageadmin", "edit_page"),
            "new_page_link"     : self.URLs.make_command_link("pageadmin", "new_page"),
            "sub_menu_link"     : self.URLs.make_command_link("admin_menu", "sub_menu"),
        }
        return self.templates.write("admin_menu_top_menu", context)

    def sub_menu( self ):
        context = {
            "commandURLprefix"  : self.URLs.get_commandURLPrefix()
        }
        return self.templates.write("admin_menu_sub_menu", context)








