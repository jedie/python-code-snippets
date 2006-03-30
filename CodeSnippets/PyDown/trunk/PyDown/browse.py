#!/usr/bin/python
# -*- coding: UTF-8 -*-

from utils import spezial_cmp

import os, sys, cgi, posixpath, locale, time, stat, subprocess
from tempfile import NamedTemporaryFile
import zipfile





class FileIter(object):

    def __init__(self, request, id):
        self._sleep_sec = 0.1

        self.db = request.db # Shorthand

        self._fileObj = request.downloadFileObj
        self._id = id

        self._current_bytes = 0
        self._last_time = time.time()
        self._blocksize = self.db.get_download_blocksize(self._sleep_sec)

    def __iter__(self):
        return self

    def next(self):
        data = self._fileObj.read(self._blocksize)
        if not data:
            raise StopIteration

        self._current_bytes += len(data)

        current_time = time.time()
        if current_time-self._last_time>5.0:
            self._last_time = current_time
            self.db.update_download(self._id, self._current_bytes)
            self._blocksize = self.db.get_download_blocksize(self._sleep_sec)

        time.sleep(self._sleep_sec)

        return data

    def close(self):
        if hasattr(self._fileObj, 'close'):
            self._fileObj.close()




class browser:
    def __init__(self, request, path):
        self.request = request

        # Shorthands
        self.cfg        = self.request.cfg
        self.path       = self.request.path
        self.context    = self.request.context
        self.db         = self.request.db

        self.setup_path(path)

        if self.pathFilename != None:
            self.download()
            return

        # "current path"-Links, oben in context einfügen
        self.request.context["path"] = self.path.path_links()

        # Verzeichnis-Daten lesen
        files, dirs = self.read_dir()
        #~ self.request.echo(files, dirs)

        self.put_dir_info_to_context(files, dirs)

        self.request.render("Browser_base")

    def setup_path(self, path):
        self.relativ_path, self.absolute_path, self.pathFilename = \
            self.path.prepare_path(path, "browse")

    def get_link(self, path):
        """
        Aus relativen Links, absolute machen
        """
        path = posixpath.join(self.request.environ["SCRIPT_ROOT"], path)
        return path

    def read_dir(self):
        "Einlesen des Verzeichnisses"
        files = []
        dirs = []
        for item in os.listdir(self.absolute_path):
            abs_path = posixpath.join(self.absolute_path, item)
            if os.path.isfile(abs_path):
                ext = os.path.splitext(abs_path)[1]
                if not ext in self.cfg["ext_whitelist"]:
                    continue
                #~ self.request.echo("file: '%s' '%s'<br>" % (item, abs_path))
                files.append((item, abs_path))

            elif os.path.isdir(abs_path):
                #~ self.request.echo("dir: '%s' '%s'<br>" % (item, abs_path))
                dirs.append((item, abs_path))

        files.sort(spezial_cmp)
        dirs.sort(spezial_cmp)
        return files, dirs

    def put_dir_info_to_context(self, files, dirs):

        # File-Informationen in context einfügen
        self.request.context["filelist"] = []
        totalBytes = 0
        for filename, abs_path in files:
            relativ_path = self.path.relative_path(abs_path)
            file_info = self._get_file_info(abs_path)
            file_info["name"] = filename
            totalBytes += file_info["size"]
            self.request.context["filelist"].append(file_info)

        # Informationen fÃ¼r Download-Link
        if len(files)>0:
            url = self.path.url(self.relativ_path)
            path_info = self.relativ_path.rstrip("/")
            path_info = path_info.split("/")
            downloadLink = "%s.zip" % path_info[-1]

            self.request.context["downloadLink"] = {
                "url": downloadLink,
                "size": totalBytes,
            }

        # Verzeichnis-Informationen in ein dict packen, welches
        # als Key, den ersten Buchstaben hat
        dirlist = {}
        for item, abs_path in dirs:
            url = self.path.url(abs_path)
            relativ_path = self.path.relative_path(abs_path)

            first_letter = item[0].upper()
            if not dirlist.has_key(first_letter):
                dirlist[first_letter] = []

            dirlist[first_letter].append({
                "url": url,
                "name": item,
            })

        # Verzeichnis-Informationen in context einfügen
        self.request.context["dirlist"] = []
        keys = dirlist.keys()
        keys.sort(spezial_cmp)
        for letter in keys:
            temp = []
            for item in dirlist[letter]:
                temp.append(item)

            self.request.context["dirlist"].append({
                "letter": letter,
                "items": temp,
            })

        self.context["show_letters"] = len(dirlist)>self.cfg["min_letters"]

    def _get_stat(self, abs_path):
        result = {}
        item_stat = os.stat(abs_path)
        result["mtime"] = time.strftime(
            '%d.%m.%Y %H:%M',
            time.localtime(item_stat[stat.ST_MTIME])
        )

        if os.path.isfile(abs_path):
            result["size"] = item_stat[stat.ST_SIZE]

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


    #_________________________________________________________________________

    def download(self):
        """
        Ein Download wurde angefordert
        """
        self.simulation = self.request.GET.get("simulation", False)

        if self.simulation:
            self.request.echo("<h1>Download Simulation!</h1><pre>")
            self.request.echo("relativ_path: '%s'\n" % self.relativ_path)
            self.request.echo("absolute_path: '%s'\n" % self.absolute_path)
            self.request.echo("pathFilename: '%s'\n" % self.pathFilename)
            log_typ = "download simulation start"
        else:
            log_typ = "download start"

        self.db.log(log_typ, self.relativ_path)

        if self.pathFilename.endswith(".zip"):
            # Alle Dateien im aktuellen Ordner als ZIP downloaden
            self.download_full_dir()
        else:
            # Gezielt eine Datei Downloaden
            self.download_file()


    def download_full_dir(self):
        """
        Alle Dateien in einem Ordner downloaden
        """
        files, _ = self.read_dir()

        args = {"prefix": "PyDown_%s_" % self.request.environ["REMOTE_USER"]}
        if self.request.cfg["temp"]:
            args["dir"] = self.request.cfg["temp"]
        tempFile = NamedTemporaryFile(**args)

        zipFile = zipfile.ZipFile(tempFile, "wb", zipfile.ZIP_STORED)

        if self.simulation:
            self.request.write("-"*80)
            self.request.write("\n")

        arcPath = self.relativ_path.split("/")
        arcPath = "/".join(arcPath[-2:])

        for file_info in files:
            filename = file_info[0]
            abs_path = posixpath.join(self.absolute_path, filename)
            arcname = posixpath.join(arcPath, filename)

            if self.simulation:
                #~ self.request.write("absolute path..: %s\n" % abs_path)
                self.request.write("<strong>%s</strong>\n" % arcname)

            try:
                zipFile.write(abs_path, arcname)
            except IOError, e:
                self.request.write("<h1>Error</h1><h2>Can't create archive: %s</h2>" % e)
                try:
                    zipFile.close()
                except:
                    pass
                try:
                    temp.close()
                except:
                    pass
                return
        zipFile.close()

        self.send_file(tempFile, self.pathFilename, self.relativ_path)


    def download_file(self):
        """
        Download einer Datei
        """
        filePath = posixpath.join(self.absolute_path, self.pathFilename)

        try:
            f = file(filePath, "rb")
        except Exception, e:
            self.request.write("<h3>Can't open file: %s</h3>" % e)
            return

        self.send_file(f, self.pathFilename, filePath)


    def send_file(self, fileObject, filename, dbItemTxt):
        """
        Sendet die Download-Daten zum Client
        """
        # DateigrÃ¶ÃŸe ermitteln
        fileObject.seek(0,2) # Am Ende der Daten springen
        fileObject_len = fileObject.tell() # Aktuelle Position
        fileObject.seek(0) # An den Anfang springen

        if self.simulation:
            self.request.write("-"*80)
            self.request.write("\n")
            self.request.echo('Filename........: "%s"\n' % filename)
            self.request.echo("Content-Length..: %sBytes\n" % fileObject_len)
            self.request.echo("\n")

            readLen = 120
            self.request.echo("First %s Bytes:\n" % readLen)
            self.request.write(
                "<hr />%s...<hr />" % cgi.escape(fileObject.read(readLen))
            )

            self.request.echo("Duration: <script_duration />")
            self.db.log(type="simulation_end", item=self.relativ_path)
            self.request.write("</pre>")
            return

        id = self.db.insert_download(dbItemTxt, fileObject_len, 0)

        # force Windows input/output to binary
        if sys.platform == "win32":
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        self.request.headers['Content-Disposition'] = \
            'attachment; filename="%s"' % filename
        self.request.headers['Content-Length'] = '%s' % fileObject_len
        self.request.headers['Content-Transfer-Encoding'] = '8bit' #'binary'
        self.request.headers['Content-Type'] = \
            'application/octet-stream;'# charset=utf-8'

        self.db.clean_up_downloads() # Alte Downloads in DB lÃ¶schen

        self.request.downloadFileObj = fileObject

        self.request.send_response(
            FileIter(self.request, id)
        )

        self.db.log(type="download_end", item=dbItemTxt)




def index(request, path):
    #~ request.write("JO")
    browser(request, path)
