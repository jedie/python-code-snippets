#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__ = "$Rev$"

debug = True
#~ debug = False



import os, posixpath
import cgi


from PyLucid.components.plugin_cfg import PluginConfig
from PyLucid.system.BaseModule import PyLucidBaseModule






class pygallery(PyLucidBaseModule):
    def __init__(self, *args, **kwargs):
        super(pygallery, self).__init__(*args, **kwargs)

        self.plugin_cfg = PluginConfig(self.request, self.response)

        self.absolute_base_path = self._get_absolute_path()
        if debug:
            self.page_msg("absolute_path:", self.absolute_base_path)

    def lucidFunction(self, function_info):
        """
        Aufruf um eine Gallerie in die CMS Seite aufzubauen
        """
        self.gallery(function_info)

    def lucidTag(self):
        """
        Dummy, mit Infos
        """
        self.setup()
        #~ self.page_msg.red("Wrong call.")
        #~ msg = (
            #~ "<p>You should use a special lucidTag:</p>"
            #~ "<h3>&lt;lucidTag:pygallery.setup/&gt;</h3>"
            #~ "<p>Put this tag on a cms page without 'permit view public'.</p>"
        #~ )
        #~ self.response.write(msg)

    #_________________________________________________________________________

    def setup(self):
        """
        Alle existierende Gallerien verwalten
        """
        if debug:
            self.page_msg(self.request.form)
            self.plugin_cfg.debug()

        if "create" in self.request.form:
            # Es soll eine neue Gallerie eingerichtet werden
            self.create_new_gallerie()
            return

        galleries = []
        for gallerie, data in self.plugin_cfg["galleries"].iteritems():
            tag = "<lucidFunction:pygallery>%s</lucidFunction>" % gallerie
            tag = cgi.escape(tag)
            galleries.append({
                "name": gallerie,
                "lucidFunction": tag,
                "path": data["path"],
                "edit_link": self.URLs.actionLink("gallery_config", gallerie)
            })

        context = {
            "galleries" : galleries,
            "url": self.URLs.currentAction(),
            "base_path": self._get_absolute_path(),
        }
        self.page_msg(context)
        self.templates.write("setup", context)

    #_________________________________________________________________________

    def create_new_gallerie(self):
        """
        Erstellt eine neue Gallerie
        """
        try:
            gallery_name = self.request.form["name"]
        except KeyError, e:
            self.page_msg.red("Form error. Key '%s' not found." % e)
            return

        if gallery_name in self.plugin_cfg["galleries"]:
            self.page_msg.red(
                "A gallery named '%s' already exists!" % gallery_name
            )
            return

        self.plugin_cfg["galleries"][gallery_name] = {
            "path": None,
            "cfg": self.plugin_cfg["default_cfg"],
        }
        self.page_msg.green("Gallerie created. Please setup.")

        # Direkt die Config Seite aufrufen
        self.gallery_config([gallery_name])

    #_________________________________________________________________________

    def _rename_gallery(self, old_name, new_name):
        """
        Umbenennen einer Gallerie...
        """
        if new_name == old_name:
            # Dolles umbenennen ;)
            return old_name

        if new_name in self.plugin_cfg["galleries"]:
            self.page_msg.red("Can't rename gallery! New name exist!")
            return old_name

        self.plugin_cfg["galleries"][new_name] = \
                                        self.plugin_cfg["galleries"][old_name]

        del(self.plugin_cfg["galleries"][old_name])
        self.page_msg.green(
            "Gallery renamed from %s to %s" % (
                old_name, new_name
            )
        )
        return new_name

    def gallery_config(self, function_info):
        """
        Einstellungen einer bestehenden Gallerie ändern
        """
        if debug:
            self.plugin_cfg.debug()
            self.page_msg("self.request.form:", self.request.form)

        gallery_name = function_info[0]

        try:
            gallery_data = self.plugin_cfg["galleries"][gallery_name]
        except KeyError, e:
            msg = "Error: Gallery named '%s' unknown! (KeyError: %s)" % (
                gallery_name, e
            )
            self.page_msg.red(msg)
            return

        if "name" in self.request.form:
            # Gallerie soll umbenannt werden!
            new_gallery_name = self.request.form["name"]
            gallery_name = self._rename_gallery(gallery_name, new_gallery_name)

        absolute_path = self._get_absolute_path()

        def get_paths():
            result = []

            def dir_filter(path):
                for filter in self.plugin_cfg["dir_filter"]:
                    if path.startswith(filter):
                        return True
                return False

            abs_path_len = len(absolute_path) + 1
            for path in os.walk(absolute_path):
                path = path[0] # Nur Verz. Infos aus os.walk()

                path = path[abs_path_len:]
                if path == "":
                    # Erstes Verz.
                    continue
                if path.startswith("."):
                    # Linux versteckte Verz.
                    continue
                if dir_filter(path):
                    # PyLucid Verz.
                    continue

                result.append(path)

            return result

        paths = get_paths()

        if "path" in self.request.form:
            new_path = self.request.form["path"]
            if not new_path in paths:
                self.page_msg.red("path error!")
            else:
                if gallery_data["path"] != new_path:
                    gallery_data["path"] = new_path
                    self.page_msg.green("new gallery path saved.")

        context = {
            #~ "galleries" : galleries,
            "absolute_path": absolute_path,
            "current_path": gallery_data["path"],
            "paths": paths,
            "name": gallery_name,

            "url": self.URLs.actionLink("gallery_config", gallery_name),
            # Nicht self.URLs.currentAction() nehmen!
            # Wenn von setup() aufrufgerufen wurde, stimmt der Link nicht!
        }
        self.page_msg(context)
        self.templates.write("gallery_config", context)

    #_________________________________________________________________________

    def gallery(self, function_info):
        #~ self.page_msg(function_info)
        gallery_name = function_info

        try:
            gallery_data = self.plugin_cfg["galleries"][gallery_name]
        except KeyError, e:
            msg = "Error: Gallery named '%s' unknown! " % gallery_name
            if debug:
                msg += "(KeyError: %s)" % e
            self.page_msg.red(msg)
            return

        try:
            self._setup_workdir(gallery_data["path"])
        except PathError, e:
            self.page_msg.red(e)
            return

        self.cfg = gallery_data["cfg"]

        try:
            files, dirs, thumbnails = self._read_workdir()
        except DirReadError, e:
            self.page_msg.red(e)
            return

        file_context = self._built_file_context(files, thumbnails)
        dir_context = self._built_dir_context(dirs)

        context = {
            "files": file_context,
            "dirs": dir_context,
        }
        #~ url = self.URLs.actionLink("gallery", gallery_data["path"])
        #~ self.response.write('<a href="%s">%s</a>' % (url, url))

        self.templates.write("gallery", context, debug=True)

    #_________________________________________________________________________

    def _setup_workdir(self, path):
        self.relativ_path = posixpath.normpath(path)
        if debug:
            self.page_msg("relativ_path:", self.relativ_path)

        self.workdir = posixpath.join(self.absolute_base_path, self.relativ_path)
        try:
            self.workdir = self._normpath(self.workdir)
        except PathError, e:
            msg = "Path Error!"
            if debug:
                msg += " (Workdir: %s - Error: %s)" % (self.workdir, e)
            raise PathError(msg)

        if debug:
            self.page_msg("workdir:", self.workdir)

    def _normpath(self, path):
        """
        Normalisiert den Path und gibt diesen zurück
        -Prüft auf böse Zeichen im Pfad
        -Prüft ob der Pfad innerhalb von self.absolute_base_path ist
        -Prüft ob das Ziel wirklich ein existierendes Verz. ist
        """
        path = posixpath.normpath(path)
        if ".." in path or "//" in path or "\\\\" in path:
            # Da stimmt doch was nicht...
            raise PathError("bad character in path")
        if not path.startswith(self.absolute_base_path):
            raise PathError("Wrong base")
        if not os.path.isdir(path):
            raise PathError("Path is not a existing directory.")

        return path

    def _get_absolute_path(self):
        """
        Liefert den absoluten basis Pfad zurück
        """
        try:
            doc_root = os.environ["DOCUMENT_ROOT"]
        except KeyError:
            doc_root = os.getcwd()

        return doc_root

    #_________________________________________________________________________

    def _read_workdir(self):
        """
        Einlesen des Verzeichnisses self.workdir
        -filtert direkt die Thumbnails raus
        """
        files = []
        dirs = []
        thumbnails = {}

        def is_thumb(name, file_name):
            "Kleine Hilfsfunktion um Thumbnails raus zu filtern"
            for suffix in self.cfg["thumb_suffix"]:
                if name[-len(suffix):] == suffix:
                    # Aktuelle Datei ist ein Thumbnail!
                    clean_name = name[:-len(suffix)]
                    thumbnails[clean_name] = file_name
                    return True
            return False

        if debug:
            self.page_msg("read '%s'..." % self.relativ_path)

        try:
            dirlist = os.listdir(self.workdir)
        except Exception, e:
            msg = "Can't read dir."
            if debug:
                msg += " (dir: %s, Error: %s)" % (self.workdir, e)
            raise DirReadError(msg)

        for item in dirlist:
            abs_path = os.path.join(
                self.absolute_base_path, self.relativ_path, item
            )
            abs_path = os.path.normpath(abs_path)
            #~ self.page_msg(abs_path)

            if os.path.isdir(abs_path): # Verzeichnis verarbeiten
                if self.cfg["allow_subdirs"]:
                    # Unterverz. sollen angezeigt werden
                    dirs.append(item)
                continue

            if os.path.isfile(abs_path): # Dateien verarbeiten
                if item in self.cfg["file_filter"]:
                    # Datei soll nicht angezeigt werden
                    continue

                name, ext = posixpath.splitext( item )

                # Thumbnails rausfiltern
                if is_thumb( name, item ):
                    # Ist ein Thumbnail -> soll nicht in die files-Liste!
                    continue

                if ext in self.cfg["ext_whitelist"]:
                    files.append(item)
                continue

            # Kein Verz., keine Datei
            if debug:
                self.page_msg(
                    "Skip: %s (is not a file or directory)" % abs_path
                )

        files.sort()
        dirs.sort()

        #~ if self.relativ_path != ".":
            #~ # Nur erweitern, wenn man nicht schon im Hauptverzeichnis ist
            #~ dirs.insert(0,"..")

        return files, dirs, thumbnails

    def _built_file_context(self, files, thumbnails):
        """
        Formt aus den Datelisting Daten den jinja context
        """
        def get_thumbnail(base):
            if base in thumbnails:
                # Es existiert zu dem Bild ein Thumbnail
                thumbnail = thumbnails[base]
            else:
                # Kein Thumbnail, dann zeigen wir das normale Bild in klein
                thumbnail = filename

            return posixpath.join(self.relativ_path, thumbnail)


        def get_clean_name(base):
            result = base
            for rule in self.cfg["name_filter"]["replace_rules"]:
                # Alle "replace_rules" Anwenden
                result = result.replace(rule[0], rule[1])

            if self.cfg["name_filter"]["strip_whitespaces"]:
                # Leerzeichen bearbeiten
                result = result.strip(" ")
                for i in xrange(10):
                    # Mehrere Leerzeichen, die evtl. bei den "replace_rules"
                    # entstanden sind, zu einem wandeln
                    if not "  " in result:
                        break
                    result = result.replace("  ", " ")

            return result


        context = []

        self.page_msg(thumbnails)
        for filename in files:
            base, ext = os.path.splitext(filename)
            if not ext in self.cfg["ext_whitelist"]:
                continue

            file_info = {}

            # Adresse zum Thumbnail
            file_info["src"] = get_thumbnail(base)

            # Name des Bildes
            file_info["name"] = get_clean_name(base)

            context.append(file_info)

        return context

    def _built_dir_context(self, dirs):
        context = []
        #~ self.page_,s
        for dirname in dirs:
            dir_info = {
                "href": dirname,
                "name": dirname
            }
            context.append(dir_info)

        return context


class PathError(Exception):
    """ Mit dem Path stimmt was nicht """
    pass

class DirReadError(Exception):
    """ Workdir kann nicht eingelesen werden """
    pass



