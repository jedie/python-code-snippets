#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""


debug = True
#~ debug = False



import os, posixpath



from PyLucid.system.BaseModule import PyLucidBaseModule


template = """
<ul class="gallery_files">
{% for item in files %}
    <li class="gallery_pic">
        <a href="{{ item.href }}" title="{{ item.name }}">
            <img src="{{ item.src }}" />
            <br />
            <small>{{ item.name }}</small>
        </a>
    </li>
{% endfor %}
"""





class pygallery(PyLucidBaseModule):
    cfg = {
        # Nur Endungen anzeigen, die in der Liste vorkommen
        "ext_whitelist": [".jpg", ".png", ".mpg", ".avi"],

        # =False -> Nur Dateien im aktuellen Verz. anzeigen
        "allow_subdirs": True,

        # Dateien die nicht angezeigt werden sollen
        "file_filter": (".htaccess",),

        ## Thumb-Gallerie-Einstellung
        # pic_ext           = Dateiendungen, die als Bilder behandelt werden sollen
        # thumb_pic_filter  = Filter, der aus den Dateinamen rausgeschnitten werden soll, um
        #                     damit das passende Thumbnail zu finden
        # thumb_suffix      = Liste der Suffixe im Dateiname mit dem ein Thumbnail markiert ist
        # resize_thumb_size = Wird kein Thumbnail gefunden, wird das original Bild auf diese Werte
        #                     verkleinert als Thumb genommen
        #
        # Bsp.:
        # Urlaub01_WEB.jpg   -> Bild zu dem ein Thumbnail gesucht wird
        # Urlaub01_thumb.jpg -> Das passende Thumbnail
        "pic_ext"           : (".jpg", ".jpeg"),
        "thumb_pic_filter"  : ("_WEB",),
        "thumb_suffix"      : ("_thumb",),
        "resize_thumb_size" : (100,60),
    }

    def __init__(self, *args, **kwargs):
        super(pygallery, self).__init__(*args, **kwargs)

        self.absolute_base_path = self._get_absolute_path()
        if debug:
            self.page_msg("absolute_path:", self.absolute_base_path)

    def lucidFunction(self, function_info):
        path = function_info.split("/")
        self.gallery(path)

    def gallery(self, function_info):
        #~ self.page_msg(function_info)
        path = "/".join(function_info)
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
            self.page_msg.red(msg)
            return

        if debug:
            self.page_msg("workdir:", self.workdir)

        try:
            files, dirs, thumbnails = self._read_workdir()
        except DirReadError, e:
            self.page_msg.red(e)
            return

        files = self._built_file_context(files, thumbnails)
        return

        context = {
            "files": files,
            "dirs": dirs,
        }
        if debug:
            self.page_msg("context:", context)

        url = self.URLs.actionLink("gallery", path)
        self.response.write('<a href="%s">%s</a>' % (url, url))

        from PyLucid.system.template_engines import render_jinja
        content = render_jinja(template, context)
        self.response.write(content)

    def _normpath(self, path):
        """
        Normalisiert den Path und gibt diesen zurück
        -Prüft auf böse Zeichen im Pfad
        -Prüft ob der Pfad innerhalb von self.absolute_base_path ist
        -Prüft ob das Ziel wirklich ein existierendes Verz. ist
        """
        path = posixpath.normpath(path)
        if ".." in path or "//" in path or "\\" in path:
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
        self.page_msg(thumbnails)
        for filename in files:
            base, ext           = posixpath.splitext( filename )
            self.page_msg(filename)


class PathError(Exception):
    """ Mit dem Path stimmt was nicht """
    pass

class DirReadError(Exception):
    """ Workdir kann nicht eingelesen werden """
    pass



