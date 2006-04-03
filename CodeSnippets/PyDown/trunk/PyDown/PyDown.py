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

__version__ = "v0.4.3"

__info__ = """<a href="%s">PyDown %s</a>""" % (__url__, __version__)

__history__ = """
v0.4.3
    - NEU: eMail Benachrichtigung beim Upload
v0.4.2
    - NEU: Temp-Verz. wird aufgeräumt
v0.4.1
    - Anpassungen an colubrid 1.0
v0.4.0
    - NEU: upload
    - NEU: Download von einzelnen Dateien möglich
    - NEU: filesystemencoding
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
    "debug": False,

    # Ab welcher Anzahl von Verzeichnissen sollen Buchstaben eingeblendet werden?
    "min_letters" : 12,

    # Anzahl der Log-Einträge die angezeigt werden sollen
    "last_log_count": 50,

    # Temp-Verz., bei None, wird das System-Temp-Verz. genommen
    "temp": None,
    "temp_prefix": "PyDown_",
    # Max. alter einer Temp-Datei in Sec. bevor sie automatisch gelöscht wird
    "temp_max_old": 60,

    #__________________________________
    # Upload
    "upload_bufsize"        : 8192,
    "upload_dir"            : "uploads",
    # Soll nach dem Upload eine eMail verschickt werden?
    "upload_email_notify"   : False,
    # Die Absender-Adresse
    "email_from"           : "pydown@localhost",
    # Die Ziel-Adresse
    "upload_to"             : "administator@localhost",

}




# Standart Python Module
import os, sys, urllib, cgi
import posixpath, subprocess, stat, time, locale

# Leitet alle print Ausgaben an stderr weiter
sys.stdout = sys.stderr

#_____________________________________________________________________________
## Eigene Module

# Eigene Ausnahmen
from exceptions import *

# SQL-Wrapper mit speziellen PyDown-DB-Zugriffsmethoden
from PyDownDB import PyDownDB

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
#~ sys.setdefaultencoding("utf-8")



# Colubrid import's werden das erste mal im Request-Handler vorgenommen und
# sind dort mit einem except und Info-Text versehen
from colubrid import BaseApplication
from colubrid import HttpResponse

# Der key im environ-Dict mit dem das request-Object eingefügt ist
requestObjectKey = "colubrid.request"


# Jinja Template engine
import jinja

"""
##~ request.GET -> request.args
##~ request.REQUEST -> request.values
##~ request.POST -> request.form
##~ request.FILES -> request.files
##~ request.COOKIES -> request.cookies

