#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = __long_description__ = (
    "PyGallery - A small picture gallery maker..."
)

#___________________________________________________________________________________________________
# Module-Manager Daten

module_manager_data = {
    "lucidTag" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
    "lucidFunction" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "setup" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "Setup all galleries",
            "template_engine"   : "jinja",
            "markup"            : None
        }
    },
    "gallery_config" : {
        "must_login"    : True,
        "must_admin"    : True,
        "internal_page_info" : {
            "description"       : "Configure a existing gallery",
            "template_engine"   : "jinja",
            "markup"            : None
        }
    },
    "gallery" : {
        "must_login"    : False,
        "must_admin"    : False,
        "internal_page_info" : {
            "description"       : "Default gallery Template",
            "template_engine"   : "jinja",
            "markup"            : None
        }
    },
    "make_thumbs" : {
        "must_login"    : True,
        "must_admin"    : True,
    },
}
plugin_cfg = {
    "dir_filter": ( # PyLucid-Verz. sollen ausgelassen werden.
            "colubrid", "jinja", "pygments", "PyLucid", "tests", "wsgiref"
    ),
    "galleries": {},
    "default_cfg": {
        # Nur Endungen anzeigen, die in der Liste vorkommen
        "ext_whitelist": (".jpg", ".png", ".mpg", ".avi"),

        # =False -> Nur Dateien im aktuellen Verz. anzeigen
        "allow_subdirs": True,

        # Dateien die nicht angezeigt werden sollen
        "file_filter": (".htaccess",),

        ## Thumb-Gallerie-Einstellung
        # pic_ext           = Dateiendungen, die als Bilder behandelt werden sollen
        # thumb_pic_filter  = Filter, der aus den Dateinamen rausgeschnitten werden soll, um
        #                     damit das passende Thumbnail zu finden
        # thumb_suffix      = Liste der Suffixe im Dateiname mit dem ein Thumbnail markiert ist
        # resize_thumb_size = Wird kein Thumbnail gefunden, wird das original Bild auf diese Werte
        #                     verkleinert als Thumb genommen
        #
        # Bsp.:
        # Urlaub01_WEB.jpg   -> Bild zu dem ein Thumbnail gesucht wird
        # Urlaub01_thumb.jpg -> Das passende Thumbnail
        "pic_ext"           : (".jpg", ".jpeg"),
        "thumb_pic_filter"  : ("_WEB",),
        "thumb_suffix"      : ("_thumb",),
        "resize_thumb_size" : (100,60),

        # Name des Bildes
        "name_filter" : {
            "replace_rules" : [# Ersetzten im Dateinamen (Reihenfolge wichtig!)
                ("_WEB", " "),
                ("_klein", " "),
                ("_", " "),
            ],
            "strip_whitespaces": True, # mehrere Leerzeichen zu einem wandeln
        }
    }
}