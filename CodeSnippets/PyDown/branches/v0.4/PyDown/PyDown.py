#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyDown - A small Python Download Center...

Info zur Installation/Benutzung: PyDown_readme.txt
"""

# copyleft: jensdiemer.de (GPL v2 or above)

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License v2 or above - http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://www.jensdiemer.de/Programmieren/Python/PyDown"

__version__ = "v0.4.0"

__info__ = """<a href="%s">PyDown %s</a>""" % (__url__, __version__)

__history__ = """
v0.3.1
    - Patch für Windows Downloads: Setzt stdout auf binary vor dem Download
v0.3
    - Dynamische Bandbreitenanpassung möglich
v0.2
    - NEU: einen Info Bereich
    - Kräftig aufgeräumt
v0.1.1
    - Bugfixes for running under Windows
v0.1
    - erste Version
"""



# Basis Config Einstellung
# Diese _nicht_ hier ändern, sondern in der ../PyDown_config.py!!!
cfg = {
    # Nur diese Usernamen haben zugriff, wenn only_auth_users==True
    "allowes_user": (),

    # Username mit dem sich der Admin einloggt
    "admin_username": "",

    # Datei-Endungsfilter, nur diese Dateien werden beachtet
    "ext_whitelist": (".mp3",),

    # Basis-Pfad, der "Rekursiv-Freigegeben" werden soll.
    # unter Windows:
    #       -normalen slash "/" verwenden!
    #       -ganze Laufwerke mit abschließendem slash!
    "base_path": "/tmp",

    # Nur HTTPs Verbindungen erlauben?
    "only_https": True,

    # Zugriff nur eingeloggte User, durch Apache's .htaccess-Auth erlauben?
    "only_auth_users": True,

    # Zugriffe nur von bestimmten IP's zulassen
    "IP_range": ["127.0.0.1","192.168.*.*"],

    # Debugausgaben einblenden?
    #~ "debug": True,
    "debug": False,

    # Ab welcher Anzahl von Verzeichnissen sollen Buchstaben eingeblendet werden?
    "min_letters" : 12,

    "temp": None,

    #__________________________________
    # Upload
    "upload_bufsize"    : 8192,
    "upload_dir"        : "uploads",
}




# Standart Python Module
import os, sys, urllib, cgi
import posixpath, subprocess, stat, time, locale


#_____________________________________________________________________________
## Eigene Module

# SQL-Wrapper mit speziellen PyDown-DB-Zugriffsmethoden
from PyDownDB import PyDownDB

# Für das rendern von Templates per decorator
from TemplateDecoratorHandler import render

# Path-Klasse für das request-Objekt
from path import path

#_____________________________________________________________________________



# local explizit auf deutsch stellen (nur Linux!), für:
#  - den tausender-Punkt bei Bytes-Angaben
#  - die richtige sortierung mit locale.strcoll()
try:
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    #~ locale.setlocale(locale.LC_COLLATE, "german")
except:
    pass


filesystemencoding = sys.getfilesystemencoding()


# Colubrid import's werden das erste mal im Request-Handler vorgenommen und
# sind dort mit einem except und Info-Text versehen
from colubrid.exceptions import *
from colubrid import RegexApplication

import jinja



















class base(object):
    """ Basisklasse von der jede ObjApp-Klasse ableitet """
    def init2(self):
        """
        Das request-Object ist bei __init__ noch nicht verfügbar, deswegen
        muß von jeder App-Methode diese init2() ausgeführt werden.
        """
        self.db = self.request.db





class index(base):
    """
    Die eigentlichen Programmteile, die automatisch von der ObjectApplication
    Aufgerufen werden.
    """

    def info(self):
        """
        Informations-Seite anzeigen
        """
        self.init2() # Basisklasse einrichten

        self.db.log(type="view", item="infopage")

        self.request.echo("bandwith:", self.db.get_bandwith())
        self.request.echo("blocksize:", self.db.get_download_blocksize(0.1))

        # Information aus der DB sammeln
        self.context["current_downloads"] = self.db.human_readable_downloads()
        self.context["last_log"] = self.db.human_readable_last_log(20)

        self.context["bandwith"] = self.db.get_bandwith()

        if cfg["debug"]: self.request.debug_info()

        self.render("Infopage_base")


    def admin(self):
        """
        Admin-Formular ausweten und Preferences eintragen
        """
        self.init2() # Basisklasse einrichten

        if self.context["is_admin"] != True:
            raise AccessDenied("Only Admin can cange preferences!")

        if self.request.POST.has_key("bandwith"):
            bandwith = self.request.POST["bandwith"]
            self.db.set_bandwith(bandwith)

            self.db.log(type="admin", item="change bandwith to %s" % bandwith)

        # Information aus der DB sammeln
        self.context["current_downloads"] = self.db.human_readable_downloads()
        self.context["last_log"] = self.db.human_readable_last_log(20)

        self.context["bandwith"] = self.db.get_bandwith()

        if cfg["debug"]: self.request.debug_info()

        self.render("Infopage_base")









class PyDown(RegexApplication):
    """
    Klasse die die Programmlogik zusammenstellt
    """

    urls = [
        (r'^$', 'index'),
        (r'^browse/(.*?)$',     "PyDown.browse.index"),
        (r'^download/(.*?)$',   "PyDown.download.index"),
        (r'^upload/(.*?)$',     "PyDown.upload.index"),
        (r'^info/status/$',     "PyDown.info.status"),
        (r'^info/setup/$',      "PyDown.info.setup"),
    ]
    slash_append = True

    naviTABs = [
        { "url": "info/status",    "title": "info"},
        { "url": "browse/",        "title": "download"},
        { "url": "upload/",        "title": "upload"},
    ]

    def __init__(self, *args):
        super(PyDown, self).__init__(*args)
        self.request.headers['Content-Type'] = 'text/html'

        # Config-Dict an Request-Objekt und der Debugausgabe anhängen
        self.request.cfg = cfg
        self.request.expose_var("cfg")

        # Datenbankverbindung herstellen und dem request-Objekt anhängen
        self.setup_db()

    def index(self):
        raise HttpRedirect, ("browse/", 301)

    def setup_db(self):
        """
        Datenbankverbindung herstellen und dem request-Objekt anhängen
        """
        try:
            self.request.db = PyDownDB(
                self.request,
                dbtyp="sqlite",
                databasename="SQLiteDB/PyDownSQLite.db"
            )
        except Exception, e:
            raise Exception("%s\n --- Have you run install_DB.py first?" % e)

    def check_rights(self):
        """
        Überprüft only_https und only_auth_users
        """
        def check_ip(mask, IP):
            mask = mask.split(".")
            IP = IP.split(".")
            for mask_part, ip_part in zip(mask, IP):
                if mask_part != ip_part and mask_part != '*':
                    return False
            return True

        def check_ip_list(mask_list, IP):
            for mask in mask_list:
                if check_ip(mask, IP):
                    return True
            return False

        if self.request.cfg["IP_range"]:
            if not check_ip_list(self.request.cfg["IP_range"], self.request.environ["REMOTE_ADDR"]):
                raise AccessDenied("Permission denied!")

        if self.request.cfg["only_https"]:
            # Nur https Verbindungen "erlauben"
            if self.request.environ.get("HTTPS", False) != "on":
                raise AccessDenied("Only HTTPs connections allow!")

        if self.request.cfg["only_auth_users"]:
            # Der User muß über Apache's basic auth eingeloggt sein
            if not (self.request.environ.has_key("AUTH_TYPE") and \
            self.request.environ.has_key("REMOTE_USER")):
                raise AccessDenied("Only identified users allow!")
            if not self.request.environ["REMOTE_USER"] in self.request.cfg["allows_user"]:
                raise AccessDenied("Permission denied!")

        if not self.request.environ.has_key("REMOTE_USER"):
            self.request.environ["REMOTE_USER"] = "anonymous"



    def process_request(self):
        """
        Abarbeiten des eigentlichen Request. Die ObjectApplication ruft
        automatisch die eigentlichen Programmteile auf
        """
        self.check_rights() # Als erstes die Rechte checken!
        self.setup_naviTABs()
        self.setup_request_objects()
        self.setup_context()
        super(PyDown, self).process_request()


    def on_access_denied(self, args):
        """
        Überschreibt die original Ausgabe und ergänzt diese mit
        einem Hinweis, warum der Access Denied ist ;)
        """
        self.request.write("<h1>403 Forbidden</h1>")
        self.request.write("<h3>%s</h3>" % " ".join(args))

    def on_regular_close(self):
        self.request.debug_info()

    #_________________________________________________________________________
    # zusätzliche Request-Objekte

    def setup_naviTABs(self):
        """
        relative TAB-Links absolut machen
        """
        for link in self.naviTABs:
            link["url"] = posixpath.join(
                self.request.environ["SCRIPT_ROOT"], link["url"]
            )

    def setup_request_objects(self):
        """
        Hängt Objekte an das globale request-Objekt
        """
        # Jinja-Context anhängen
        self.request.context = {}
        self.request.expose_var("context")

        # jinja-Render-Methode anhängen
        self.request.render = self.render

        # Path-Klasse anhängen
        self.request.path = path(self.request)

    def setup_context(self):
        # ein paar Angaben
        self.request.context = {
            "naviTABs"          : self.naviTABs,
            "cfg"               : self.request.cfg,
            "__info__"          : __info__,
            "filesystemencoding": filesystemencoding,
            "username"          : self.request.environ["REMOTE_USER"],
            "is_admin"          : self.request.environ["REMOTE_USER"] in \
                self.request.cfg["admin_username"],
        }

        usernames = self.request.db.last_users()
        usernames = ",".join(usernames)
        self.request.context["serverInfo"] = {
            "bandwith"      : self.request.db.get_bandwith(),
            "downloadCount" : self.request.db.download_count(),
            "user"          : usernames,
        }


    def render(self, templatename):
        """
        Template mit jinja rendern, dabei wird self.request.context verwendet
        """
        #~ loader = jinja.FileSystemLoader('templates')
        loader = jinja.CachedFileSystemLoader('templates')

        template = jinja.Template(templatename, loader)
        context = jinja.Context(self.request.context)

        self.request.write(template.render(context))





# Middleware, die den Tag <script_duration /> ersetzt
from ReplacerMiddleware import replacer
app = replacer(PyDown)

