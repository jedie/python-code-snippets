#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Self PyLucid Documentation

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

import cgi, inspect

from PyLucid.components.plugin_cfg import PluginConfig
from PyLucid.tools.out_buffer import Redirector
from PyLucid.system.BaseModule import PyLucidBaseModule

class SelfDocu(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(SelfDocu, self).__init__(*args, **kwargs)

        self.plugin_cfg = PluginConfig(self.request, self.response)

    def lucidTag(self):
        self.menu()

    def menu(self):
        self.response.write(
            "<h4>self documentation <small>(%s)</small></h4>" % \
                                                        __version__.strip("$ ")
        )
        self.response.write(self.module_manager.build_menu())

    def object_hierarchy(self, function_info=None):
        context = {
            "menu_link": self.URLs.actionLink("menu"),
        }
        if function_info == None:
            context["obj_info"] = self._get_start_object_info()
        else:
            context["obj_info"] = self._make_obj_info(function_info)

        """
{'menu_data': [{'href': u'/Index/',
                'level': 0,
                'name': u'index',
                'subitems': [{'href': u'/Index/Newpage/',
                              'level': 1,
                              'name': u'Newpage',
                              'title': u'Newpage'},
                             {'href': u'/Index/LucidTagPygallery/',
                              'level': 1,
                              'name': u'<lucidTag:pygallery/>',
                              'title': u'<lucidTag:pygallery/>'},
                             {'href': u'/Index/LucidTagPygallerySetup/',
                              'level': 1,
                              'name': u'<lucidTag:pygallery.setup/>',
                              'title': u'<lucidTag:pygallery.setup/>'},
                             {'href': u'/Index/LucidTagSelfDocu/',
                              'is_current_page': True,
                              'level': 1,
                              'name': u'<lucidTag:SelfDocu/>',
                              'title': u'<lucidTag:SelfDocu/>'}],
                'title': u'index'},
               {'href': u'/ExamplePages/',
                'level': 0,
                'name': u'example pages',
                'title': u'example pages'}]}
        """

        #~ self.page_msg(context)
        self.templates.write("object_select", context)

    def _make_obj_info(self, function_info):

        selected_object = function_info[0].split(".")
        if not selected_object[0] in self.plugin_cfg["object_names"]:
            self.page_msg.red("Object name Error!")
            return

        object_data = []
        for obj_name in selected_object[1:-1]:
            self.page_msg("1:", obj_name)
            #~ data = {
                #~ "name": obj_name
            #~ }
            try:
                attr_info = self.display_object(obj_name)
            except Exception, e:
                self.page_msg.red("Error: %s" % e)
                continue

            self.page_msg(attr_info)

            #~ object_data
            #~ context[obj_name] = attr_info

        self.page_msg("2:", selected_object[-1])

    def _get_start_object_info(self):
        result = []
        for obj_name in self.plugin_cfg["object_names"]:
            result.append(self._get_basic_obj_info(self, obj_name))
        return result

    def _get_basic_obj_info(self, parent_obj, obj_name):
        context = self._get_object_info(parent_obj, obj_name)

        subitems = self._get_object_attributes(parent_obj, obj_name)
        if subitems!=[]:
            context["subitems"] = subitems

        return context

    def _get_object_attributes(self, parent_obj, obj_name):
        obj = getattr(parent_obj, obj_name)
        attributes = dir(obj)

        result = []
        for attr_name in attributes:
            if attr_name.startswith("_"):
                continue

            result.append(
                self._get_object_info(obj, attr_name)
            )

        return result

    def _get_object_info(self, parent_obj, obj_name):
        obj = getattr(parent_obj, obj_name)

        context = {
            "name": obj_name,
            "type": self.__get_type_info(obj),
        }

        doc = self.__get_doc_or_help(obj)
        if doc != None:
            context["doc"] = doc

        return context

    def __get_doc_or_help(self, obj):
        doc = self.__get_doc(obj)
        if doc != None:
            return doc

        doc = self.__get_help(obj)
        if doc != None:
            return doc

    def __get_help(self, obj):
        out = Redirector(self.page_msg)
        help(obj)
        return cgi.escape(out.get())

    def __get_doc(self, obj):
        doc = obj.__doc__
        if doc == None:
            return None

        try:
            doc = unicode(doc, "utf8")
        except UnicodeError, e:
            doc = "%s [Unicode Error: %s]" % (
                unicode(doc, errors="replace"), e
            )

        doc = doc.strip()
        if doc == "":
            return None

        doc = cgi.escape(doc)
        return doc

    def __get_type_info(self, obj):
        type_info = type(obj)
        type_info = unicode(type_info)
        type_info = type_info.strip("<>")
        return type_info

    #_______________________________________________________________________

    def pygments_lexer_list(self):
        """
        Liste alle vorhandener pygments Lexer erstellen
        """
        from pygments_info import lexer_list
        lexer_list(self.request, self.response)

    def pygments_css(self, function_info=None):
        from pygments_info import style_info
        style_info(self.request, self.response, function_info)