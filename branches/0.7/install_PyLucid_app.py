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




class ObjectApp_MenuGenerator(object):

    def __init__(self, request, root):
        self.request = request
        self.root = root

    def root_link(self, path, info):
        "Methode zum überscheiben"
        self.request.write('<a href="%s">%s</a>' % (path, info))

    def sub_link(self, path, info):
        "Methode zum überscheiben"
        self.request.write('<a href="%s">%s</a>' % (path, info))

    def _get_objnamelist(self, obj, attr_type):
        """
        Baut eine Liste mit den nötigen Informationen für ein Menü zusammen
        Hilfmethode für make_menu
        """
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

            info = cgi.escape(info)

            result.append([info, objname, obj_attr])
        result.sort()
        return result

    def get_menu_data(self):
        """ Liefert eine verschachtelre Liste mit den Menüdaten zurück """
        result = []
        objnamelist = self._get_objnamelist(self.root, attr_type="class")
        for info, path, obj_attr in objnamelist:
            result.append((path, info))
            temp = []
            subobjnamelist = self._get_objnamelist(obj_attr, attr_type="methods")
            for sub_info, sub_path, _ in subobjnamelist:
                sub_path = "%s/%s" % (path, sub_path)
                temp.append((sub_path, sub_info))
            result.append(temp)
        return result

    # Zum überschreiben/Anpassen:
    root_list_tags = ('\n<ul>\n', '</ul>\n', '\t<li>', '</li>\n')
    sub_list_tags = ('\t<ul>\n', '\t</ul>\n', '\t\t<li>', '</li>\n')

    def make_menu(self):
        """
        Generiert ein Menü für alle vorhandenen Objekte/Pfade und nutzt
        dabei die erste Zeile des DocString von jeder Klasse/Methode.
        Generell wird das Menü nach DocString sortiert, d.h. wenn man
        gezielt eine sortierung haben will, kann man z.B. den DocString
        mit 1., 2., 3. anfangen.
        """
        def write_menu(handler, item, tags):
            """Ruft den passenden Handler, also self.sub_link oder
            self.root_link mit den Menü-Daten auf"""
            self.request.write(tags[2])
            handler(*item)
            self.request.write(tags[3])

        self.request.write(self.root_list_tags[0])
        for item in self.get_menu_data():
            if isinstance(item, list):
                # Untermenüpunkte
                self.request.write(self.sub_list_tags[0])
                for sub_item in item:
                    write_menu(self.sub_link, sub_item, self.sub_list_tags)
                self.request.write(self.sub_list_tags[1])
            else:
                # Hauptmenüpunkt
                write_menu(
                    self.root_link, item, self.root_list_tags
                )

        self.request.write(self.root_list_tags[1])


class MyMenuGenerator(ObjectApp_MenuGenerator):
    """
    Anpassen des Menügenerators
    """
    # id="menu" in ul einbauen
    root_list_tags = ('\n<ul id="menu">\n', '</ul>\n', '\t<li>', '</li>\n')

    def root_link(self, path, info):
        "Methode zum Überscheiben"
        try: # Zahlen bei den Hauptmení±µnkten weg schneiden
            info = info.split(" ",1)[1]
        except:
            pass
        self.request.write('<h4>%s</h4>' % info)



import inspect


import config # PyLucid Konfiguration
from PyLucid.system import sessiondata
from PyLucid.system import preferences
from PyLucid.system import tools
from PyLucid.system import db


class base(object):
    """ Basisklasse von der jede ObjApp-Klasse ableitet """
    def _get_module_admin(self):
        #~ self.PyLucid["URLs"]["action"] = "?action=module_admin&sub_action="

        from PyLucid.modules import module_admin

        module_admin = module_admin.module_admin(self.request, call_from_install_PyLucid = True)

        return module_admin

    def _write_info(self):
        #~ self.request.write("<pre>")
        try:
            stack_info = inspect.stack()[1]
            attr_name = stack_info[3]
            info = getattr(self, attr_name).__doc__
        except:
            pass
        else:
            self.request.write("<h3>%s</h3>" % info)

        self._write_backlink()

    def _write_backlink(self):
        url_info = ()
        self.request.write(
            '<p><a href="%s">%s</a></p>' % (
                self.request.environ["SCRIPT_ROOT"], "menu"
            )
        )



class index(base):
    def index(self):
        "Main Menu"
        #~ self._write_head(backlink=False)
        self.request.write("Please select:")
        #~ self.make_menu()
        self.MenuGenerator.make_menu()

    def name(self, arg1="Default", arg2="Default"):
        """Beispiel für eine Parameter übergabe"""
        self._info('index.name')
        self.request.write(
            'arg1="%s" - arg2="%s"' % (arg1, arg2)
        )


