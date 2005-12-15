#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" uploader
used WSGI: http://wsgiarea.pocoo.org by Armin Ronacher <armin.ronacher@active-4.com>

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! NOTE: Please change the notifer email adress to you own !!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Konfiguration:
==============
 only_https
    Erlaubt nur HTTPs zugriffe, ermittelt mit os.environ["HTTPS"] == "on"

 only_auth_users
    Erlaubt nur "eingeloggten" Usern den Zugriff. Dabei ist die Apache-Basic-Auth. mit
    .htaccess und .htpasswd gemeint s. http://httpd.apache.org/docs/2.0/howto/auth.html
    ermittelt mit: os.environ.has_key("AUTH_TYPE") and os.environ.has_key("REMOTE_USER")

 send_email_notify = True
    Sendet bei jedem gemachten Upload eine eMail mit Informationen.

Ablauf:
=======
 Zu jeder hoch geladenen Datei wird eine *.nfo-Textdatei erstellt. Diese ist im
 ConfigParser-ini-Format. Es werden Informationen zur Datei gespeichert. u.a.:
    * fileinfo: Ergebniss des Linux 'file'-Befehls
    * client_info: Username (nur bei only_auth_users=True) und socket.getfqdn()-Info

 Beim generieren der Dateiliste werden die *.nfo-Dateien wieder ausgelesen.

Hinweis:
Die Preformance Werte stimmen nicht wirklich...
Also es ist nicht die echte Upload-Geschwindigkeit.
"""

__author__      = "Jens Diemer"
__url__         = "http://www.jensdiemer.de"
__license__     = "GNU General Public License (GPL)"
__description__ = "a small upload-form used WSGI"
__version__     = "0.1"

__info__        = 'uploader v%s' % __version__

__history__ = """
v0.1.1
    - Bugfix with filenames from IE
v0.1
    - erste Version
"""

from __future__ import generators

import sys, os, time, socket, ConfigParser

from wsgi.middlewares import debug; debug.cgi_debug()
from wsgi.wrappers.basecgi import WSGIServer

from wsgi import tools, http


#~ print "Content-type: text/html; charset=utf-8\r\n" # Debugging
#~ print "<pre>"
#~ for k,v in os.environ.iteritems(): print k,v
#~ print "</pre>"


only_https = True
#~ only_https = False
only_auth_users = True
#~ only_auth_users = False
#~ send_email_notify = True
send_email_notify = False
notifer_email_from_adress = "auto_mailer@htfx-mirror.de"
notifer_email_to_adress = "uploader@jensdiemer.de"
bufsize = 8192
upload_dir = "uploads"




html_head = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>File Upload</title>
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
</head>
<body>"""


html_form = """
    <h1>File Upload</h1>
    <form action="" method="post" enctype="multipart/form-data">
        <p><input type="file" name="upload" size="40" />
        <input type="submit" value="upload" /></p>
    </form>"""


html_footer = """<div id="footer"><p>[only_https: %s, only_auth_users: %s, email_notify:%s]<br />
<a href="http://www.jensdiemer.de">%s by Jens Diemer</a></p>
</div></body></html>""" % (only_https, only_auth_users, send_email_notify, __info__)


email_notify_text = """
A person '%(client_info)s' used the uploader.

File information:
%(fileinfo)s

--
This is a automaticly constructed notify message.
created with %(info)s
"""




