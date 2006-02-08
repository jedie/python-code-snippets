#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__      = "Jens Diemer"
__url__         = "http://www.jensdiemer.de/Programmieren/Python/PyFileCenter"
#SVN: http://pylucid.python-hosting.com/file/CodeSnippets/PyFileCenter/FileBrowser.py
__license__     = "GNU General Public License (GPL)"
__description__ = "a pure Python-CGI-FileBrowser (Download-Center)"

"""
Beispiel "index.py":
-------------------------------------------------------------------------------
# Verzeichnis in dem sich "FileBrowser.py" befindet in den Suchpfad aufnehmen
sys.path.insert( 0, os.environ["DOCUMENT_ROOT"] + "cgi-bin/PyFileCenter/" )

import FileBrowser


# Nur Endungen anzeigen, die in der Liste vorkommen
FileBrowser.cfg.ext_whitelist   = [ ".7z", ".zip", ".py" ]

# Hauptverz.: Navigation nur innerhalb diese Verz. mit Unterverz. erlauben
FileBrowser.cfg.base_path       = "Programmieren"

# Verz. in der Liste auslassen:
FileBrowser.cfg.dir_filter      = ["OLD"]

# Dateien die nicht angezeigt werden sollen
FileBrowser.cfg.file_filter     = ["index.py"]

# =False -> Nur Dateien im aktuellen Verz. anzeigen
FileBrowser.cfg.allow_subdirs   = True

# =True -> User kann in ZIP Archiven reinsehen
FileBrowser.cfg.allow_zipview   = True

# zurück-Link der auf jeder Seite eingeblendes werden soll
FileBrowser.cfg.backlink = {
        "txt"   : "< zurück zur Homepage",
        "url"   : "http://www.jensdiemer.de/"
    }

# Verzeichnis bezogene zurück-Links
FileBrowser.cfg.dir_backlinks = {
    "PyAdmin"       : ["< PyAdmin Projektseite",        "http://www.jensdiemer.de?PyAdmin"],
    "PyDiskEraser"  : ["< PyDiskEraser Projektseite",   "http://www.jensdiemer.de?PyDiskEraser"],
    "PyLucid"       : ["< PyLucid Projektseite",        "http://www.jensdiemer.de?PyLucid"]
}

# HTML-Head
FileBrowser.cfg.html_head["robots"] = "index,follow"


# Starten...
FileBrowser.FileBrowser()
-------------------------------------------------------------------------------

Es gibt noch einige andere Parameter in der cfg-Klasse. Einfach mal unten in
den Sourcen schauen!



____________________________________________________________________________________

Benötigte SQL-Tabellen

CREATE TABLE `FileCenter_Stat_Path` (
    `id` INT NOT NULL AUTO_INCREMENT ,
    `name` VARCHAR( 255 ) NOT NULL ,
    PRIMARY KEY ( `id` )
) TYPE = MYISAM ;

CREATE TABLE `FileCenter_Stat_Item` (
    `id` INT NOT NULL AUTO_INCREMENT ,
    `path_id` INT NOT NULL ,
    `name` VARCHAR( 255 ) NOT NULL ,
    `count` int(11) NOT NULL default '0',
    PRIMARY KEY ( `id` )
) TYPE = MYISAM ;


"""

__version__ = "v0.5.2"

__history__ = """
v0.5.2
    - Bugfix: print_back_link() nutzt nun urllib.quote_plus() damit auch Sonderzeichen in
        den Verzeichnisnamen erlaubt sind
v0.5.1
    - NEU: cfg.use_sql_statistic, damit es auch ohne SQL eingesetzt werden kann!
    - NEU: cfg.debug
v0.5.0
    - NEU: MySQL Statistik
v0.4.2
    - Bilder-Gallerie: Ein Bild wird nun auch mit Thumbnail dargestellt, wenn es nicht
        in cfg.thumb_pic_filter vorkommt, aber ein passendes Thumbnail gefunden wurde.
v0.4.1
    - Bilder-Gallerie: Beim anschauen eines Bilder kann man drauf klicken und es
        es wird das nächste angezeigt
v0.4.0
    - NEU: Thumb-Gallerie-Einstellung
    - NEU: CSS läßt sich nun auch ändern
    - Bug: änderungen am HTML-Kopf funktionierten garnicht
v0.3.3
    - Alle URLs sollten nun durch urllib.quote() angezeigt werden
v0.3.2
    - Umstellung von subprocess auf os.popen, weil's subprocess erst ab 2.4 gibt
    - ZIPfile-Viewer zeigt nun mehr an
v0.3.1
    - Umstrukturierung des Codes
    - NEU: Download-Proxy für Scriptdateien, damit sie nicht auf dem Server ausgeführt
        werden, sondern runterladen ;)
    - NEU: Renderzeit anzeige... wow =:-0
v0.3.0
    - Komplette Änderung der Konfiguration
v0.2.2
    - NEU: BackLink
v0.2.1
    - Downloadlinks nun immer mit MIME-type="application/octet-stream" - danke Leonidas
    - Fehler: Downloadlinks korrigiert
v0.2
    - NEU: zipfile "Viewer"
v0.1.1
    - Darstellung der KBytes für Dateien mit "de_DE.UTF-8"
v0.1
    - erste Version
"""

