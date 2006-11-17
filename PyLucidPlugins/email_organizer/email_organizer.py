#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Organize your emails with PyLucid ;)
"""

__author__  = "Alen Hopek"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.mactricks.de"


__version__="0.1"
__history__="""
v0.1
    - init
"""

__todo__ = """
"""

import os, urllib2, urllib, pprint
from PyLucid.system.BaseModule import PyLucidBaseModule

class email_organizer(PyLucidBaseModule):

    def lucidTag(self):
        ''' Nope '''

    # --- Action Methods ---

    def liste(self):
        template_entry = {}

        if "kategorie" in self.request.form:  template_entry['form_data'] = self.request.form
        if "stichwort" in self.request.form:   template_entry['form_data'] = self.request.form

        template_entry['option_entries'] = self._GetOptionFieldData()

        template_entry['other'] = self._MakeOtherVariables()
        template_entry['other']['mode']     = "ShowListView"

        template_entry['menu_entries'] = self._MakeMenuEntries()
        template_entry['list_entries'] = self._GetListData()

        if "suchwort" in self.request.form:
            template_entry['list_entries'] = self._GetKeywordResults()


        if "kategorie" in self.request.args:
            PreSelected = self.request.args['kategorie']
            self.request.form['kategorie'] = PreSelected

            template_entry['option_entries'] = self._GetOptionFieldData( PreSelected )
            template_entry['list_entries'] = self._GetListData()

        self.templates.write("email_auswahl_liste", template_entry)
        self.page_msg( self.request.form )



    def NewCategory(self):
        template_entry = {}

        template_entry['other']          = self._MakeOtherVariables()
        template_entry['other']['mode']  = "AddCategory"

       # Get FormData
        if self.request.form:
            template_entry['form_data'] = self.request.form

            self.db.insert(
                "email_table",
                self.request.form,
            )

            template_entry['other']['status'] = "<b>STATUS</b>: Datensatz wurde erfolgreich gespeichert."

        template_entry['menu_entries']   = self._MakeMenuEntries()


        self.templates.write("add_category", template_entry)
        #self.page_msg( template_entry )


    def AddEmail(self):
        template_entry = {}

        template_entry['other']          = self._MakeOtherVariables()
        template_entry['other']['mode']  = "AddMailAdress"

        # Get FormData
        if self.request.form:
            template_entry['form_data'] = self.request.form

            self.db.insert(
                "email_table",
                self.request.form,
            )

            template_entry['other']['status'] = "<b>STATUS</b>: Datensatz wurde erfolgreich gespeichert."

        template_entry['option_entries'] = self._GetOptionFieldData()
        template_entry['menu_entries']   = self._MakeMenuEntries()

        # Remove first two items from List "" and "-- Alle --"
        option_list = template_entry['option_entries']['list']
        option_list[0:2] = []

        self.templates.write("add_email", template_entry)
        #self.page_msg( template_entry )


    def EditDataset(self):
        dataset_entries = {}
        template_entry  = {}


        template_entry = {}

        template_entry['other']          = self._MakeOtherVariables()
        template_entry['other']['mode']  = "AddMailAdress"

        template_entry['menu_entries']   = self._MakeMenuEntries()

        kat_value = []
        if self.request.form.has_key("kategorie"):
            kategorie = self.request.form["kategorie"]
            kat_value.append({ "selected" : kategorie })
            template_entry['kategorie'] = kat_value


        SQLresult = self.db.select(
            select_items    = ["nr", "kategorie", "email", "name", "bemerkung"],
            from_table      = "email_table",
            where           = ( "nr",  self.request.args['nr'] )
        )

        for item in SQLresult:
            dataset_entries["kategorie_field"]   = item['kategorie']
            dataset_entries["name_field"]        = item['name']
            dataset_entries["email_field"]       = item['email']
            dataset_entries["bemerkung_field"]   = item['bemerkung']
            act_db_category                      = item['kategorie']

        template_entry['menu_entries'] = self._MakeMenuEntries()
        template_entry['edit_dataset_entry']  = dataset_entries


        template_entry['option_entries'] = self._GetOptionFieldData( act_db_category )

        # Remove first two items from List "" and "-- Alle --"
        option_list = template_entry['option_entries']['list']
        option_list[0:2] = []

        self.templates.write("edit_dataset", template_entry)
        #self.page_msg( template_entry )


    def DeleteDataset(self):
        if "nr" in self.request.args:
            self.db.delete(
                "email_table",
                where = ( "nr", self.request.args['nr'] ),
                limit=1
            )

        self.liste()



    # --- Sub Methodes ---

    def _GetOptionFieldData(self, PreSelected=""):
        option_entries = {}
        cat_values = []

        SQLresult = self.db.select(
            select_items    = ["kategorie"],
            from_table      = "email_table",
            group           = ("kategorie", "ASC")
            )

        cat_values.append( u"" )
        cat_values.append( u"-- Alle --" )
        for item in SQLresult:
            cat_values.append(item['kategorie'])

        option_entries['list'] = cat_values

        if PreSelected:
            option_entries['selected'] = PreSelected
        elif "kategorie" in self.request.form:
                option_entries['selected'] = self.request.form['kategorie']

        #self.page_msg( option_entries )

        return option_entries


    def _GetListData(self):
        list_entries = []

        first_color = "#FEFEFE"
        second_color   = "#EFEFEF"
        bgcolor  = first_color

        if self.request.form.has_key("kategorie"):
            kategorie = self.request.form["kategorie"]

            if kategorie ==  "-- Alle --":
                SQLresult = self.db.select(
                    select_items = ["nr", "kategorie", "email", "name", "bemerkung"],
                    from_table = "email_table",
                )
            else:
                SQLresult = self.db.select(
                    select_items = ["nr","kategorie", "email", "name", "bemerkung"],
                    from_table = "email_table",
                    where = ( "kategorie", kategorie ),
                )

            for item in SQLresult:
                if bgcolor == second_color: bgcolor = first_color
                else: bgcolor = second_color

                list_entries.append(
                {
                    "id" : item['nr'],
                    "kategorie" : item['kategorie'],
                    "email" : item['email'],
                    "name" : item['name'],
                    "bemerkung" : item['bemerkung'],
                    "bgcolor" : bgcolor
                }
            )
        return list_entries


    def _GetKeywordResults(self):
        KeyWordResults = []

        first_color = "#FEFEFE"
        second_color = "#EFEFEF"
        highlight_color = "red"
        bgcolor = first_color

        SQLresult = self.db.select(
            select_items = ["nr","kategorie", "email", "name", "bemerkung"],
            from_table = "email_table",
            like = ( "name", self.request.form['suchwort'] ),
        )

        for item in SQLresult:
            if bgcolor == second_color: bgcolor = first_color
            else: bgcolor = second_color

            KeyWordResults.append(
            {
                "id" : item['nr'],
                "kategorie" : item['kategorie'],
                "email" : item['email'],
                "name" : item['name'],
                "bemerkung" : item['bemerkung'],
                "bgcolor" : bgcolor
            }
        )

        return KeyWordResults



    # --- Some other definitions ---

    def _MakeMenuEntries(self):
        menulist = {}
        menulist["Liste"]           = self.URLs.commandLink("email_organizer", "liste")
        menulist["Neue_Kategorie"]  = self.URLs.commandLink("email_organizer", "NewCategory")
        menulist["Neue_EMail"]      = self.URLs.commandLink("email_organizer", "AddEmail")

        return menulist


    def _MakeOtherVariables(self):
        other = {}
        other["keyword_form_action"] = self.URLs.currentAction()
        other["select_form_action"]    = self.URLs.currentAction()
        other["delete_action"]         = self.URLs.commandLink("email_organizer", "DeleteDataset")
        other["edit_action"]             = self.URLs.commandLink("email_organizer", "EditDataset")

        return other