class Application:

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def incoming(self, formdata):
        try:
            client_info = socket.getfqdn(os.environ["REMOTE_ADDR"])
        except Exception, e:
            client_info = "Error: %s" % e

        if only_auth_users == True:
            # Usernamen hinzufügen
            client_info = "%s - %s" % (os.environ["REMOTE_USER"], client_info)

        filename = formdata['upload']['filename']
        if filename == "":
            yield "<h2>ERROR: No File!</h2>"
            yield '<a href="?">continue</a>'
            return

        # IE unter Windows, schickt den Pfad mit
        filename = filename.replace("\\","/")
        filename = os.path.basename(filename)
        yield "<h2>File '%s' save...</h2>" % filename

        filename = os.path.join(upload_dir, filename)

        file_obj = formdata['upload']['descriptor']
        bytesreaded = 0
        try:
            f = file(filename, 'wb')
            time_threshold = start_time = int(time.time())
            while 1:
                data = file_obj.read(bufsize)
                if not data:
                    break
                bytesreaded += len(data)
                f.write(data)

                current_time = int(time.time())
                if current_time > time_threshold:
                    yield "<p>read: %sBytes (%s)</p>" % (
                        bytesreaded, time.strftime("%H:%M:%S", time.localtime())
                    )
                    time_threshold = current_time

            end_time = time.time()
            f.close()

            performance = bytesreaded / (end_time-start_time) / 1024
            yield "</h3>saved with %.2fKByes/sec.</h3>" % performance
        except Exception, e:
            yield "<h2>ERROR: Can't write file: %s</h2>" % e
            return
        else:
            try:
                self.write_info_file(client_info, filename, bytesreaded)
                f = file(filename+".nfo", "rU")
                fileinfo = f.read()
                f.close()
            except Exception, e:
                yield "<h2>ERROR: Can't write info file: %s</h2>" % e
                fileinfo = "ERROR: %s" % e

        if send_email_notify == True:
            email().send(
                from_adress = notifer_email_from_adress,
                to_adress   = notifer_email_to_adress,
                subject     = "uploaded: '%s' from '%s'" % (filename, client_info),
                text        = email_notify_text % {
                    "client_info"   : client_info,
                    "fileinfo"      : fileinfo,
                    "info"          : "%s (Python v%s)" % (__info__, sys.version),
                }
            )

        yield '<a href="?">continue</a>'

    def view_uploaded_files(self):
        yield "<h2>Filellist:</h2>"

        yield '<table class="filelist">\n'
        for filename in os.listdir(upload_dir):
            if filename.endswith(".nfo"):
                continue
            yield "<tr>\n"
            yield "\t<td>%s</td>\n" % filename

            try:
                client_info, size, fileinfo, upload_time = self.read_info_file(filename)
            except Exception, e:
                yield '\t<td colspan="4"><small>Error, get fileinfo: %s</small></td>\n' % e
            else:
                yield "\t<td>%s</td>\n" % client_info
                yield '\t<td align="right">%0.2fKB</td>\n' % (size/1024.0)
                yield "\t<td>%s</td>\n" % upload_time
                yield "\t<td>%s</td>\n" % fileinfo

            yield "</tr>\n"
        yield "</table>\n"

    def get_file_info(self, filename):
        """ Datei Information mit Linux 'file' Befehl zusammentragen """
        file_cmd_out = os.popen("file '%s'" % filename).readlines()[0]
        file_cmd_out = file_cmd_out.split(":",1)[1]
        return file_cmd_out

        if file_cmd_out.find("ERROR") != -1:
            # Ersatz für >"ERROR" in fileinfo< ;)
            return ""
        else:
            return file_cmd_out

        return mtime, size, file_cmd_out

    def write_info_file(self, client_info, filename, bytesreaded):
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
        filename = os.path.join(upload_dir, filename)
        f = file(filename+".nfo", "rU")
        config = ConfigParser.ConfigParser()
        config.readfp(f)
        f.close()

        client_info = config.get("info", "client_info")
        size        = int(config.get("info", "bytes"))
        fileinfo    = config.get("info", "fileinfo")
        upload_time = config.get("info", "upload_time")

        return client_info, size, fileinfo, upload_time

    def __iter__(self):
        self.start_response(http.get_status(200), [('Content-Type', 'text/html')])
        yield html_head

        if only_https == True:
            # Nur https Verbindungen "erlauben"
            if os.environ.get("HTTPS", False) != "on":
                yield "<h2>Error: Only HTTPs connections allow!</h2>"
                link = "https://%s%s" % (os.environ["HTTP_HOST"], os.environ["SCRIPT_NAME"])
                yield '<h4>try: <a href="%s">%s</a></h4>' % (link, link)
                yield html_footer
                return

        if only_auth_users == True:
            # Der User muß über Apache's basic auth eingeloggt sein
            if not (os.environ.has_key("AUTH_TYPE") and os.environ.has_key("REMOTE_USER")):
                yield "<h2>Error: Only identified users allow!</h2>"
                yield html_footer
                return

        params = tools.get_parameters(self.environ)
        if not 'do' in params or params['do'] == 'upload':
            formdata = tools.get_files(self.environ)
            if formdata:
                for line in self.incoming(formdata): yield line
            else:
                yield html_form
                for line in self.view_uploaded_files(): yield line

        else:
            raise RuntimeError, 'Invalid Request'

        yield html_footer



class email:
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


#___________________________________________________________________________

if __name__ == '__main__':
    app = Application
    WSGIServer(app).run()

