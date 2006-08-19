#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
PyLucid Plugin - ZIP-File of Sourcecode

Bsp.:
<lucidFunction:PluginDownload>PyLucid/buildin_plugins/PluginDownload</lucidFunction>

"""

__version__="0.1"

__history__="""
v0.1
    - erste Version

"""

__todo__="""
    - Anzeigen einer Versionsnummer / Änderungsdatum
    - Mehr Info's zum Plugin (automatisch aus der DB)
    - Sourcecode ansicht
"""


import os, sys, StringIO, zipfile

from colubrid import HttpResponse

from PyLucid.system.BaseModule import PyLucidBaseModule

class PluginDownload(PyLucidBaseModule):

    def lucidFunction(self, function_info):
        """
        Link zum Downloaden des Plugins ausgeben
        """
        html = '<a href="%s">%s</a>' % ( 
            self.URLs.actionLink("download", function_info), function_info
        )
        self.response.write(html)

    def download(self, function_info):
        """
        Einen Download der ZIP Datei durchführen
        """
        try:
            plugin_name = function_info[0]
            package_name = self.db.get_package_name(plugin_name)
        except IndexError:
            self.response.write("Plugin/Module unknown!")
            return
            
        plugin_path = package_name.replace(".",os.sep)
        #sef.response.write(plugin_path)        
                
        #Dateiliste erstellen, von allen Dateien im Plugin Verzeichnis
        try:
            filelist = self.get_filelist(plugin_path)
        except WrongPath, e:
            msg = (
                "Can't get filelist! Is the path '%s' right? (Error: %s)"
            ) % (function_info, e)
            self.page_msg(msg)
            return


        # Virtuelle Datei im RAM erstellen
        buffer = StringIO.StringIO()
        #ZIP-File im RAM anlegen
        z = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

        for arcname in filelist:

            absfilename = os.path.join(plugin_path, arcname)
            #self.page_msg(arcname, absfilename)

            # Namen in ZIP-Dateien werden immer mit dem codepage 437 gespeichert
            # siehe Kommentare im Python-Bug 878120:
            #https://sourceforge.net/tracker/?func=detail&atid=105470&aid=878120&group_id=5470
            arcname = arcname.encode("cp437", "replace")

            z.write(absfilename, arcname)

        # Wenn alle Dateien in die ZIP Datei geschrieben wurden, müssen wir die Datei schließen
        # ist ganz wichtig, das erst dann der ZIP Header geschrieben wird!
        z.close()

        buffer.seek(0,2) # Am Ende der Daten springen
        buffer_len = buffer.tell() # Aktuelle Position
        buffer.seek(0) # An den Anfang springen

        #self.page_msg("Zip Datei len:", buffer_len)

        content = buffer.read()
        #self.page_msg(content[:50]) #Debug
        buffer.close()

        filename = self.get_pluginname(plugin_path)

        # Endung .zip anhängen
        filename = "%s.zip" % filename

        # ZIP Datei zum Browser senden
        response = self.FileResponse(content, buffer_len, filename)
        return response


    def get_pluginname(self, function_info):
        # Pfad normalisieren (evtl. vorhandenes / am Ende entfernen)
        filename = os.path.normpath(function_info)
        # Nur den letzten Teil des Namens:
        filename = os.path.basename(filename)

        return filename


    def get_filelist(self, function_info):
        """liefert eine Liste aller Dateien, die zum Plugin gehören zurück"""

        try:
            filelist = os.listdir(function_info)
        except OSError, e:
            raise WrongPath(e)

        result = []
        for filename in filelist:

            name, ext = os.path.splitext(filename)

            if not ext in (".pyc",):
                result.append(filename)

        # Nach der Schleife das Ergebnis ausgeben:
        #self.page_msg(result) # Alle Dateien außer *.pyc ausgeben

        return result # Ergebnis zurück liefern


    def FileResponse(self, content, contentLen, filename):
        # force Windows input/output to binary
        if sys.platform == "win32":
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


        # Ein "wirklich" frisches response-Object nehmen:
        response = HttpResponse()

        response.headers['Content-Disposition'] = \
            'attachment; filename="%s"' % filename
        response.headers['Content-Length'] = '%s' % contentLen
        response.headers['Content-Transfer-Encoding'] = '8bit' #'binary'
        response.headers['Content-Type'] = \
            'application/octet-stream; charset=utf-8'

        response.write(content)

        return response




class WrongPath(Exception):
    """
    Wenn der Pfad zu den Plugin Sourcen nicht stimmt
    """
    pass

