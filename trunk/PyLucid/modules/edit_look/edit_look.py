#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Editor für alles was mit aussehen zu tun hat:
    - edit_style
    - edit_template
    - edit_internal_page

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

__version__ = "$Rev$"

# Python-Basis Module einbinden
import sys, cgi


#~ debug = True
debug = False


from PyLucid.system.BaseModule import PyLucidBaseModule


class StyleAndTemplate(PyLucidBaseModule):
    """
    Methoden für Stylesheet und Template Verwaltung
    """

    def action(self):

        #~ self.response.debug()
        #~ self.page_msg.debug(self.request.form)

        if "edit" in self.request.form:
            self._makeEditPage()
            return
        elif "clone" in self.request.form:
            self._cloneItem()
        elif "del" in self.request.form:
            self._delItem()
        elif "apply" in self.request.form:
            self._applyItem()
            return
        elif "default" in self.request.form and "set" in self.request.form:
            self._set_default()
        elif "save" in self.request.form:
            self._updateItem()

        # Styles/Templates Auswahl anzeigen:
        self._select_table()


    def _cloneItem(self):
        """ Ein Stylesheet soll kopiert werden """

        clone_name = self.request.form["clone_name"]

        try:
            content = \
                    self.db_getItemDataByName(clone_name)["content"]
        except IndexError:
            msg = "Can't get content from %s '%s'" % (
                self.type, clone_name
            )
            self.page_msg(msg)
            return

        new_name = self.request.form.get("new_name", "%s_copy" % clone_name)
        # Einen evtl. doppelten Namen eindeutig machen (Zahl wird angehängt)
        new_name = self.db_getUniqueItemName(new_name)

        data = {
            "name"          : new_name,
            "description"   : "clone of '%s'" % clone_name,
            "content"       : content,
        }
        try:
            self.db_newItem(data)
        except Exception, e:
            msg = "Error clone %s '%s' to '%s': %s" % (
                self.type, clone_name, new_name, e
            )
        else:
            msg = "%s '%s' duplicated to '%s'" % (
                self.type, clone_name, new_name
            )

        self.page_msg(msg)

    def _applyItem(self):
        """
        Apply-Button
        Speichern und direkt wieder im Editor öffnen
        """
        self._updateItem()
        self._makeEditPage()

    def _updateItem(self):
        """
        Speichert die Änderungen vom template oder stylesheet editieren.
        """
        id = self._getID()
        if id==None: return

        name = self.request.form["name"]
        data = {
            "name": name,
            "description": self.request.form.get("description",""),
            "content": self.request.form["content"]
        }
        try:
            self.db_updateItem(id, data)
        except Exception, e:
            self.page_msg("Can't update %s: %s" % (self.type, e))
        else:
            self.page_msg("%s '%s' saved!" % (self.type, name))


    def _makeEditPage(self):
        """ Erstellt die Seite zum Stylesheet/Template editieren """

        id = self._getID()
        if id==None: return

        try:
            edit_data = self.db_getItemData(id)
        except IndexError:
            self.page_msg("bad style id '%s'!" % id)
            return

        context = {
            "name"          : edit_data["name"],
            "url"           : self.URLs.currentAction(),
            "url_taglist"   : self.URLs.commandLink("pageadmin", "tag_list"),
            "content"       : cgi.escape( edit_data["content"] ),
            "description"   : cgi.escape( edit_data["description"] ),
            "id"            : id,
        }
        internal_page_name = "edit_%s" % self.type
        self.templates.write(internal_page_name, context, debug)

    def _select_table(self):
        """ Erstellt die Tabelle zum auswählen eines Style/Templates """

        # default Style/Template, stored in the preferences
        default_name = self.get_default()

        table_data = self.db_getItemList()
        nameList = [i["name"] for i in table_data]

        context = {
            "url"           : self.URLs.currentAction(),
            "nameList"      : nameList,
            "itemsDict"     : table_data,
            "default_name"  : default_name,
        }
        internalPageName = "select_%s" % self.type
        self.templates.write(internalPageName, context, debug)

    def _delItem( self ):
        """ Lösche ein Stylesheet """
        id = self._getID()
        if id==None: return

        page_names = self.db.select(
            select_items    = ["name"],
            from_table      = "pages",
            where           = (self.type, id)
        )
        if page_names:
            names = [cgi.escape(i["name"]) for i in page_names]
            msg = (
                "Can't delete %s, the following pages used it:\n"
                "%s"
            ) % (self.type, names)
            self.page_msg(msg)
            return

        try:
            self.db_deleteItem(id)
        except Exception, e:
            msg = "Error deleting %s with id '%s': %s" % (self.type, id, e)
        else:
            msg = "%s with id %s deleted." % (self.type, id)

        self.page_msg(msg)

    def _getID(self):
        try:
            id = self.request.form["id"]
        except KeyError:
            self.page_msg("Error: There is no %s ID in POST data!" % self.type)
            return None

        try:
            id = int(id)
        except:
            self.page_msg("Error: %s ID is not a number!" % self.type)
            return None

        return id

    def _set_default(self):
        default_name = self.request.form["default"]
        self.set_default(default_name)





