#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid "installer"
"""

__version__ = "v0.7"

__history__ = """
v0.7
    - Umbau zu einer colubrid WSGI ObjectApplication
v0.6
    - Neu: update_db()
v0.5
    - Neu: "Information about installed modules"
    - ein paar "confirm"-Dialoge eingebaut...
v0.4.1
    - Ein wenig Aufgeräumt
v0.4
    - Anderer Aufbau der actions: In Sektionen unterteilt.
    - Neu: db_info
v0.3.1
    - Packports Pfad hinzugefügt
v0.3
    - Es kann nur einmal ein Admin angelegt werden
    - Benutzt nun einige PyLucid-Objekte (erforderlich für neues userhandling)
    - Möglichkeit dir Markup-String zu IDs zu konvertieren (Änderung in PyLucid v0.5)
    - CSS Spielereien 2
v0.2
    - Anpassung an neue install-Daten-Struktur.
    - "add Admin"-Formular wird mit JavaScript überprüft.
    - NEU Path Check: allerdings wird erstmal nur die Pfade angezeigt, mehr nicht...
    - CSS Spielereien
    - Aussehen geändert
v0.1.0
    - NEU: "partially re-initialisation DB tables" damit kann man nur ausgesuhte
        Tabellen mit den Defaultwerten überschrieben.