__info__ = '<a href="%s">FileBrowser</a> %s' % (__url__, __version__)

import cgitb; cgitb.enable()

import time
start_time = time.time()

import os, sys, cgi, stat, locale, re, urllib
import zipfile



#______________________________________
# Beispiel config.py:
## dbconf = {
##     "dbHost"            : 'localhost', # Evtl. muß hier die Domain rein
##     "dbDatabaseName"    : 'DatabaseName',
##     "dbUserName"        : 'UserName',
##     "dbPassword"        : 'Password',
## }
import config # Import der SQL-Konfiguration (dbconf-Dict)




CSS_style = """<style type="text/css">
@media all {
/*
Mac IE Filter
http://w3development.de/css/hide_css_from_browsers/media/
*/
    body {
        font-size: 0.9em;
    }
    html, body {
        margin: 10px;
        padding: 0;
        font-family: tahoma, arial, sans-serif;
        color: #000000;
        background-color: #FFFFFF;
    }
    body {
        min-height: 500px;
    }
    a {         /* Link allgemein */
        text-decoration:none;
    }
    a:link {    /* noch nicht besuchter Link */
        color: #000088;
    }
    a:visited { /* schon besuchter Link */
        color: #000000;
    }
    a:hover {   /* Maus über dem Link */
        color: #4444FF;
        text-decoration:underline;
    }
    a:active {  /* Link wird angeklickt */
        color: #FF0000;
    }
    h1 { /* Seitenüberschrift */
        border-bottom: 1px solid #000000;
    }
    /*
        _________________________________________
        Verzeichnis-Liste
    */
    .gallery_dirs ul {
    }
    .gallery_dirs li {
        list-style-type: none;
    }
    .gallery_dirs li:hover {
        list-style-type:disc;
    }
    /*
        _________________________________________
        Datei-Liste
    */
    /*
        Dateiliste allgemein
    */
    .gallery_files ul {
        text-align: center;
        margin: 0px;
        padding: 0px;
    }
    .gallery_files li {
        float: left;
        border: 1px solid #DDDDDD;
        height: 150px;
        width: auto;
        text-align: center;
        margin: 5px;
        padding: 5px;
        list-style-type: none;
        background-color: #EEEEEE;
    }
    /*
        nur normale Dateien
    */
    .normal a {
        padding: 0 5px 0px 5px;
    }
    /*
        nur Bilder mit Thumnailansicht
    */
    .gallery_pic a {
        text-decoration:none;
    }
    .gallery_pic img {
        border: 0px;
    }
    #dir_counter, #file_counter, #zip_counter {
        font-size: 0.6em;
        clear: both;
        text-align: center;
        color: #CCCCCC;
    }
    #zip_counter {
        text-align: left;
    }
    /*
        _________________________________________
        Footer
    */
    #gallery_clear {
        clear: both;
        width: auto;
        border: none;
    }
    #gallery_footer {
        border-top: 2px solid #CCCCCC;
        font-size: 0.6em;
        text-align: center;
        color: #CCCCCC;
    }
    #gallery_footer a {
        padding: 0;
        color: #CCCCCC;
        text-decoration:none;
    }
    /*
        _________________________________________
        ZIP
    */
    .zipinfo td {
        padding-right: 0.7em;
        padding-left: 0.7em;
    }
    /*
        _________________________________________
        Image View - Ein Bild wird Angezeit
    */
    #img_view {
        text-align:center;
        width:auto;
        margin:auto;
        display:block;
        text-decoration:none;
    }
    #img_view img {
        border: 1px solid #000000;
    }
    #img_view a, #img_view a:hover {
        text-decoration:none;
    }
}
</style>
"""







