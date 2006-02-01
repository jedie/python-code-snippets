#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" uploader
used WSGI colubird by Armin Ronacher <armin.ronacher@active-4.com>
http://wsgiarea.pocoo.org/colubrid/


Konfiguration:
==============
 only_https
    Erlaubt nur HTTPs zugriffe, ermittelt mit self.request.environ["HTTPS"] == "on"

 only_auth_users
    Erlaubt nur "eingeloggten" Usern den Zugriff. Dabei ist die Apache-Basic-Auth. mit
    .htaccess und .htpasswd gemeint s. http://httpd.apache.org/docs/2.0/howto/auth.html
    ermittelt mit: self.request.environ.has_key("AUTH_TYPE") and self.request.environ.has_key("REMOTE_USER")

 send_email_notify = True
    Sendet bei jedem gemachten Upload eine eMail mit Informationen.


Beispiel
========
 Damit man nicht in den original Quellen die Config ändern muß, kann man sich einfach eine "Start-Datei"
 bauen und dort die Config ändern. Wie das aussehen kann:
_________________________________________________________________________
import uploader

uploader.cfg.html_title = "Welcome to my super Uploader!"

uploader.cfg.only_https = False
uploader.cfg.only_auth_users = False

uploader.cfg.send_email_notify = True
uploader.cfg.notifer_email_from_adress = "uploader@example.com"
uploader.cfg.notifer_email_to_adress = "uploader@example.com"

app = uploader.uploader
_________________________________________________________________________


Ablauf:
=======
 Zu jeder hoch geladenen Datei wird eine *.nfo-Textdatei erstellt. Diese ist im
 ConfigParser-ini-Format. Es werden Informationen zur Datei gespeichert. u.a.:
    * fileinfo: Ergebniss des Linux 'file'-Befehls
    * client_info: Username (nur bei only_auth_users=True) und socket.getfqdn()-Info

 Beim generieren der Dateiliste werden die *.nfo-Dateien wieder ausgelesen.

Hinweis:
Die Preformance Werte stimmen nicht wirklich...
Also es ist nicht die echte Upload-Geschwindigkeit, sondern die Geschwindigkeit mit der die Datei auf
Platte geschrieben wurde :)
"""

__author__      = "Jens Diemer"
__url__         = "http://www.jensdiemer.de"
__license__     = "GNU General Public License (GPL)"
__description__ = "a small upload-form used WSGI"
__version__     = "0.4 alpha"

__info__        = 'uploader v%s' % __version__

__history__ = """
v0.4
    - Umbau zu einer PathApplication
v0.3
    - Neu: Download der hochgeladenen Dateien möglich, wenn cfg.allow_download == True ist
v0.2
    - Umbau/rewrite für colubird
v0.1.2
    - Small handling changes
v0.1.1
    - Bugfix with filenames from IE
v0.1
    - erste Version
"""

import sys, os, time, socket, ConfigParser, subprocess, urllib, cgi
import posixpath

from colubrid import PathApplication





class cfg:
    """
    Default config
    """
    allow_download = False

    only_https = True
    #~ only_https = False

    only_auth_users = True
    #~ only_auth_users = False

    #~ send_email_notify = True
    send_email_notify = False
    #~ notifer_email_from_adress = os.environ.get("SERVER_ADMIN","")
    #~ notifer_email_to_adress = os.environ.get("SERVER_ADMIN","")

    bufsize = 8192
    upload_dir = "uploads"

    html_head = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
    <title>%(title)s</title>
    %(CSS)s
    </head>
    <body>
    <h2>%(title)s</h2>
    """

    html_title = "File Upload"

    css = """
    <style type="text/css">
    html, body {
        padding: 10px;
        background-color: #EEF8FF;
    }
    body {
        font-family: tahoma, arial, sans-serif;
        color: #000000;
        font-size: 0.9em;
        background-color: #DBF1FF;
        margin: 10px;
        padding: 20px;
        border: 3px solid #3CBFFF;
    }
    table.filelist {
        border: 1px solid #3CBFFF;
    }
    .filelist td {
        padding-left: 5px;
        padding-right: 5px;
    }
    #footer {
      font-size: 0.6em;
      border-top: 1px solid #3CBFFF;
    }
    #footer, #footer a {
      margin-top: 1em;
      color: #3CBFFF;
      text-decoration:none;
      text-align: right;
    }
    </style>
    """

    html_form = """
    <form action="%s" method="post" enctype="multipart/form-data">
        <p><input type="file" name="upload" size="40" />
        <input type="submit" value="upload" /></p>
    </form>"""

    html_footer = """<div id="footer"><p>[only_https: %s, only_auth_users: %s, email_notify: %s]<br />
    <a href="http://www.jensdiemer.de">%s by Jens Diemer</a></p>
    </div></body></html>"""

    email_notify_text = """
    A person '%(client_info)s' used the uploader.

    File information:
    %(fileinfo)s

    --
    This is a automaticly constructed notify message.
    created with %(info)s
    """


