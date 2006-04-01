#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Eigene Ausnahmen
from exceptions import *

import os, posixpath, urllib, copy

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

        path = urllib.unquote(path)

        self.relativ_path = path
        if self.relativ_path == "":
            self.relativ_path = "/"
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
        path = self.relative_path(path)
        path = posixpath.join(
            self.request.environ["SCRIPT_ROOT"], self.url_prefix, path
        )
        #~ path = posixpath.join(self.url_prefix, path)
        return urllib.quote(path)

    def relative_path(self, path):
        #~ self.request.echo("<p>",path,"<br>")
        if not path.startswith(self.cfg["base_path"]):
            return path
        path = path.lstrip(self.cfg["base_path"])
        #~ path = path.lstrip(self.absolute_path)

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

        if not os.path.exists(self.absolute_path):
            # Den Pfad gibt es nicht
            raise AccessDenied, "'%s' not exists" % self.absolute_path


    def path_links(self):
        """
        Baut die Path Links zusammen
        """
        links = []

        #~ self.response.write(self.relativ_path)
        path = copy.copy(self.relativ_path)

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

        if self.relativ_path == "/":
            # Wir sind im "root"-Verzeichnis
            return links

        lastURL = rootPath
        for item in path.split("/"):
            currentURL = lastURL + item + "/"
            lastURL = currentURL

            links.append({
                "url": currentURL,
                "title": item,
            })

        return links