class cfg:
    """
    Pseudo Klasse zum 'speichern' der Konfiguration.

    Hierhin wird die Basis Konfiguration gespeichert, die
    von außerhalb verändert werden sollte.
    """

    # Nur Endungen anzeigen, die in der Liste vorkommen
    ext_whitelist       = [ ".jpg",".mpg",".avi" ]

    # Downloadbare Textdateien über eingebaute Downloadproxy
    ext_download_proxy  = [ ".py",".php",".php4",".php5" ]

    # Dateiendungen, bei denen nicht der file-Befehl ausgeführt werden soll,
    # sondern der eingebaute "Analysator", der aber bisher nur *.py Dateien kann ;)
    override_fileinfo = {
            ".py"   : "Python Script",
        }

    # Hauptverz.: Navigation nur innerhalb diese Verz. mit Unterverz. erlauben
    base_path           = "MeinDownloadVerzeichnis"

    # Verz. in der Liste auslassen:
    dir_filter          = []

    # Dateien die nicht angezeigt werden sollen
    file_filter         = [ "index.py", ".htaccess" ]

    # =False -> Nur Dateien im aktuellen Verz. anzeigen
    allow_subdirs       = True

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
    pic_ext             = ( ".jpg", ".jpeg" )
    thumb_pic_filter    = ( "_WEB", )
    thumb_suffix        = ( "_thumb", )
    resize_thumb_size   = ( 100,60 )

    # zurück-Link der auf jeder Seite eingeblendes werden soll
    backlink = {
            "txt"   : "< zurück zur Homepage", # wird HTML-escaped!
            "url"   : "http://www.jensdiemer.de/"
        }

    # Verzeichnis bezogene zurück-Links
    dir_backlinks_code = '<p><a href="%(url)s">%(txt)s</a></p>'
    dir_backlinks = {}

    # Link auf der Seite unten
    footer_backlink_code = '<p><small><a href="%(url)s">%(txt)s</a></small></p>'
    footer_backlink = {
            "txt"   : "< zurück zur Homepage", # wird HTML-escaped!
            "url"   : "http://www.jensdiemer.de/"
        }

    # HTML Header Informationen
    html_head = {
            "robots"      : "noindex,nofollow",
            "keywords"    : "",
            "description" : "",
            "CSS"         : CSS_style,
        }

    ## Counter...
    # ...in einer Dateiliste
    dir_counter_txt = '<div id="dir_counter">(count %s)</div>'
    # ...In Dateiliste
    file_count_txt = '<div id="file_counter">(count %s)</div>'
    # ...beim betrachten einer ZIP-Datei
    zip_view_txt = '<div id="zip_counter">(count %s)</div>'

    # Wird nach den Standart CSS-Tag eingefügt
    # Damit kann man also gezielt nur ein paar CSS-Eigenschaften überschreiben
    # Muß komplett mit Anfangs-/Endtags sein, also:
    # <style type="text/css">...</style>
    additional_CSS = ""

    # Soll in der SQL-Datenbank ein counter Statistik geführt werden?
    use_sql_statistic = True

    # Debug-Ausgaben
    debug = False



