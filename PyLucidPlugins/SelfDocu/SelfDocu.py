#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Self PyLucid Documentation

Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev:$"

import cgi

from PyLucid.components.plugin_cfg import PluginConfig
from PyLucid.system.BaseModule import PyLucidBaseModule

class SelfDocu(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(SelfDocu, self).__init__(*args, **kwargs)

        self.plugin_cfg = PluginConfig(self.request, self.response)

    def lucidTag(self):
        #~ url = self.URLs.actionLink("menu")
        #~ self.response.write('<a href="%s">self documentation</a>' % url)
        self.menu()

    def menu(self):
        self.response.write(
            "<h4>self documentation <small>(%s)</small></h4>" % \
                                                        __version__.strip("$ ")
        )
        self.response.write(self.module_manager.build_menu())

    def object_hierarchy(self, function_info=None):
        self.page_msg("object_hierarchy")

        context = {
            "menu_link": self.URLs.actionLink("menu"),
        }

        if function_info:
            selected_object = function_info[0].split(".")
            if not selected_object[0] in self.plugin_cfg["object_names"]:
                self.page_msg.red("Object name Error!")
                return
        else:
            raise "jo?"

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

        object_data = []
        for obj_name in selected_object[:-1]:
            self.page_msg("1:", obj_name)
            #~ data = {
                #~ "name": obj_name
            #~ }
            #~ if obj_name == selected_object:
                #~ attr_info = self.display_object(obj_name)

            #~ object_data
            #~ context[obj_name] = attr_info

        self.page_msg("2:", selected_object[-1])

        #~ self.page_msg(context)
        #~ self.templates.write("object_select", context)

    def display_object(self, obj_name):

        obj = getattr(self, obj_name)

        attributes = dir(obj)
        #~ self.page_msg(attributes)

        attr_info = []
        for attr_name in attributes:
            if attr_name.startswith("_"):
                continue

            attr_obj = getattr(obj, attr_name)
            #~ self.page_msg(dir(attr_obj))

            type_info = str(type(attr_obj)).strip("<>")
            #~ self.page_msg(type_info)

            info = {
                "name": attr_name,
                "type": type_info,
            }

            doc = attr_obj.__doc__
            if doc != None:
                info["doc"] = doc.strip()

            attr_info.append(info)

        self.page_msg(attr_info)

        return attr_info