class install(base):
    "1. install PyLucid from scratch"
    def init_DB(self):
        "1. init Database tables"
        self._write_info()

    def init_modules(self):
        "2. init basic Modules"
        self._write_info()

    def add_admin(self):
        "3. add a admin user"
        self._write_info()


class admin(base):
    "2. low level Admin"
    def module_admin(self):
        "Module/Plugin Administration"
        self._write_info()

        module_admin = self._get_module_admin()

        sub_action = self.CGIdata.get("sub_action", None)

        if sub_action == "install":
            try:
                module_admin.install(self.CGIdata["package"], self.CGIdata["module_name"])
            except KeyError, e:
                self.request.write("KeyError: %s" % e)
            return
        elif sub_action == "deinstall":
            try:
                module_admin.deinstall(self.CGIdata["id"])
            except KeyError, e:
                self.request.write("KeyError: %s" % e)
            return
        elif sub_action == "reinit":
            try:
                module_admin.reinit(self.CGIdata["id"])
            except KeyError, e:
                self.request.write("KeyError: %s" % e)
            return
        elif sub_action == "activate":
            try:
                module_admin.activate(self.CGIdata["id"])
            except KeyError, e:
                self.request.write("KeyError: %s" % e)
        elif sub_action == "deactivate":
            try:
                module_admin.deactivate(self.CGIdata["id"])
            except KeyError, e:
                self.request.write("KeyError: %s" % e)
        elif sub_action == "module_admin_info":
            self.module_admin_info()
            return
        elif sub_action == "administation_menu":
            self.print_backlink()
        elif sub_action == "init_modules":
            self.print_backlink()
            if self.CGIdata.get("confirm","no") == "yes":
                module_admin = self._get_module_admin()
                module_admin.first_time_install_confirmed()
            self.print_backlink()
            return

        module_admin.administation_menu()


    def re_init(self):
        "partially re-initialisation DB tables"
        self._write_info()


class update(base):
    "3. update"
    def update_db(self):
        "update DB tables (PyLucid v0.x -> 0.6)"
        self._write_info()

    def convert_markups(self):
        "Convert Markup Names to IDs (PyLucid v0.x -> 0.5)"
        self._write_info()


class tests(base):
    "4. info / tests"
    def db_info(self):
        "DB connection Information"
        self._write_info()

        self.request.write("<pre>")
        for k,v in self.request.preferences.iteritems():
            if not k.startswith("db"):
                continue
            if k == "dbPassword":
                v = "***"
            self.request.write("%-20s: %s\n" % (k,v))
        self.request.write("</pre>")

    def module_admin_info(self):
        "Information about installed modules"
        self._write_info()

        self.PyLucid["URLs"]["current_action"] = "?action=module_admin&sub_action=module_admin_info"
        module_admin = self._get_module_admin()
        module_admin.debug_installed_modules_info()

    def path_info(self):
        "Path/URL check"
        self._write_info()






class LowLevelAdmin(ObjectApplication):

    root = index
    root.install    = install
    root.update     = update
    root.admin      = admin
    root.tests      = tests

    def __init__(self, *args):
        super(LowLevelAdmin, self).__init__(*args)
        self.request.headers['Content-Type'] = 'text/html'

        self._write_head()

        # Speichert Nachrichten die in der Seite angezeigt werden sollen
        self.page_msg           = sessiondata.page_msg(debug=True)
        #~ self.page_msg           = sessiondata.page_msg(debug=False)
        self.request.page_msg   = self.page_msg
        #~ self.request.exposed.append("page_msg") # An Debug-Info dranpacken

        # Verwaltung für Einstellungen aus der Datenbank
        self.preferences            = preferences.preferences(self.request, config.config)
        self.request.preferences    = self.preferences
        self.request.exposed.append("preferences") # An Debug-Info dranpacken

        # Passt die verwendeten Pfade an.
        self.request.URLs = preferences.URLs(self.request)
        self.request.exposed.append("URLs") # An Debug-Info dranpacken

        tools.request           = self.request # Request Objekt an tools übergeben
        self.request.tools      = tools

        # Anbindung an die SQL-Datenbank, mit speziellen PyLucid Methoden
        self.request.db = db.get_PyLucid_Database(self.request)
        #~ self.request.db = SQL_wrapper.SQL_wrapper(self.request)
        self.db = self.request.db

        # Menügenerator in die Basisklasse "einflanzen"
        base.MenuGenerator = MyMenuGenerator(self.request, self.root)


    def process_request(self):
        super(LowLevelAdmin, self).process_request()
        self.on_close()

    def on_close(self):
        self.request.echo(self.page_msg.get())
        self.request.write(HTML_bottom)
        #~ self.db.close()

    def _write_head(self, backlink=True):
        self.request.write(HTML_head)



app = LowLevelAdmin

if __name__ == '__main__':
    from colubrid import execute
    execute()