HTML_head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>FileBrowser</title>
<meta name="robots"                    content="%(robots)s" />
<meta name="keywords"                  content="%(keywords)s" />
<meta name="description"               content="%(description)s" />
<meta http-equiv="Content-Type"        content="text/html; charset=utf-8" />
<meta name="MSSmartTagsPreventParsing" content="TRUE" />
<meta http-equiv="imagetoolbar"        content="no" />
%(CSS)s
%(additional_CSS)s
</head>
<body>"""



formatter_regex = re.compile("^ *\d*\D\d{1,3}|\d{1,3} *")
def formatter(number, format = "%.2f", decChar = ",", groupChar = "."):
    """
    Convert to required format
    by HarryH modify by Jens Diemer

    number =      number to convert
    format =      python string formatting (%)
    decChar =     decimal char for the converted format
    groupChar =   group char for the converted format

    For example:
    formatter(1234567890.987, "%.2f", ",", ".")
    ==> 1.234.567.890,99
    formatter( 1234567890.987, "%i")
    ==> 1.234.567.890

    """
    def reverse(s):
        # ersatz für string[::-1] welches erst ab v2.3 gibt :(
        # Nach einer Idee von Milan
        l = map(None, s)
        l.reverse()
        return ('').join(l)

    return reverse(
        groupChar.join(
            formatter_regex.findall(
                reverse( (format % number).replace(".", decChar) )
            )
        )
    )


#____________________________________________________________________________________


class zipmanager:
    def __init__( self, workdir, filename ):
        self.filename = filename

        try:
            self.zipobj = zipfile.ZipFile( os.path.join(workdir, self.filename), "r" )
        except Exception,e:
            print "<p>Error: %s</p>" % e
            return

        self.view()

    def view( self ):
        print '<table class="zipinfo">'
        print "<tr>"
        print "<th>filename</th>"
        print "<th>compress_size</th>"
        print "<th>size</th>"
        print "<th>ratio</th>"
        print "<th>date_time</th>"
        print "</tr>"
        total_compress_size = 0
        total_file_size = 0
        for fileinfo in self.zipobj.infolist():
            if fileinfo.filename.endswith("/"):
                # Ist ein Verzeichniss
                continue

            print "<tr>"
            print "<td>%s</td>" % fileinfo.filename

            total_compress_size += fileinfo.compress_size
            print '<td style="text-align: right;">%s</td>' % formatter( fileinfo.compress_size, "%i" )

            total_file_size += fileinfo.file_size
            print '<td style="text-align: right;">%s</td>' % formatter( fileinfo.file_size, "%i" )

            try:
                ratio = float(fileinfo.compress_size)/fileinfo.file_size*100
            except ZeroDivisionError:
                ratio = 100.0
            print '<td style="text-align: right;">%s%%</td>' % formatter( ratio, "%0.1f" )

            d = fileinfo.date_time
            print '<td>%0.2i.%0.2i.%i %0.2i:%0.2i:%0.2i</td>' % (d[2],d[1],d[0],d[3],d[4],d[5])

            print "</tr>"
        print "</table>"
        print "<ul>"
        print "<li>total compress size: %s Bytes</li>" % formatter( total_compress_size, "%i" )
        print "<li>total size: %s Bytes</li>" % formatter( total_file_size, "%i" )
        try:
            print "<li>Ratio: %s%%</li>" % formatter( float(total_compress_size)/total_file_size*100 )
        except ZeroDivisionError:
            pass
        print "</ul>"



#____________________________________________________________________________________

class mySQL_statistic:
    def __init__( self ):
        self.db = self.connect()
        self.db_conf = {
            "path" : "FileCenter_Stat_Path",
            "item" : "FileCenter_Stat_Item",
        }

    def connect( self ):
        import mySQL
        try:
            # SQL connection aufbauen
            return mySQL.mySQL(
                    host    = config.dbconf["dbHost"],
                    user    = config.dbconf["dbUserName"],
                    passwd  = config.dbconf["dbPassword"],
                    db      = config.dbconf["dbDatabaseName"],
                )
        except Exception, e:
            print "Content-type: text/html\n"
            print "<h1>PyLucid - Error</h1>"
            print "<h2>Can't connect to SQL-DB: '%s'</h2>" % e
            import sys
            sys.exit()

    def get_path_id( self, path, auto_create=True ):
        """ id eines Eintrages, existiert der Eintrag noch nicht, wird er angelegt """

        def id( path ):
            return self.db.select(
                select_items    = ["id"],
                from_table      = self.db_conf["path"],
                where           = ( "name", path )
            )[0]["id"]

        try:
            return id( path )
        except IndexError:
            # Path existiert noch nicht
            if auto_create != True:
                return False
            # Path wird angelegt
            self.db.insert(
                    table = self.db_conf["path"],
                    data  = { "name" : path }
                )
            return id( path )

    def get_item( self, path_id, item_name, auto_create=True ):

        def id( path_id, item_name ):
            result = self.db.select(
                select_items    = ["id","count"],
                from_table      = self.db_conf["item"],
                where           = [ ("path_id", path_id), ("name",item_name) ]
            )[0]
            return result["id"], result["count"]

        try:
            return id( path_id, item_name )
        except IndexError:
            # Item existiert noch nicht
            if auto_create != True:
                return False
            # Eintrag für Item wird angelegt
            self.db.insert(
                    table = self.db_conf["item"],
                    data  = { "path_id": path_id, "name": item_name }
                )
            return id( path_id, item_name )

    def only_get_count( self, path, item_name ):
        """ Nur den Counterwert zurückliefern, ohne den Zähler zu erhöhen """

        path_id = self.get_path_id( path, auto_create=False )
        if path_id == False:
            return "Path unknow!"
            return False

        item_info = self.get_item( path_id, item_name, auto_create=False )
        if item_info == False:
            print "Kein item_info [%s] path_id:%s" % (item_name, path_id)
            return 0
        else:
            return item_info[1]

    def count( self, path, item_name ):
        """ Zähler eines Eintrages hochsetzten oder erstellen, wenn noch nicht existend. """

        path_id = self.get_path_id( path )
        item_id, item_count = self.get_item( path_id, item_name )
        item_count += 1

        self.db.update(
            table   = self.db_conf["item"],
            data    = { "count" : item_count },
            where   = ( "id", item_id),
            limit   = 1
        )
        return item_count


#____________________________________________________________________________________


class FileBrowser:
    def __init__( self ):
        if cfg.use_sql_statistic == True:
            # SQL connection aufbauen
            self.statistic = mySQL_statistic()

        self.thumbnails = {} # wird von read_dir gefüllt, wenn Thumbnails gefunden wurden

        self.absolute_basepath = os.path.join( os.environ["DOCUMENT_ROOT"], cfg.base_path )

        self.CGIdata = self.getCGIdata()

        (self.relativ_path, self.absolute_path) = self.get_current_path()
        # Wird vom Counter verwendet:
        self.root_path = self.absolute_path[len(os.environ["DOCUMENT_ROOT"]):]

        if self.CGIdata.has_key("download"):
            # ist ein Download-Proxy-Link aufruf
            # Davor darf noch kein Header gesendet worden sein!
            self.download_proxy( self.CGIdata["download"] )

        # Erst der Header hier ausgeben, weil der Download-Proxy evtl. ausgeführt wurde!!!
        print "Content-type: text/html; charset=utf-8\r\n"
        self.print_head()
        if cfg.debug:
            print "absolute_basepath:", self.absolute_basepath

        if self.CGIdata.has_key("zipfile") and (cfg.allow_zipview == True):
            # Es soll eine ZIP-Datei angezeigt werden.
            self.print_back_link()
            zm = zipmanager( self.absolute_path, self.CGIdata["zipfile"] )

            if cfg.use_sql_statistic == True:
                # Aktueller Counterwert, anzeigen und in DB um eins erhöhen
                print cfg.zip_view_txt % self.statistic.count( self.root_path, "<view %s>" % self.CGIdata["zipfile"] )

            self.print_back_link()

        elif self.CGIdata.has_key("img"):
            # Ein Bild soll angezeigt werden
            self.print_back_link()
            self.print_img_view( self.CGIdata["img"] )
            self.print_back_link()

        elif self.CGIdata.has_key("next_img"):
            # Das nächste Bild soll angezeigt werden
            self.handle_next_img( self.CGIdata["next_img"] )

        else:
            # Normale Brower-Seite
            files, dirs = self._read_dir()
            self.print_body( files, dirs )

        self.print_footer()

    ##_____________________________________________________________________________
    ## Allgemeine Routinen

    def print_back_link( self ):
        print '<p><a href="?path=%s">&lt; back</a></p>' % urllib.quote_plus(self.relativ_path)

    def get_current_path( self ):
        if self.CGIdata.has_key( "path" ):
            relativ_path = os.path.normpath( self.CGIdata["path"] )
        else:
            relativ_path = "."

        cfg.base_path = os.path.normpath( cfg.base_path )

        absolute_path = os.path.join( self.absolute_basepath, relativ_path )
        absolute_path = os.path.normpath( absolute_path )

        self.check_absolute_path( absolute_path )

        return relativ_path, absolute_path


    def error( self, txt ):
        """Fehlermeldung mit anschließendem sys.exit()"""
        print "Content-Type: text/html\n"
        print HTML_head
        print "<h2>%s</h2>" % txt
        print '<a href="?">back</a>'
        self.print_footer()
        sys.exit()

    def check_absolute_path( self, absolute_path ):
        """
        Überprüft einen absoluten Pfad
        """
        if (absolute_path.find("..") != -1) or (absolute_path.find("//") != -1):
            # Hackerscheiß schon mal ausschließen
            self.error( "not allowed!" )

        if absolute_path[:len(self.absolute_basepath)] != self.absolute_basepath:
            # Fängt nicht wie Basis-Pfad an... Da stimmt was nicht
            self.error( "permission deny." )

        if not os.path.isdir( absolute_path ):
            # Den Pfad gibt es nicht
            self.error( "'%s' not exists" % absolute_path )

    def getCGIdata( self ):
        "CGI-POST Daten auswerten"
        data = {}
        FieldStorageData = cgi.FieldStorage( keep_blank_values=True )
        for i in FieldStorageData.keys(): data[i] = FieldStorageData.getvalue(i)
        return data


    def _read_dir( self ):
        "Einlesen des Verzeichnisses"

        def is_thumb( name, file_name ):
            "Kleine Hilfsfunktion um Thumbnails raus zu filtern"
            for suffix in cfg.thumb_suffix:
                if name[-len(suffix):] == suffix:
                    # Aktuelle Datei ist ein Thumbnail!
                    clean_name = name[:-len(suffix)]
                    self.thumbnails[clean_name] = file_name
                    return True
            return False

        if cfg.debug:
            print "read '%s'..." % self.absolute_path

        files = []
        dirs = []
        for item in os.listdir( self.absolute_path ):
            abs_path = os.path.join( self.absolute_path, item )
            if os.path.isfile( abs_path ):
                # Dateien verarbeiten

                if item in cfg.file_filter:
                    # Datei soll nicht angezeigt werden
                    continue

                name, ext = os.path.splitext( item )

                # Thumbnails rausfiltern
                if is_thumb( name, item ):
                    # Ist ein Thumbnail -> soll nicht in die files-Liste!
                    continue

                if ext in cfg.ext_whitelist:
                    files.append( item )

            else:
                # Verzeichnis verarbeiten

                if cfg.allow_subdirs:
                    # Unterverz. sollen angezeigt werden
                    if not item in cfg.dir_filter:
                        dirs.append( item )

        files.sort()
        dirs.sort()

        if self.relativ_path != ".":
            # Nur erweitern, wenn man nicht schon im Hauptverzeichnis ist
            dirs.insert(0,"..")

        return files, dirs


    ##_____________________________________________________________________________
    ## Datei-Routinen

    def get_charset( self, absolute_filepath ):
        """Ermittelt das charset im Dateiheader: z.b.: # -*- coding: UTF-8 -*- """

        f = file( absolute_filepath, "rU" )

        headlines = []
        for i in range(2):
            # ersten zwei Zeilen lesen
            headlines.append( f.readline() )

        f.close()

        return re.findall(r"- coding: (.+?) -", "".join(headlines) )[0]

    def process_file_command( self, filename ):
        """ Datei Information mit Linux 'file' Befehl zusammentragen """

        command = "file %s" % os.path.join(self.absolute_path,filename)
        fileinfo = os.popen( command ).readlines()[0]

        fileinfo = fileinfo.split(":",1)[1]
        if fileinfo.find("ERROR") != -1:
            # Ersatz für >"ERROR" in fileinfo< ;)
            return ""
        else:
            return fileinfo


    def print_fileinfo( self, filename, absolute_filepath, base, ext ):
        """ file-Informationen mittels file oder manuell """

        print "<small>"

        if ext in cfg.override_fileinfo:
            # Es soll kein 'file'-Befehl ausgeführt werden
            print cfg.override_fileinfo[ext]
            if ext == ".py":
                try:
                    print " - Charset: %s" % self.get_charset( absolute_filepath )
                except:
                    pass
        else:
            # Holt informationen über den 'file'-Befehl
            try:
                print self.process_file_command( filename )
            except Exception, e:
                print "FileInfo Error:<br/>%s" % e

        print "</small>"


    ##_____________________________________________________________________________
    ## Seiten generierung

    def print_head( self ):
        """Kopf + Überschrift + backLink ausgeben"""

        # Key für zusätzliche CSS Einträge ans Dict hinzufügen
        cfg.html_head.update(
            { "additional_CSS": cfg.additional_CSS }
        )
        print HTML_head % cfg.html_head

        current_path = os.path.join( cfg.base_path, self.relativ_path )
        current_path = os.path.normpath( current_path )
        print "<h1>%s - Downloads</h1>" % current_path

        if self.relativ_path in cfg.dir_backlinks:
            print cfg.dir_backlinks_code % {
                "url" : cfg.dir_backlinks[ self.relativ_path ][1],
                "txt" : cgi.escape( cfg.dir_backlinks[ self.relativ_path ][0] )
            }


    def print_dir( self, dir ):
        """Verzeichnis auflisten"""

        if dir != "..":
            before  = ""
            after   = " &gt;"
        else:
            before  = "&lt; "
            after   = ""

        print '<li><a href="?path=%(url)s">%(before)s%(txt)s%(after)s</a></li>' % {
                "url"       : urllib.quote( os.path.normpath( os.path.join( self.relativ_path, dir ) ) ),
                "before"    : before,
                "txt"       : dir,
                "after"     : after
            }


    def print_body( self, files, dirs ):
        """Schleife für die eigentliche Seite"""

        if cfg.allow_subdirs:
            print '<ul class="gallery_dirs">'
            for dir in dirs:
                self.print_dir( dir )
            print "</ul>"

        print '<ul class="gallery_files">'
        for file in files:
            self.print_file( file )

        print "</ul>"

        if cfg.use_sql_statistic == True:
            # Aktueller Counterwert, anzeigen und in DB um eins erhöhen
            print cfg.dir_counter_txt % self.statistic.count( self.root_path, "<dir %s>" % self.root_path )


    def print_gallery_pic( self, pic_base_name, img_name, file_url ):

        print '<li class="gallery_pic">'

        print '<a href="?path=%s&img=%s">' % (
            urllib.quote( self.relativ_path ),
            urllib.quote( img_name )
        )

        if pic_base_name in self.thumbnails:
            # Es gibt ein Thumbnail
            img_path = os.path.join( self.relativ_path, self.thumbnails[pic_base_name] )
            print '<img src="%s" />' % img_path
        else:
            # Kein passendes Thumb. gefunden -> Original Bild wird als Thumb. verwendet
            print '<img src="%s" width="%s" height="%s" />' % (
                file_url, cfg.resize_thumb_size[0], cfg.resize_thumb_size[1]
            )

        print "<br/>"
        print "<small>%s</small>" % pic_base_name.replace("_"," ")
        print "</a>"
        print "</li>"

    def _is_gallery_img( self, base, ext ):
        """ Unterscheidet Bilder für Gallerymodus """
        if not (ext in cfg.pic_ext):
            # Ist überhaupt kein Bild
            return False

        if base in self.thumbnails:
            # Ein Thumbnail ist für das aktuelle Bild vorhanden
            return base

        # Ist ein Bild, könnte für eine Thumbnailansicht sein.
        for suffix in cfg.thumb_pic_filter:
            # Testet ob das Bild ein suffix besitzt (z.B. *_WEB.jpg)
            if base[-len(suffix):] == suffix:
                # Aktuelle Datei ist ein Gallerie-Bild
                return base[:-len(suffix)]

        return False


    def print_file( self, filename ):
        """ Dateiinfromationen ermitteln und auflisten """

        absolute_filepath   = os.path.join(self.absolute_path,filename)
        base, ext           = os.path.splitext( filename )
        file_url            = os.path.join( self.relativ_path, filename )

        clean_base_name = self._is_gallery_img( base, ext )
        if clean_base_name != False:
            # Aktuelle Datei ist ein Gallerie-Bild
            self.print_gallery_pic( clean_base_name, filename, file_url )
            return

        print '<li class="normal"><br/>'

        #~ if ext in cfg.ext_download_proxy:
        # Download-Proxy-Link
        print '<a href="?download=%s">%s</a>' % ( urllib.quote(file_url), urllib.quote(filename) )
        #~ else:
            #~ # Normaler Link
            #~ print '<a href="%s" type="application/octet-stream">%s</a>' % \
                #~ ( urllib.quote(file_url), urllib.quote(filename) )

        print "<br/>"

        self.print_fileinfo( filename, absolute_filepath, base, ext )

        print "<br/>"

        if cfg.allow_zipview and (ext == ".zip"):
            print '<a href="?path=%s&zipfile=%s">view ZIP file</a>' % \
                ( urllib.quote(self.relativ_path) , urllib.quote(filename) )
            print "<br/>"

        print "<br/>"

        item_stat = os.stat( absolute_filepath )
        print "<small>%s</small>" % time.strftime(
                '%d.%m.%Y %H:%M',
                time.localtime(item_stat[stat.ST_MTIME])
            )
        print "<br/>"

        file_KBytes = item_stat[stat.ST_SIZE]/1024.0
        try:
            locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
            print "%s KB" % locale.format("%0.1f", file_KBytes, True)
        except:
            print "%0.1f KB" % file_KBytes

        if cfg.use_sql_statistic == True:
            print "<br/>"
            print cfg.file_count_txt % self.statistic.only_get_count( self.root_path, filename )

        print "</li>"


    def print_footer( self ):
        """zurück-Link + HTML-Fussdaten"""
        print '<hr id="gallery_clear">'

        # zurück-Link
        cfg.footer_backlink["txt"] = cgi.escape( cfg.footer_backlink["txt"] )
        print cfg.footer_backlink_code % cfg.footer_backlink

        print '<div id="gallery_footer">'
        print "Generated by %s" % __info__
        print "| render time %0.2fsec." % (time.time() - start_time)
        print "</div></body></html>"


    ##_____________________________________________________________________________
    ## Zusätzliche Funktionen

    def download_proxy( self, filename ):
        abs_filepath = os.path.join( os.environ["DOCUMENT_ROOT"], cfg.base_path, filename )
        abs_filepath = os.path.normpath( abs_filepath )

        abs_path, filename = os.path.split( abs_filepath )

        self.check_absolute_path( abs_path )

        #~ print 'Content-Type: text/html\n\n<pre>' # Debug

        try:
            charset = self.get_charset( abs_filepath )
        except:
            charset = []

        #~ print 'Cache-Control: no-cache, must-revalidate'
        #~ print 'Pragma: no-cache'
        print 'Content-Length: %s' % os.path.getsize( abs_filepath )
        print 'Content-Disposition: attachment; filename=%s' % filename
        print 'Content-Transfer-Encoding: binary'
        if charset != []:
            print 'Content-Type: text/plain; charset=%s\n' % charset
        else:
            print 'Content-Type: text/plain\n'

        f = file( abs_filepath, "rb" )
        while True:
            # In Blöcken, die Datei rausprinten...
            data = f.read(8192)
            if not data:
                break
            sys.stdout.write(data)
        f.close()

        if cfg.use_sql_statistic == True:
            # Counter um eins erhöhen
            self.statistic.count( self.root_path, filename )

        sys.exit()

    def print_img_view( self, img_name ):
        """ Anzeigen eines angeklickten Bildes """

        if cfg.use_sql_statistic == True:
            # Aktueller Counterwert, wird in DB um eins erhöht
            count = self.statistic.count( self.root_path, img_name )

        print '<a href="?path=%s&next_img=%s" title="next &gt;" id="img_view">' % (
            urllib.quote(self.relativ_path), urllib.quote(img_name)
        )
        print '<img src="%s"/><br/>' % os.path.join( self.relativ_path, img_name )
        print '%s<br/>' % img_name
        print "<small>Counter: %s</small>" % count
        print '</a>'

    def handle_next_img( self, old_img_name ):
        """ Das nächste Bild soll angezeigt werden """

        files, dirs = self._read_dir()

        if not old_img_name in files:
            # Der alte Name ist wohl falsch -> Normale Seite aufbauen
            self.print_body( files, dirs )
            return

        current_pos = files.index( old_img_name )

        try:
            next_img = files[ current_pos + 1 ]
        except IndexError:
            # Kein neues Image vorhanden -> Normale Seite aufbauen
            self.print_body( files, dirs )
            return

        base, ext = os.path.splitext( next_img )
        if self._is_gallery_img( base, ext ) == False:
            # Aktuelle Datei ist kein Gallery-Bild -> Normale Seite aufbauen
            self.print_body( files, dirs )
            return

        # Alles klar, nächstes Bild wird gezeigt
        self.print_back_link()
        self.print_img_view( next_img )
        self.print_back_link()









