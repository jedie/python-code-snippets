#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Eigene Ausnahmen
from exceptions import *

import os, sys, locale, posixpath, urllib, copy, cgi

stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding()


class path:
    def __init__(self, request, response):
        self.request = request
        self.response = response

        # Shorthands
        self.cfg = self.request.cfg
        self.environ = self.request.environ

        self.pathFilename = None
        self.relativ_path = None
        self.absolute_path = None

    def prepare_path(self, path, prefix=""):
        """
        jau
        """
        self.url_prefix = prefix

        self.relativ_path = path
        if self.relativ_path == "":
            self.relativ_path = u"/"
        elif self.relativ_path[0]!="/":
            self.relativ_path = "/%s" % self.relativ_path

        if not self.relativ_path.endswith("/"):
            # Verzeichnisse enden immer mit einem slash, Dateien nie
            possibleExt = list(self.cfg["ext_whitelist"])
            possibleExt.append(".zip")

            base, filename = posixpath.split(self.relativ_path)
            _, ext = posixpath.splitext(filename)
            #~ raise "base:'%s' filename:'%s' ext:'%s'" % (base, filename, ext)

            if ext != "" and ext in possibleExt:
                self.relativ_path = base
                self.pathFilename = filename

        self.absolute_path = "%s%s" % (self.cfg["base_path"], self.relativ_path)
        #~ raise "relativ_path:'%s' pathFilename:'%s' absolute_path:'%s'" % (
            #~ self.relativ_path, self.pathFilename, self.absolute_path
        #~ )

        self.check_absolute_path()

        self.absolute_path = posixpath.normpath(self.absolute_path)

        return self.relativ_path, self.absolute_path, self.pathFilename

    def url(self, path):
        #~ self.response.write("<p>path.url: %s<br>" % path)
        #~ self.response.write("SCRIPT_ROOT:%s - url_prefix: %s<br>" % (
                #~ self.request.environ["SCRIPT_ROOT"], self.url_prefix
            #~ )
        #~ )
        path = self.relative_path(path)
        path = path.lstrip("/") # / Am Anfang wegschneiden
        path = posixpath.join(
            self.request.environ["SCRIPT_ROOT"], self.url_prefix, path
        )
        if path[-1]!="/": path+="/"

        #~ self.response.write("%s</p>" % path)

        try:
            return urllib.quote(path.encode("UTF-8"))
        except UnicodeError, e:
            if self.cfg["debug"]:
                self.response.write(
                    "<small>(Unicode-Error path.url: %s)</small><br />" % e
                )
            try:
                return urllib.quote(path)
            except:
                return path

    def relative_path(self, path):
        #~ self.response.write(
            #~ "<p>path.relative_path: '%s' - base_path: '%s'<br>" % (path, self.cfg["base_path"])
        #~ )
        if path.startswith(self.cfg["base_path"]):
            path = path[len(self.cfg["base_path"]):]
        #~ self.response.write("%s</p>" % path)
        return path

    def check_absolute_path(self):
        """
        Überprüft einen absoluten Pfad
        """
        if (self.absolute_path.find("..") != -1):
            # Hackerscheiß schon mal ausschließen
            raise AccessDenied("not allowed!")

        if not self.absolute_path.startswith(self.cfg["base_path"]):
            # Fängt nicht wie Basis-Pfad an... Da stimmt was nicht
            raise AccessDenied("permission deny #%s#%s#" % (
                self.absolute_path, self.cfg["base_path"])
            )
            raise AccessDenied("permission deny.")

        #~ print "JAU", self.absolute_path
        if not os.path.exists(self.absolute_path):
            # Den Pfad gibt es nicht
            raise AccessDenied, "'%s' not exists" % self.absolute_path


    def path_links(self, relativ_path=None):
        """
        Baut die Path Links zusammen
        """
        links = []

        if not relativ_path:
            relativ_path = copy.copy(self.relativ_path)

        path = relativ_path
        path = path.rstrip("/") # / Am Ende wegschneiden
        path = path.lstrip("/") # / Am Anfang wegschneiden

        # Link zu 'root' hinzufügen
        rootPath = posixpath.join(
            self.request.environ["SCRIPT_ROOT"], self.url_prefix
        )
        links.append({
            "url": rootPath,
            "title": "root",
        })

        if relativ_path == "/":
            # Wir sind im "root"-Verzeichnis
            return links

        lastURL = rootPath + "/"
        for item in path.split("/"):
            currentURL = lastURL + item + "/"
            lastURL = currentURL

            links.append({
                "url": currentURL,
                "title": item,
            })

        return links


    def get_absolute_fs_path(self):
        """
        Liefert den absoluten filesystem Pfad zurück (für os.listdir)
        """
        listPath = os.path.normpath(self.absolute_path)
        listPath = os.path.abspath(listPath)

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

            if not isinstance(listPath, unicode):
                self.response.write(
                        "<small>(Note: listPath is not unicode)</small><br />"
                    )

            self.response.write("listPath:")
            self.response.write(cgi.escape(str(type(listPath))))
            try:
                self.response.write("listPath: %s" % listPath)
            except:
                try:
                    self.response.write("listPath: %s" % listPath.encode(stdout_encoding))
                except:
                    pass
            self.response.write("<br>")

        return listPath




