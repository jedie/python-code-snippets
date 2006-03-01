#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyDown - A small Python Download Center...

Info zur Installation/Benutzung: PyDown_readme.txt
"""

# copyleft: jensdiemer.de (GPL v2 or above)

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License v2 or above - http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://pylucid.python-hosting.com/browser/CodeSnippets/"

__version__ = "v0.1.1"

__info__ = """<a href="%s">PyDown %s</a>""" % (__url__, __version__)

__history__ = """
v0.1.1
    - Bugfixes for running under Windows
v0.1
    - erste Version
"""



# Basis Config Einstellung
# Diese _nicht_ hier ändern, sondern in der ../PyDown_config.py!!!
cfg = {
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
import os, sys, zipfile, StringIO, urllib, cgi
import posixpath, subprocess, stat, time, locale


# Eigene Module
from database import SQL_wrapper




# Für den tausender-Punkt bei Bytes-Angaben (nur Linux!)
try:
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
    #~ locale.setlocale(locale.LC_COLLATE, "german")
except:
    pass


filesystemencoding = sys.getfilesystemencoding()


# Colubrid import's werden das erste mal im Request-Handler vorgenommen und
# sind dort mit einem except und Info-Text versehen
from colubrid import ObjectApplication
from colubrid.exceptions import *




# Jinja-Template-Engine
try:
    from jinja import Template, Context, FileSystemLoader
except ImportError, e:
    print "Content-type: text/plain; charset=utf-8\r\n"
    print "<h1>Jinja-Template-Engine, Import Error: %s</h1>" % s
    print "Download at: http://wsgiarea.pocoo.org/jinja/"
    import sys
    sys.exit()






# Import für ObjectApplication
import inspect
from colubrid.utils import ERROR_PAGE_TEMPLATE, splitpath, fix_slash
class ObjectApplication(ObjectApplication):
    """
        Tauschen von
        path_info = self.request.environ.get('PATH_INFO', '/')
        mit
        path_info = self.request.GET.get('action', '/')
    """

    def process_request(self):
        if not hasattr(self, 'root'):
            raise AttributeError, 'ObjectApplication requires a root object.'

        #~ path_info = self.request.environ.get('PATH_INFO', '/')
        path_info = self.request.GET.get('action', '/')
        self._process_request(path_info)

    def _process_request(self, path_info):
        path = splitpath(path_info)
        handler, handler_args = self._find_object(path)
        if not handler is None:
            args, vargs, kwargs, defaults = None, None, None, None
            try:
                args, varargs, kwargs, defaults = inspect.getargspec(handler)
                args = args[1:]
            except:
                pass
            if defaults is None:
                defaults = ()
            min_len = len(args) - len(defaults)
            max_len = len(args)
            handler_len = len(handler_args)

            if not hasattr(handler, 'container'):
                if not handler_args and max_len != 0:
                    handler.__dict__['container'] = True
                else:
                    handler.__dict__['container'] = False
            # now we call the redirect method
            # if it forces an redirect the __iter__ method skips the next
            # part. call it magic if you like -.-
            fix_slash(self.request, handler.container)

            if min_len <= handler_len <= max_len:
                parent = handler.im_class()
                parent.request = self.request
                return handler(parent, *handler_args)

        raise PageNotFound








def spezial_cmp(a,b):
    """ Sortiert alle mit "_" beginnenen items nach oben """
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
    def __init__(self):
        self.context = {
            "cfg": cfg,
            "__info__": __info__,
            "filesystemencoding": filesystemencoding,
        }

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
        self.log_path = posixpath.join(self.request.environ["DOCUMENT_ROOT"], "log")
        self.context["username"] = self.request.environ["REMOTE_USER"]

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
    def index(self):
        """
        Anzeigen des Browsers
        """
        self._setup_path()

        files, dirs = self._read_dir()
        self._put_dir_info_to_context(files, dirs)

        # Basis Template importiert selber das User-Template
        t = Template('PyDown/Browser_base', FileSystemLoader("."))
        c = Context(self.context)
        self.request.write(t.render(c))

        if cfg["debug"]:
            self.request.debug_info()

    def download(self):
        """
        Ein Download wird ausgeführt
        """
        simulation = self.request.POST.get("simulation", False)

        self._setup_path()
        if simulation:
            self.request.echo("<h1>Download Simulation!</h1><pre>")
            self.request.echo("request path: %s\n" % self.request_path)

        artist = self.request.POST.get("artist", "")
        album = self.request.POST.get("album", "")

        files, _ = self._read_dir()

        buffer = StringIO.StringIO()
        z = zipfile.ZipFile(buffer, "w")

        if simulation:
            #~ z.debug = 3
            #~ oldstdout = sys.stdout
            #~ sys.stdout = self.request
            #~ print "TEST"
            self.request.write("-"*80)
            self.request.write("\n")

        for file_info in files:
            filename = file_info[0]
            abs_path = posixpath.join(self.request_path, filename)
            arcname = posixpath.join(artist, album, filename)

            if simulation:
                #~ self.request.write("absolute path..: %s\n" % abs_path)
                self.request.write("<strong>%s</strong>\n" % arcname)

            z.write(abs_path, arcname)
        z.close()

        if simulation:
            #~ sys.stdout = oldstdout
            self.request.write("-"*80)
            self.request.write("\n")

        buffer.seek(0,2) # Am Ende der Daten springen
        buffer_len = buffer.tell() # Aktuelle Position
        buffer.seek(0) # An den Anfang springen

        filename = posixpath.split(self.request_path)[-1]

        if simulation:
            self.request.echo('Filename........: "%s.zip"\n' % filename)
            self.request.echo("Content-Length..: %sBytes\n" % buffer_len)
            self.request.echo("\n")

            l = 120
            self.request.echo("First %s Bytes:\n" % l)
            buffer = buffer.read(l)
            #~ buffer = buffer.encode("String_Escape")
            self.request.write("<hr />%s...<hr />" % cgi.escape(buffer))

            self.request.echo("Duration: <script_duration />")
            return

        self.request.headers['Content-Disposition'] = 'attachment; filename="%s.zip"' % filename
        self.request.headers['Content-Length'] = '%s' % buffer_len
        self.request.headers['Content-Transfer-Encoding'] = 'binary'
        self.request.headers['Content-Type'] = 'application/octet-stream;'# charset=utf-8'

        def send_data(buffer):
            while 1:
                data = buffer.read(2048)
                if not data:
                    return
                yield data
                time.sleep(0.1)

        self.request.send_response(send_data(buffer))



class PyDown(ObjectApplication):

    root = index

    def __init__(self, *args):
        super(PyDown, self).__init__(*args)
        self.request.headers['Content-Type'] = 'text/html'

        if not hasattr(self.request, "cfg"):
            self.request.cfg = cfg
            self.request.exposed.append("cfg")

        #~ db = SQL_wrapper(dbtyp="sqlite", databasename="PyDownSQLite")
        #~ self.request.db = db

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

    def process_request(self):
        self.check_rights() # Als erstes die Rechte checken!
        super(PyDown, self).process_request()

    def on_access_denied(self, args):
        self.request.write("<h1>403 Forbidden</h1>")
        self.request.write("<h3>%s</h3>" % " ".join(args))

    #~ def on_regular_close(self):
        #~ self.request.debug_info()




# Middleware, die den Tag <script_duration /> ersetzt
from ReplacerMiddleware import replacer
app = replacer(PyDown)