v0.0.8
    - Fehler in SQL_dump(): Zeigte SQL-Befehle nur an, anstatt sie auszuführen :(
v0.0.7
    - Neue Art die nötigen Tabellen anzulegen.
v0.0.6
    - Einige anpassungen
v0.0.5
    - NEU: convert_db: Convertiert Daten von PHP-LucidCMS nach PyLucid
v0.0.4
    - Anpassung an neuer Verzeichnisstruktur
v0.0.3
    - NEU: update internal pages
v0.0.2
    - Anpassung an neuer SQL.py Version
    - SQL-connection werden am Ende beendet
v0.0.1
    - erste Version
"""

__todo__ = """
Sicherheitslücke: Es sollte nur ein Admin angelegt werden können, wenn noch keiner existiert!
"""


import cgi

from colubrid import ObjectApplication





HTML_head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>PyLucid Setup</title>
<meta name="robots"             content="noindex,nofollow" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<style type="text/css">
html, body {
    padding: 30px;
    background-color: #FFFFEE;
}
body {
    font-family: tahoma, arial, sans-serif;
    color: #000000;
    font-size: 0.9em;
    background-color: #FFFFDB;
    margin: 30px;
    border: 3px solid #C9C573;
}
form * {
  vertical-align:middle;
}
input {
    border: 1px solid #C9C573;
    margin: 0.4em;
}
pre {
    background-color: #FFFFFF;
    padding: 1em;
}
#menu li, #menu li a {
    list-style-type: none;
    padding: 0.3em;
}
#menu h4 {
    margin: 0px;
}
a {
    color:#00BBEE;
    padding: 0.1em;
}
a:hover {
    color:#000000;
    background-color: #F4F4D2;
}
</style>
<h2>PyLucid Setup %s</h2>""" % __version__
HTML_bottom = "</body></html>"










class base(object):

    actions = [
        {
            "class"     : "install",
            "head"      : "install PyLucid from scratch",
            "methods"   : [
                ("init_DB",              "1. init Database tables"),
                ("init_modules",         "2. init basic Modules"),
                ("add_admin",            "3. add a admin user"),
            ]
        },
        {
            "class"     : "admin",
            "head"      : "low level Admin",
            "methods"   : [
                ("module_admin",         "Module/Plugin Administration"),
                ("re_init",              "partially re-initialisation DB tables"),
            ]
        },
        {
            "class"     : "update",
            "head"      : "low level Admin",
            "methods"   : [
                ("update_db",            "update DB tables (PyLucid v0.x -&gt; 0.6)"),
                ("convert_markups",      "Convert Markup Names to IDs (PyLucid v0.x -&gt; 0.5)"),
                #~ (self.convert_db,       "convert_db",           "convert DB data from PHP-LucidCMS to PyLucid Format"),
                #~ (self.convert_locals,   "locals",               "convert locals (ony preview!)"),
            ]
        },
        {
            "class"     : "tests",
            "head"      : "info / tests",
            "methods"   : [
                ("db_info",              "DB connection Information"),
                ("module_admin_info",    "Information about installed modules"),
                ("path_info",            "Path/URL check"),
            ]
        },
    ]

    def _write_head(self, backlink=True):
        self.request.write(HTML_head)
        if backlink == True:
            url_info = (self.request.environ["SCRIPT_ROOT"], "menu")
            self.request.write('<p><a href="%s">%s</a></p>' % url_info)



class index(base):
    local_var = "1"
    def index(self):
        self._write_head(backlink=False)
        self.request.write("Please select:")
        self.request.write('<ul id="menu">')
        for section in self.actions:
            #~ self.request.write("%s\n" % str(section))
            self.request.write("<li><h4>%s</h4>" % section["head"])
            self.request.write("\t<ul>")
            for method in section["methods"]:
                self.request.write(
                    '\t\t<li><a href="%s/%s">%s</a></li>' % (
                        section["class"], method[0], method[1]
                    )
                )
            self.request.write("\t</ul>")

        self.request.write("</ul>")

    def name(self, arg1="Default", arg2="Default"):
        """Beispiel für eine Parameter übergabe"""
        self._info('index.name')
        self.request.write(
            'arg1="%s" - arg2="%s"' % (arg1, arg2)
        )


class install(base):
    "install PyLucid from scratch"
    def init_DB(self):
        self._write_head()
        self.request.write("init_DB:")
    def init_modules(self):
        self._write_head()
        self.request.write("init_modules")
    def add_admin(self):
        self._write_head()
        self.request.write("Please select:")


class tests(base):
    "info / tests"
    def db_info(self):
        pass
    def module_admin_info(self):
        pass
    def path_info(self):
        pass


class ObjectApplication2(ObjectApplication):

    def _root_link(self, path, info):
        "Methode zum überscheiben"
        self.request.write('<a href="%s">%s</a>' % (path, info))

    def _sub_link(self, path, info):
        "Methode zum überscheiben"
        self.request.write('<a href="%s">%s</a>' % (path, info))

    def _get_objnamelist(self, obj, attr_type):
        """Hilfmethode für _make_menu"""

        raise TypeError("TEST")

        result = []
        for objname in dir(obj):
            if objname.startswith("_"):
                continue

            obj_attr = getattr(obj, objname)
            if attr_type == "methods": # Methoden einer Klasse
                if getattr(obj_attr, "__call__", None) == None:
                    continue
            elif attr_type == "class": # Klassen des root-Objekts
                if type(obj_attr) != type:
                    continue
            else:
                raise TypeError("attr_type must be 'class' or 'methods'!")

            if obj_attr.__doc__:
                info = obj_attr.__doc__
                info = info.strip().split("\n",1)[0]
            else:
                info = objname

            result.append([objname, info, obj_attr])
        return result

    def _make_menu(self, top_link=True):

        self.request.write("<ul>\n")

        objnamelist = self._get_objnamelist(self.root, attr_type="class")
        for path, info, obj_attr in objnamelist:
            self.request.write('<li>\n')
            self._root_link(path, info)
            self.request.write('</li>\n')

            self.request.write("<ul>")
            subobjnamelist = self._get_objnamelist(obj_attr, attr_type="methods")
            for sub_path, sub_info, sub_obj_attr in subobjnamelist:
                self.request.write('<li>\n')
                self._sub_link("%s/%s" % (path, sub_path), info)
                self.request.write('</li>\n')
            self.request.write("</ul>")

        self.request.write("</ul>")



class LowLevelAdmin(ObjectApplication2):

    root = index
    root.install = install
    root.tests = tests

    def __init__(self, *args):
        super(LowLevelAdmin, self).__init__(*args)
        self.request.headers['Content-Type'] = 'text/html'

    def process_request(self):
        super(LowLevelAdmin, self).process_request()
        self._make_menu()




app = LowLevelAdmin

if __name__ == '__main__':
    from colubrid import execute
    execute()