http://trac.pocoo.org/browser/colubrid/webpage/documentation/applications/regex.txt
http://trac.pocoo.org/browser/colubrid/webpage/documentation/request.txt
http://trac.pocoo.org/browser/colubrid/webpage/documentation/response.txt
"""



class PyDown(BaseApplication):
    """
    Klasse die die Programmlogik zusammenstellt
    """
    charset = 'utf-8'

    urls = [
        (r'^$', 'index'),
        (r'^browse/(.*?)$',     "PyDown.browse.index"),
        (r'^download/(.*?)$',   "PyDown.download.index"),
        (r'^upload/(.*?)$',     "PyDown.upload.index"),
        (r'^info/status/$',     "PyDown.info.status"),
        #~ (r'^info/setup/$',      "PyDown.info.setup"),
    ]
    slash_append = True

    naviTABs = [
        { "url": "info/status",    "title": "info"},
        { "url": "browse/",        "title": "download"},
        { "url": "upload/",        "title": "upload"},
    ]

    def __init__(self, *args):
        super(PyDown, self).__init__(*args)
        self.response = HttpResponse()

        # Config-Dict an Request-Objekt und der Debugausgabe anhängen
        self.request.cfg = cfg

        # Datenbankverbindung herstellen und dem request-Objekt anhängen
        self.setup_db()

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
                raise PermissionDenied("Permission denied!")

        if self.request.cfg["only_https"]:
            # Nur https Verbindungen "erlauben"
            if self.request.environ.get("HTTPS", False) != "on":
                raise PermissionDenied("Only HTTPs connections allow!")

        if self.request.cfg["only_auth_users"]:
            # Der User muß über Apache's basic auth eingeloggt sein
            if not (self.request.environ.has_key("AUTH_TYPE") and \
            self.request.environ.has_key("REMOTE_USER")):
                raise PermissionDenied("Only identified users allow!")
            if not self.request.environ["REMOTE_USER"] in self.request.cfg["allows_user"]:
                raise PermissionDenied("Permission denied!")
                #~ raise PermissionDenied(
                    #~ "Permission denied: %s - %s " % (
                        #~ self.request.environ["REMOTE_USER"],
                        #~ self.request.cfg["allows_user"]
                    #~ )
                #~ )

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

        pathInfo = self.request.environ.get('PATH_INFO', '/')
        if pathInfo in ("", "/"):
            # Weiterleitung zum browser
            url = posixpath.join(self.request.environ['APPLICATION_REQUEST'], "browse")
            self.response.write("<h1>PathInfo: '%s'</h1>" % pathInfo)
            self.response.write("<h1>url: '%s'</h1>" % url)
            raise HttpMoved(url)

        elif pathInfo.startswith("/info"):
            # Informations-Seite
            import info
            info.info(self.request, self.response)

        elif pathInfo.startswith("/browse"):
            # Browser/Download
            path = pathInfo.lstrip("/browse")
            import browse
            FileIter = browse.browser(self.request, self.response, path).get()
            if FileIter != None:
                return FileIter

        elif pathInfo.startswith("/upload/status"):
            from upload import UploadStatus
            UploadStatus(self.request, self.response)

        elif pathInfo.startswith("/upload"):
            import upload
            upload.Uploader(self.request, self.response)

        else:
            self.response.write("<h1>PathInfo: '%s'</h1>" % pathInfo)

        return self.response

    #~ def on_regular_close(self):
    def close(self):
        if hasattr(self.request, 'downloadFileObj'):
            self.request.downloadFileObj.close()

    def on_access_denied(self, args):
        """
        Überschreibt die original Ausgabe und ergänzt diese mit
        einem Hinweis, warum der Access Denied ist ;)
        """
        self.response.write("<h1>403 Forbidden</h1>")
        self.response.write("<h3>%s</h3>" % " ".join(args))

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

        # jinja-Render-Methode anhängen
        self.request.jinja = self.jinja
        self.request.render = self.render

        # Path-Klasse anhängen
        self.request.path = path(self.request, self.response)

    def setup_context(self):
        # ein paar Angaben
        self.request.context = {
            "naviTABs"          : self.naviTABs,
            "cfg"               : self.request.cfg,
            "__info__"          : __info__,
            "filesystemencoding": sys.getfilesystemencoding(),
            "username"          : self.request.environ["REMOTE_USER"],
            "is_admin"          : self.request.environ["REMOTE_USER"] in \
                self.request.cfg["admin_username"],
        }

        usernames = self.request.db.last_users()
        usernames = ",".join(usernames)
        self.request.context["serverInfo"] = {
            "totalBandwith"     : int(round(self.request.db.get_bandwith())),
            "availableBandwith" : int(round(self.request.db.available_bandwith())),
            "downloadCount"     : self.request.db.download_count(),
            "uploadCount"     : self.request.db.upload_count(),
            "user"              : usernames,
        }

    #_________________________________________________________________________

    def jinja(self, templatename, context, suffix=".html"):
        #~ try:
            #~ loader = jinja.CachedFileSystemLoader('templates', suffix=suffix, charset='utf-8')
            #~ template = jinja.Template(templatename, loader)
        #~ except:# EOFError, ImportError:
            #~ self.response.write("<small>(jinja FileSystemLoader fallback)</small>")
        loader = jinja.FileSystemLoader('templates', suffix=suffix, charset='utf-8')
        template = jinja.Template(templatename, loader)

        context = jinja.Context(context, charset='utf-8')

        content = template.render(context)
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        else:
            self.response.write("<small>(Content not unicode)</small><br />")

        return content

    def render(self, templatename):
        """
        Template mit jinja rendern, dabei wird self.request.context verwendet
        """
        if cfg["debug"]:
            self.response.write("<small>Debug: ON</small><br />")

        content = self.jinja(templatename, self.request.context)
        self.response.write(content)


class UploadCallback:

    def __init__(self, request, environ, filename):
        self.request = request
        self.environ = environ
        self.filename = filename

        self.db = request.db

        #~ print "init", filename

    def start(self, contentLength):
        #~ print "Start", contentLength
        self.id = self.db.insert_upload(
            self.filename, contentLength, current_bytes=0
        )

    def update(self, pos):
        self.db.update_upload(self.id, pos)
        #~ print "pos:", pos

    def finished(self):
        #~ self.db.update_upload(self.id, pos)
        #~ print "finished", self.filename
        pass


app = PyDown


# Middleware, die den Tag <script_duration /> ersetzt
from ReplacerMiddleware import replacer
app = replacer(app)

# callback Funktion für Uploads
from uploadMiddleware import ProgressMiddleware
app = ProgressMiddleware(
    app, UploadCallback, requestObjectKey, threshold=512*1024
)

