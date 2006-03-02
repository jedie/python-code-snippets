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

__version__ = "v0.2"

__info__ = """<a href="%s">PyDown %s</a>""" % (__url__, __version__)

__history__ = """
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

    # Debugausgaben einblenden?
    #~ "debug": True,
    "debug": False,
}




# Standart Python Module
import os, sys, urllib, cgi
import posixpath, subprocess, stat, time, locale
from tempfile import NamedTemporaryFile
from tarfile import TarFile


#_____________________________________________________________________________
## Eigene Module

# SQL-Wrapper mit speziellen PyDown-DB-Zugriffsmethoden
from PyDownDB import PyDownDB

# Für das rendern von Templates per decorator
from TemplateDecoratorHandler import render

# ObjectApplication basierend auf cgi-GET-Parameter
from cgi_GET_ObjectApplication import ObjectApplication
#_____________________________________________________________________________



# Für den tausender-Punkt bei Bytes-Angaben (nur Linux!)
try:
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    #~ locale.setlocale(locale.LC_COLLATE, "german")
except:
    pass


filesystemencoding = sys.getfilesystemencoding()


# Colubrid import's werden das erste mal im Request-Handler vorgenommen und
# sind dort mit einem except und Info-Text versehen
from colubrid.exceptions import *









def spezial_cmp(a,b):
    """
    Abgewandelte Form für sort()
    Sortiert alle mit "_" beginnenen items nach oben
    """
    x = a[0][0] == "_" # x ist True wenn erste Buchstabe ein "_" ist
    y = b[0][0] == "_"
    if x and y: return 0
    if x: return -1
    if y: return 1
    # strcoll -> Damit auch äöü richtig einsortiert werden
    return locale.strcoll(a[0],b[0])
    #~ return cmp(a,b)



















class base(object):
    """ Basisklasse von der jede ObjApp-Klasse ableitet """
    #~ def __init__(self):


    def init2(self):
        """
        Das request-Object ist bei __init__ noch nicht verfügbar, deswegen
        muß von jeder App-Methode diese init2() ausgeführt werden.
        """
        self.context = {
            "cfg": self.request.cfg,
            "__info__": __info__,
            "filesystemencoding": filesystemencoding,
            "username": self.request.environ["REMOTE_USER"],
            "is_admin": self.request.environ["REMOTE_USER"] in self.request.cfg["admin_username"],
        }
        self.db = self.request.db

    def _read_dir(self):
        "Einlesen des Verzeichnisses"
        files = []
        dirs = []
        for item in os.listdir(self.request_path):
            abs_path = posixpath.join(self.request_path, item)
            if os.path.isfile(abs_path):
                ext = os.path.splitext(abs_path)[1]
                if not ext in cfg["ext_whitelist"]:
                    continue
                files.append((item, abs_path))

            elif os.path.isdir(abs_path):
                #~ self.request.echo("#%s#%s#<br>" % (item, abs_path))
                dirs.append((item, abs_path))

        files.sort()
        dirs.sort(spezial_cmp)
        return files, dirs

    def _put_dir_info_to_context(self, files, dirs):

        self._put_path_to_context(self.raw_path_info)

        # File-Informationen in context einfügen
        self.context["filelist"] = []
        for filename, abs_path in files:
            file_info = {"name": filename}
            file_info.update(self._get_file_info(abs_path))
            self.context["filelist"].append(file_info)

        # Informationen für Download-Link
        if len(files)>0:
            url = self._get_url(self.request_path)
            path_info = self.request_path.split("/")
            self.context["download"] = {
                "url": url,
                "artist": path_info[-2],
                "album": path_info[-1],
            }

        # Verzeichnis-Informationen in context einfügen
        #~ self.context["dirlist"] = {}
        #~ for item, abs_path in dirs:
            #~ url = self._get_url(abs_path)
            #~ relativ_path = self._get_relative_path(abs_path)

            #~ first_letter = item[0]
            #~ if not self.context["dirlist"].has_key(first_letter):
                #~ self.context["dirlist"][first_letter] = []

            #~ self.context["dirlist"][first_letter] .append({
                #~ "url": url,
                #~ "name": item,
            #~ })

        dirlist = {}
        for item, abs_path in dirs:
            url = self._get_url(abs_path)
            relativ_path = self._get_relative_path(abs_path)

            first_letter = item[0]
            if not dirlist.has_key(first_letter):
                dirlist[first_letter] = []

            dirlist[first_letter] .append({
                "url": url,
                "name": item,
            })

        self.context["dirlist"] = []
        for letter, items in dirlist.iteritems():
            temp = []
            for item in items:
                temp.append(item)

            self.context["dirlist"].append({
                "letter": letter,
                "items": temp,
            })

    def _get_stat(self, abs_path):
        result = {}
        item_stat = os.stat(abs_path)
        result["mtime"] = time.strftime(
            '%d.%m.%Y %H:%M',
            time.localtime(item_stat[stat.ST_MTIME])
        )

        if os.path.isfile(abs_path):
            size = item_stat[stat.ST_SIZE]/1024.0
            try:
                result["size"] = "%s KB" % locale.format("%0.1f", size, True)
            except:
                result["size"] = "%0.1f KB" % size

        return result

    def _get_file_info(self, filename):
        """ Datei Information mit Linux 'file' Befehl zusammentragen """
        result = {}

        result.update(self._get_stat(filename))

        if sys.platform == "win32":
            # Unter Windows gibt es keinen File-Befehl
            result["info"] = ""
            return result

        try:
            proc = subprocess.Popen(
                args        = ["file", filename],
                stdout      = subprocess.PIPE,
                stderr      = subprocess.PIPE
            )
        except Exception, e:
            result["info"] = "Can't make file subprocess: %s" % e
            return result

        try:
            result["info"] = proc.stdout.read()
        except Exception, e:
            result["info"] = "Can't read stdout from subprocess: %s" % e
            return result

        proc.stdout.close()

        try:
            result["info"] = result["info"].split(":",1)[1].strip()
        except Exception, e:
            result["info"] = "Can't prepare String: '%s' Error: %s" % (file_info, e)
            return result

        return result

    def _put_path_to_context(self, path):
        self.context["path"] = ""

        if path == "/":
            # Wir sind im "root"-Verzeichnis
            self.context["path"] = "/"
            return

        if path[:1] == "/": path = path[:-1] # / Am Ende wegschneiden
        path = path[1:] # / Am Anfang wegschneiden

        # zurück hinzufügen
        self.context["path"] += '[<a href="%s">root</a>]' % \
            self.request.environ["SCRIPT_ROOT"]

        path = path.split("/")
        lastitem = path[-1:][0]
        path = path[:-1]

        #~ self.request.echo(path)
        url_part = ""
        for item in path:
            if url_part != "":
                url_part += "/" + item
            else:
                url_part = item
            url = posixpath.join(
                self.request.environ["SCRIPT_ROOT"], url_part
            )
            self.context["path"] += '/<a href="%s">%s</a>' % (url, item)

        self.context["path"] += "/%s" % lastitem

    def _get_url(self, path):
        path = self._get_relative_path(path)
        path = posixpath.join(self.request.environ["SCRIPT_ROOT"], path)
        #~ self.request.echo("2#%s#%s#<br>" % (self.request.environ["SCRIPT_ROOT"], path))
        return urllib.quote(path)

    def _get_relative_path(self, path):
        if not path.startswith(cfg["base_path"]):
            return path
        relative_path = path.lstrip(cfg["base_path"])
        #~ self.request.echo(
            #~ "#%s#%s#%s#<br>" % (path, cfg["base_path"], relative_path)
        #~ )
        return relative_path

    def _setup_path(self):
        self.raw_path_info = self.request.environ.get('PATH_INFO', '')
        self.request_path = "%s%s" % (cfg["base_path"], self.raw_path_info)

        self._check_absolute_path(self.request_path)

        self.request_path = posixpath.normpath(self.request_path)
        self.context["request_path"] = self.request_path


    def _check_absolute_path(self, absolute_path):
        """
        Überprüft einen absoluten Pfad
        """
        if (absolute_path.find("..") != -1):
            # Hackerscheiß schon mal ausschließen
            raise AccessDenied("not allowed!")

        if not absolute_path.startswith(cfg["base_path"]):
            # Fängt nicht wie Basis-Pfad an... Da stimmt was nicht
            raise AccessDenied("permission deny #%s#%s#" % (
                absolute_path, cfg["base_path"])
            )
            raise AccessDenied("permission deny.")

        if not os.path.exists(absolute_path):
            # Den Pfad gibt es nicht
            raise AccessDenied("'%s' not exists" % absolute_path)







class index(base):
    """
    Die eigentlichen Programmteile, die automatisch von der ObjectApplication
    Aufgerufen werden.
    """

    @render('Browser_base') # return wird durch TemplateEngine gerendert
    def index(self):
        """
        Anzeigen des Browsers
        """
        self.init2() # Basisklasse einrichten
        self._setup_path()

        files, dirs = self._read_dir()
        self._put_dir_info_to_context(files, dirs)

        if self.context['filelist'] != []:
            # Nur in log schreiben, wenn überhaupt Dateien vorhanden sind
            self.db.log(type="browse", item=self.context['request_path'])

        if cfg["debug"]: self.request.debug_info()

        return self.context


    @render('Infopage_base') # return wird durch TemplateEngine gerendert
    def info(self):
        """
        Informations-Seite anzeigen
        """
        self.init2() # Basisklasse einrichten

        self.db.log(type="view", item="infopage")

        # Information aus der DB sammeln
        self.context["current_downloads"] = self.db.human_readable_downloads()
        self.context["last_log"] = self.db.human_readable_last_log(20)

        self.context["bandwith"] = self.db.get_bandwith()

        if cfg["debug"]: self.request.debug_info()

        return self.context


    @render('Infopage_base') # return wird durch TemplateEngine gerendert
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

        return self.context


    def download(self):
        """
        Ein Download wird ausgeführt
        """
        self.init2() # Basisklasse einrichten

        simulation = self.request.POST.get("simulation", False)

        self._setup_path()
        if simulation:
            self.request.echo("<h1>Download Simulation!</h1><pre>")
            self.request.echo("request path: %s\n" % self.request_path)
            log_typ = "download simulation start"
        else:
            log_typ = "download start"

        self.db.log(log_typ, self.context['request_path'])

        artist = self.request.POST.get("artist", "")
        album = self.request.POST.get("album", "")

        files, _ = self._read_dir()

        temp = NamedTemporaryFile(prefix="PyDown_%s_" % self.request.environ["REMOTE_USER"])
        tar = TarFile(mode="w", fileobj=temp)

        if simulation:
            self.request.write("-"*80)
            self.request.write("\n")

        for file_info in files:
            filename = file_info[0]
            abs_path = posixpath.join(self.request_path, filename)
            arcname = posixpath.join(artist, album, filename)

            if simulation:
                #~ self.request.write("absolute path..: %s\n" % abs_path)
                self.request.write("<strong>%s</strong>\n" % arcname)

            tar.add(abs_path, arcname)
        tar.close()

        if simulation:
            self.request.write("-"*80)
            self.request.write("\n")

        temp.seek(0,2) # Am Ende der Daten springen
        temp_len = temp.tell() # Aktuelle Position
        temp.seek(0) # An den Anfang springen

        filename = posixpath.split(self.request_path)[-1]

        if simulation:
            self.request.echo('Filename........: "%s.zip"\n' % filename)
            self.request.echo("Content-Length..: %sBytes\n" % temp_len)
            self.request.echo("\n")

            l = 120
            self.request.echo("First %s Bytes:\n" % l)
            temp = temp.read(l)
            #~ buffer = buffer.encode("String_Escape")
            self.request.write("<hr />%s...<hr />" % cgi.escape(temp))

            self.request.echo("Duration: <script_duration />")
            self.log(type="simulation_end", item=self.context['request_path'])
            return

        id = self.db.insert_download(self.context['request_path'], temp_len, 0)

        self.request.headers['Content-Disposition'] = 'attachment; filename="%s.tar"' % filename
        self.request.headers['Content-Length'] = '%s' % temp_len
        #~ self.request.headers['Content-Transfer-Encoding'] = 'binary'
        self.request.headers['Content-Transfer-Encoding'] = '8bit'
        self.request.headers['Content-Type'] = 'application/octet-stream;'# charset=utf-8'

        def send_data(id, temp):
            current_bytes = 0
            last_time = time.time()
            while 1:
                data = temp.read(2048)
                if not data:
                    return
                yield data
                current_bytes += len(data)

                current_time = time.time()
                if current_time-last_time>5.0:
                    last_time = current_time
                    self.db.update_download(id, current_bytes)
                time.sleep(0.05)

            temp.close()

            self.db.update_download(id, current_bytes)

        self.request.send_response(send_data(id, temp))

        self.db.log(type="download_end", item=self.context['request_path'])

#1-100



class PyDown(ObjectApplication):
    """
    Klasse die die Programmlogik zusammenstellt
    """

    root = index

    def __init__(self, *args):
        super(PyDown, self).__init__(*args)
        self.request.headers['Content-Type'] = 'text/html'

        # Config-Dict an Request-Objekt und der Debugausgabe anhängen
        self.request.cfg = cfg
        self.request.expose_var("cfg")

        # Datenbankverbindung herstellen und dem request-Objekt anhängen
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

    def process_request(self):
        """
        Abarbeiten des eigentlichen Request. Die ObjectApplication ruft
        automatisch die eigentlichen Programmteile auf
        """
        self.check_rights() # Als erstes die Rechte checken!
        super(PyDown, self).process_request()

    def on_access_denied(self, args):
        """
        Überschreibt die original Ausgabe und ergänzt diese mit
        einem Hinweis, warum der Access Denied ist ;)
        """
        self.request.write("<h1>403 Forbidden</h1>")
        self.request.write("<h3>%s</h3>" % " ".join(args))

    #~ def on_regular_close(self):
        #~ self.request.debug_info()




# Middleware, die den Tag <script_duration /> ersetzt
from ReplacerMiddleware import replacer
app = replacer(PyDown)

