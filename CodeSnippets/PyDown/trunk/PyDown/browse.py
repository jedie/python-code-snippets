#!/usr/bin/python
# -*- coding: UTF-8 -*-

from utils import spezial_cmp

import os, sys, cgi, posixpath, locale, time, stat, subprocess
import dircache, tempfile, zipfile, glob, urllib

from colubrid import HttpResponse

reload(sys)
sys.setdefaultencoding("utf-8")

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding()


class FileIter(object):

    def __init__(self, request, fileObj, id, dbItemTxt):
        self._sleep_sec = 0.1

        self.db = request.db # Shorthand

        self._fileObj = fileObj
        self._id = id
        self._dbItemTxt = dbItemTxt

        self._current_bytes = 0
        self._last_time = time.time()
        self._blocksize = self.db.get_download_blocksize(self._sleep_sec)

    def __iter__(self):
        return self

    def next(self):
        data = self._fileObj.read(self._blocksize)
        if not data:
            self.db.log(type="download_end", item=self._dbItemTxt)
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
    def __init__(self, request, response, path):
        self.request = request
        self.response = response

        # Shorthands
        self.cfg        = self.request.cfg
        self.path       = self.request.path
        self.context    = self.request.context
        self.db         = self.request.db

        self.setup_path(path)

        self.clean_temp()

    def get(self):
        if self.pathFilename != None:
            return self.download()

        # "current path"-Links, oben in context einfÌ®•n
        self.request.context["path"] = self.path.path_links()

        # Verzeichnis-Daten lesen
        files, dirs = self.read_dir()
        #~ self.request.echo(files, dirs)

        #~ try:
        self.put_dir_info_to_context(files, dirs)
        #~ except Exception, e:
            #~ if self.cfg["debug"]:
                #~ self.response.write(
                    #~ "<small>(Error 'put_dir_info_to_context': %s)</small><br />" % e
                #~ )

        self.request.render("Browser_base")

    def setup_path(self, path):
        self.relativ_path, self.absolute_path, self.pathFilename = \
            self.path.prepare_path(path, u"browse")

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
        listPath = os.path.normpath(self.absolute_path)
        listPath = os.path.abspath(listPath)

        codec = self.request.context["filesystemencoding"]

        self.cfg["debug"] = True

        if self.cfg["debug"]:
            def get_file_encoding(f):
                if hasattr(f, "encoding"):
                    return f.encoding
                else:
                    return "not set"

            self.response.write("sys.stdin.encoding: %s<br/>" % get_file_encoding(sys.stdin))
            self.response.write("sys.stdout.encoding: %s<br/>" % get_file_encoding(sys.stdout))
            self.response.write("sys.stderr.encoding: %s<br/>" % get_file_encoding(sys.stderr))
            self.response.write("sys.getdefaultencoding(): %s<br/>" % sys.getdefaultencoding())
            self.response.write("sys.getfilesystemencoding(): %s<br/>" % sys.getfilesystemencoding())
            self.response.write("locale.getpreferredencoding(): %s<br/>" % locale.getpreferredencoding())

            self.response.write("stdout_encoding: %s<br/>" % stdout_encoding)

            try:
                listPath = unicode(listPath)
            except Exception, e:
                msg = "listPath Unicode-Error: %s" % e
                print msg
                self.response.write(
                    "<small>(%s)</small><br />" % msg
                )
            if not isinstance(listPath, unicode):
                self.response.write(
                        "<small>(Note: listPath is not unicode)</small><br />"
                    )

            self.response.write("listPath:")
            self.response.write(cgi.escape(str(type(listPath))))
            try:
                self.response.write("listPath: %s" % listPath.encode(stdout_encoding))
            except:
                pass
            self.response.write("<br>")

        dirList = os.listdir(listPath)
        for item in dirList:
            if not isinstance(item, unicode):
                try:
                    if codec == "mbcs": # f√ºr Windows
                        item = unicode(item, codec)
                except UnicodeError, e:
                    if self.cfg["debug"]:
                        self.response.write(
                            "<small>(Unicode-Error1: %s)</small><br />" % e
                        )
                    continue

            if self.cfg["debug"]:
                if not isinstance(item, unicode):
                    self.response.write("skip %s (not unicode)<br>" % item)
                    continue

            try:
                abs_path = posixpath.join(self.absolute_path, item)

                if os.path.isfile(abs_path):
                    ext = os.path.splitext(abs_path)[1]
                    if not ext in self.cfg["ext_whitelist"]:
                        continue
                    #~ self.request.echo("file: '%s' '%s'<br>" % (item, abs_path))
                    files.append((item, abs_path))

                elif os.path.isdir(abs_path):
                    #~ self.request.echo("dir: '%s' '%s'<br>" % (item, abs_path))
                    dirs.append((item, abs_path+"/"))

                elif self.cfg["debug"]:
                    self.response.write(
                        "<small>(Unknown dir item: '%s' %s)</small><br />" % (
                            abs_path, cgi.escape(str(type(abs_path)))
                        )
                    )
            except UnicodeError, e:
                if self.cfg["debug"]:
                    self.response.write(
                        "<small>(Unicode-Error 2: %s)</small><br />" % e
                    )

        files.sort(spezial_cmp)
        dirs.sort(spezial_cmp)
        return files, dirs

    def put_dir_info_to_context(self, files, dirs):

        # File-Informationen in context einf¸gen
        self.request.context["filelist"] = []
        totalBytes = 0
        for filename, abs_path in files:
            relativ_path = self.path.relative_path(abs_path)
            file_info = self._get_file_info(abs_path)
            file_info["url"] = filename
            file_info["name"] = filename
            totalBytes += file_info["size"]
            self.request.context["filelist"].append(file_info)

        # Informationen f√ºr Download-Link
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

            #~ print "item:", type(item)
            first_letter = item[0].upper()
            #~ try:
                #~ first_letter = item.decode("utf-8") # nach unicode wandeln
                #~ first_letter = first_letter[0].upper()
                #~ first_letter = first_letter.encode("utf-8") # zur√ºck konvertieren
            #~ except UnicodeError, e:
                #~ if self.cfg["debug"]:
                    #~ self.response.write(
                        #~ "<small>(Unicode-Error 'first_letter': %s)</small><br />" % e
                    #~ )
                #~ first_letter = "#"

            if not dirlist.has_key(first_letter):
                dirlist[first_letter] = []

            dirlist[first_letter].append({
                "url": url,
                "name": item,
            })

        # Verzeichnis-Informationen in context einf¸gen
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
    # Download-Methoden

    def download(self):
        """
        Ein Download wurde angefordert
        """
        self.simulation = self.request.args.get("simulation", False)

        if self.simulation:
            self.response.write("<h1>Download Simulation!</h1><pre>")
            self.response.write("relativ_path: '%s'\n" % self.relativ_path)
            self.response.write("absolute_path: '%s'\n" % self.absolute_path)
            self.response.write("pathFilename: '%s'\n" % self.pathFilename)
            log_typ = "download simulation start"
        else:
            log_typ = "download start"

        self.db.log(log_typ, self.relativ_path)

        if self.pathFilename.endswith(".zip"):
            # Alle Dateien im aktuellen Ordner als ZIP downloaden
            return self.download_full_dir()
        else:
            # Gezielt eine Datei Downloaden
            return self.download_file()


    def download_full_dir(self):
        """
        Alle Dateien in einem Ordner downloaden
        """
        self.clean_temp()

        files, _ = self.read_dir()

        tempFile = tempfile.NamedTemporaryFile(
            prefix = "%s%s_" % (
                    self.request.cfg["temp_prefix"], self.request.environ["REMOTE_USER"]
            ),
            dir = self.get_temp_dir(),
        )

        zipFile = zipfile.ZipFile(tempFile, "wb", zipfile.ZIP_STORED)

        if self.simulation:
            self.response.write("-"*80)
            self.response.write("\n")

        arcPath = self.relativ_path.split("/")
        arcPath = "/".join(arcPath[-2:])

        for file_info in files:
            filename = file_info[0]
            abs_path = posixpath.join(self.absolute_path, filename)
            arcname = posixpath.join(arcPath, filename)

            if self.simulation:
                #~ self.response.write("absolute path..: %s\n" % abs_path)
                self.response.write("<strong>%s</strong>\n" % arcname)

            try:
                zipFile.write(abs_path, arcname)
            except IOError, e:
                self.response.write("<h1>Error</h1><h2>Can't create archive: %s</h2>" % e)
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

        return self.send_file(tempFile, self.pathFilename, self.relativ_path)


    def download_file(self):
        """
        Download einer Datei
        """
        filePath = posixpath.join(self.absolute_path, self.pathFilename)

        try:
            f = file(filePath, "rb")
        except Exception, e:
            self.response.write("<h3>Can't open file: %s</h3>" % e)
            return

        return self.send_file(f, self.pathFilename, filePath)


    def send_file(self, fileObject, filename, dbItemTxt):
        """
        Sendet die Download-Daten zum Client
        """
        # Dateigr√∂√üe ermitteln
        fileObject.seek(0,2) # Am Ende der Daten springen
        fileObject_len = fileObject.tell() # Aktuelle Position
        fileObject.seek(0) # An den Anfang springen

        if self.simulation:
            self.response.write("-"*80)
            self.response.write("\n")
            self.response.write('Filename........: "%s"\n' % filename)
            self.response.write("Content-Length..: %sBytes\n" % fileObject_len)
            self.response.write("\n")

            readLen = 120
            self.response.write("First %s Bytes:\n" % readLen)
            self.response.write(
                "<hr />%s...<hr />" % cgi.escape(fileObject.read(readLen))
            )

            self.response.write("Duration: <script_duration />")
            self.db.log(type="simulation_end", item=self.relativ_path)
            self.response.write("</pre>")
            return

        id = self.db.insert_download(dbItemTxt, fileObject_len, 0)

        # force Windows input/output to binary
        if sys.platform == "win32":
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

        response = HttpResponse(
            FileIter(self.request, fileObject, id, self.relativ_path)
        )

        response.headers['Content-Disposition'] = \
            'attachment; filename="%s"' % filename
        response.headers['Content-Length'] = '%s' % fileObject_len
        response.headers['Content-Transfer-Encoding'] = '8bit' #'binary'
        response.headers['Content-Type'] = \
            'application/octet-stream;'# charset=utf-8'

        return response

    #_________________________________________________________________________

    def get_temp_dir(self):
        """
        Liefert das TEMP-Verz. entweder das in der Config angegebene
        oder das System-Temp-Verz.
        """
        if self.request.cfg["temp"]:
            return self.request.cfg["temp"]
        else:
            return tempfile.gettempdir()

    def clean_temp(self):
        """
        L√∂scht alte TEMP-Dateien
        """
        tempDir = self.get_temp_dir()
        globDir = os.path.join(tempDir, "%s*" % self.request.cfg["temp_prefix"])
        for filename in glob.glob(globDir):
            pathStat = os.stat(filename)
            lastAccess          = pathStat.st_atime
            if (time.time() - lastAccess) > self.request.cfg["temp_max_old"]:
                try:
                    os.remove(filename)
                except Exception, e:
                    self.db.log(
                        type="temp_autoclean",
                        item="Error: '%s'" % e
                    )
                else:
                    self.db.log(
                        type="temp_autoclean",
                        item="OK '%s' deleted" % filename
                    )