class uploader(PathApplication):

    def __init__(self, *args):
        super(uploader, self).__init__(*args)
        self.request.cfg = cfg
        #~ self.request.exposed.append("cfg")


    #_________________________________________________________________________
    ## Haupt-Methoden

    def show_index(self, *args):
        """ Normaler Aufruf des Skriptes """
        self.print_head()
        #~ self.request.debug_info()
        self.write_footer()

    def show_upload(self, *args):
        """ Datei wird hochgeladen """

        self.print_head()

        client_info = self.get_client_info()
        try:
            filename, bytes = self.save_file(self.request.FILES['upload'])
        except CanNotSaveFile, e:
            self.request.write("<h2>ERROR: Can't write file: %s</h2>" % e)
        else:
            self.write_info_file(client_info, filename, bytes)
            self.email_notify()

        self.write_footer()

    def show_download(self, filename):
        """
        Downloaden einer Datei, nur erlaubt, wenn cfg.allow_download == True
        """
        if not self.request.cfg.allow_download:
            raise RightsError("Downloads are not permitted!")

        absolute_filename = os.path.join(self.request.cfg.upload_dir, filename)

        file_handle = file(absolute_filename, "rb")

        self.request.headers['Content-Disposition'] = 'attachment; filename=%s' % filename
        self.request.headers['Content-Length'] = '%s' % os.path.getsize(absolute_filename)
        self.request.headers['Content-Transfer-Encoding'] = 'binary'
        self.request.headers['Content-Type'] = 'application/octet-stream; charset=utf-8'

        while 1:
            data = file_handle.read(self.request.cfg.bufsize)
            if not data:
                break
            self.request.write(data)

    #_________________________________________________________________________

    def get_client_info(self):
        """
        Liefert einen String mit Domain-Namen und evtl. vorhandenen Usernamen zurück
        """
        try:
            client_info = socket.getfqdn(self.request.environ["REMOTE_ADDR"])
        except Exception, e:
            client_info = "Error: %s" % e

        if "REMOTE_USER" in self.request.environ:
            # Usernamen hinzufügen
            client_info = "%s - %s" % (self.request.environ["REMOTE_USER"], client_info)

        return client_info

    def save_file(self, file_object):
        """ Speichert eine gerade hochgeldadene Datei ab """
        filename = file_object.filename
        if filename == "":
            self.request.write("<h1>ERROR: No File!</h1>")
            return

        filename = os.path.basename(filename)
        self.request.write("<h2>File '%s' save...</h2>" % filename)

        filename = os.path.join(self.request.cfg.upload_dir, filename)

        bytesreaded = 0
        try:
            f = file(filename, 'wb')
            time_threshold = start_time = int(time.time())
            while 1:
                data = file_object.read(self.request.cfg.bufsize)
                if not data:
                    break
                bytesreaded += len(data)
                f.write(data)

                current_time = int(time.time())
                if current_time > time_threshold:
                    self.request.write("<p>read: %sBytes (%s)</p>" % (
                            bytesreaded, time.strftime("%H:%M:%S", time.localtime())
                        )
                    )
                    time_threshold = current_time

            end_time = time.time()
            f.close()

            performance = bytesreaded / (end_time-start_time) / 1024
            self.request.write("</h3>saved with %.2fKByes/sec.</h3>" % performance)
        except Exception, e:
            raise CanNotSaveFile(e)

        return filename, bytesreaded

    def view_uploaded_files(self):
        """
        Erzeugt eine Tabelle, der schon hochgeladenen Dateien
        wenn cfg.allow_download == True, dann werden auch die Links zum download eingeblendet
        """
        self.request.write("<h3>Filellist:</h3>")
        try:
            filelist = os.listdir(self.request.cfg.upload_dir)
        except Exception, e:
            self.request.write("Error: Can't read filelist: %s" % e)
            return

        self.request.write('<table class="filelist">\n')
        for filename in filelist:
            if filename.endswith(".nfo"):
                continue
            self.request.write("<tr>\n")

            if self.request.cfg.allow_download:
                url = posixpath.join(
                    self.request.environ.get('SCRIPT_NAME', ''),
                    "download/%s" % urllib.quote_plus(filename)
                )
                html_part = '<a href="%s">%s</a>' % (
                    url, cgi.escape(filename)
                )
            else:
                html_part = cgi.escape(filename)

            self.request.write("\t<td>%s</td>\n" % html_part)

            try:
                client_info, size, fileinfo, upload_time = self.read_info_file(filename)
            except Exception, e:
                self.request.write('\t<td colspan="4"><small>Error, get fileinfo: %s</small></td>\n' % e)
            else:
                self.request.write("\t<td>%s</td>\n" % client_info)
                self.request.write('\t<td align="right">%0.2fKB</td>\n' % (size/1024.0))
                self.request.write("\t<td>%s</td>\n" % upload_time)
                self.request.write("\t<td>%s</td>\n" % fileinfo)

            self.request.write("</tr>\n")
        self.request.write("</table>\n")

    def get_file_info(self, filename):
        """ Datei Information mit Linux 'file' Befehl zusammentragen """
        try:
            proc = subprocess.Popen(
                args        = ["file", filename],
                stdout      = subprocess.PIPE,
                stderr      = subprocess.PIPE
            )
        except Exception, e:
            return "Can't make file subprocess: %s" % e

        try:
            file_cmd_out = proc.stdout.read()
        except Exception, e:
            return "Can't read stdout from subprocess: %s" % e

        proc.stdout.close()

        try:
            file_cmd_out = file_cmd_out.split(":",1)[1]
        except Exception, e:
            return "Can't prepare String: '%s' Error: %s" % (file_cmd_out, e)

        if file_cmd_out.find("ERROR") != -1:
            # Ersatz für >"ERROR" in fileinfo< ;)
            return ""
        else:
            return file_cmd_out

        return mtime, size, file_cmd_out

    #_________________________________________________________________________

    def write_info_file(self, client_info, filename, bytesreaded):
        """ Info-Datei zur hochgeladenen Datei schreiben """
        f = file(filename+".nfo", "wU")
        config = ConfigParser.ConfigParser()
        config.add_section("info")

        config.set("info", "client_info", client_info)
        config.set("info", "filename", filename)
        config.set("info", "bytes", bytesreaded)
        config.set("info", "fileinfo", self.get_file_info(filename))
        config.set("info", "upload_time", time.strftime("%d %b %Y %H:%M:%S", time.localtime()))

        config.write(f)
        f.close()

    def read_info_file(self, filename):
        """ vorhandene Info-Datei lesen (für die Upload-Datei-Tabelle) """
        filename = os.path.join(self.request.cfg.upload_dir, filename)
        f = file(filename+".nfo", "rU")
        config = ConfigParser.ConfigParser()
        config.readfp(f)
        f.close()

        client_info = config.get("info", "client_info")
        size        = int(config.get("info", "bytes"))
        fileinfo    = config.get("info", "fileinfo")
        upload_time = config.get("info", "upload_time")

        return client_info, size, fileinfo, upload_time

    #_________________________________________________________________________

    def email_notify(self):
        """
        Sendet eine eMail, das eine neue Datei hochgeladen wurde
        Nutzt die seperate email-Klasse
        """
        if not self.request.cfg.send_email_notify:
            return

        email().send(
            from_adress = notifer_email_from_adress,
            to_adress   = notifer_email_to_adress,
            subject     = "uploaded: '%s' from '%s'" % (
                filename, client_info
            ),
            text        = email_notify_text % {
                "client_info"   : client_info,
                "fileinfo"      : fileinfo,
                "info"          : "%s (Python v%s)" % (
                    __info__, sys.version
                ),
            }
        )

        self.request.write('<a href="?">continue</a>')

    def check_rights(self):
        """
        Überprüft only_https und only_auth_users
        """
        if self.request.cfg.only_https:
            # Nur https Verbindungen "erlauben"
            if self.request.environ.get("HTTPS", False) != "on":
                raise RightsError("Only HTTPs connections allow!")

        if self.request.cfg.only_auth_users:
            # Der User muß über Apache's basic auth eingeloggt sein
            if not (self.request.environ.has_key("AUTH_TYPE") and \
            self.request.environ.has_key("REMOTE_USER")):
                raise RightsError("Only identified users allow!")

    #_________________________________________________________________________

    def print_head(self):
        """ Header und HTML-Kopf ausgeben und dabei das CSS einbinden """
        self.request.headers['Content-Type'] = 'text/html'

        self.request.echo(
            self.request.cfg.html_head % {
                "CSS"   : self.request.cfg.css,
                "title" : self.request.cfg.html_title
            }
        )

    def write_footer(self):
        """
        Footer anzeigen, bestehent aus:
            - HTML-Form für den Upload
            - Tabelle der schon hochgeladenen Dateien
            - die Konfiguration
        """

        url = posixpath.join(self.request.environ.get('SCRIPT_NAME', ''), "upload")

        # Form zum Uploaden anzeigen
        self.request.write(self.request.cfg.html_form % url)

        # Tabelle der schon hochgeladenen Dateien aufbauen
        self.view_uploaded_files()

        self.request.write(
            self.request.cfg.html_footer % (
                self.request.cfg.only_https,
                self.request.cfg.only_auth_users,
                self.request.cfg.send_email_notify,
                __info__
            )
        )






class email:
    """
    Kleine Hilfsklasse um Text-EMails zu versenden
    """
    def send(self, from_adress, to_adress, subject, text):
        import time, smtplib
        from email.MIMEText import MIMEText

        msg = MIMEText(
            _text = text,
            _subtype = "plain",
            _charset = "UTF-8"
        )
        msg['From'] = from_adress
        msg['To'] = to_adress
        msg['Subject'] = subject
        # Datum nach RFC 2822 Internet email standard.
        msg['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        msg['User-Agent'] = "%s (Python v%s)" % (__info__, sys.version)

        s = smtplib.SMTP()
        s.connect()
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.close()



class CanNotSaveFile(Exception):
    """
    Datei könnte nicht auf Platte geschrieben werden
    """
    pass

class RightsError(Exception):
    """
    Die Zugangsberechtigung ist nicht vorhanden
    """
    pass