#_____________________________________________________________________________

class Style(StyleAndTemplate):
    """
    Namen und Methoden zur Stylesheet Verabreitung
    """
    table_name = "styles"
    type = "style"

    def __init__(self, *args, **kwargs):
        super(Style, self).__init__(*args, **kwargs)

        # Datenbank-Methoden für die Stylesheet Verabreitung definieren die
        # von der Klasse StyleAndTemplate benutzt werden:

        # select
        self.db_getItemList = self.db.get_style_list

        # edit
        self.db_getItemData = self.db.get_style_data

        # save
        self.db_updateItem = self.db.update_style

        # clone
        self.db_newItem = self.db.new_style
        self.db_getItemDataByName = self.db.get_style_data_by_name
        self.db_getUniqueItemName = self.db.get_UniqueStylename

        # delete
        self.db_deleteItem = self.db.delete_style

        # default
        self.get_default = self.preferences.get_default_style_name
        self.set_default = self.preferences.set_default_style



#_____________________________________________________________________________

class Template(StyleAndTemplate):
    """
    Namen und Methoden zur Template Verabreitung
    """
    table_name = "templates"
    type = "template"

    def __init__(self, *args, **kwargs):
        super(Template, self).__init__(*args, **kwargs)

        # Datenbank-Methoden für die Template Verabreitung definieren die
        # von der Klasse StyleAndTemplate benutzt werden:

        # select
        self.db_getItemList = self.db.get_template_list

        # edit
        self.db_getItemData = self.db.get_template_data

        # save
        self.db_updateItem = self.db.update_template

        # clone
        self.db_newItem = self.db.new_template
        self.db_getItemDataByName = self.db.get_template_data_by_name
        self.db_getUniqueItemName = self.db.get_UniqueTemplatename

        # delete
        self.db_deleteItem = self.db.delete_template

        # default
        self.get_default = self.preferences.get_default_template_name
        self.set_default = self.preferences.set_default_template



#_____________________________________________________________________________

class edit_look(PyLucidBaseModule):

    def stylesheet(self):
        """ Es wird die internal_page 'select_style' zusammen gebaut """
        s = Style(self.request, self.response)
        s.action()


    def template(self):
        """ Es wird die internal_page 'select_template' zusammen gebaut """
        t = Template(self.request, self.response)
        t.action()

    #_________________________________________________________________________
    ## Interne Seiten editieren

    def internal_page(self):
        EditInternalPage = self.__get_EditInternalPage()
        EditInternalPage.internal_page()

    def edit_internal_page(self, function_info):
        """ Formular zum editieren einer internen Seite """
        EditInternalPage = self.__get_EditInternalPage()
        EditInternalPage.edit_internal_page(function_info)

    def download_internal_page(self, function_info):
        EditInternalPage = self.__get_EditInternalPage()
        return EditInternalPage.download_internal_page(function_info)

    def save_all_local(self):
        EditInternalPage = self.__get_EditInternalPage()
        EditInternalPage.save_all_local()

    def internal_page_diff(self, function_info):
        EditInternalPage = self.__get_EditInternalPage()
        EditInternalPage.internal_page_diff(function_info)

    def __get_EditInternalPage(self):
        from PyLucid.modules.edit_look.edit_internal_page \
                                                        import EditInternalPage

        EditInternalPage = EditInternalPage(self.request, self.response)
        return EditInternalPage


    #_______________________________________________________________________
    ## Allgemeine Funktionen

    def error( *msg ):
        page  = "<h2>Error.</h2>"
        page += "<p>%s</p>" % "<br/>".join( [str(i) for i in msg] )
        return page



