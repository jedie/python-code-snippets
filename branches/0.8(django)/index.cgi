#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
index CGI file.

If settings.DEBUG is ON:
  - all write to stdout+stderr are checked. It's slow!
  - Its guaranteed that a HTML Header would be send first.
"""

#print "Content-type: text/html; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#print "Content-type: text/plain; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#import cgitb;cgitb.enable()

import os

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

def traceback_end():
    """
    Print out a traceback and terminate with sys.exit()
    """
    print
    print "-"*80
    try:
        import sys, traceback
        print traceback.format_exc()
    except Exception, e:
        print "Error: %s" % e
    sys.exit()


try:
    from PyLucid.settings import DEBUG
except Exception, e:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "Low-Level-Error!"
    print
    print "Can't import 'settings':", e
    print
    print "You must rename ./PyLucid/settings-example.py to ./PyLucid/settings.py"
    print
    print "You must setup this file for your config!"
    traceback_end()


if DEBUG:
    import sys, cgi, inspect

    class BaseOut(object):
        """
        Base class for HeaderChecker and StdErrorHandler
        -global header_send variable
        """
        oldFileinfo = ""
        header_send = False
        def send_info(self):
            """
            Write information about the file and line number, from which the
            message comes from.
            """
            stack = inspect.stack()[1]
            fileinfo = (stack[1].split("/")[-1][-40:], stack[2])

            if fileinfo != self.oldFileinfo:
                # Send the fileinfo only once.
                self.oldFileinfo = fileinfo
                self.out.write(
                    "<br />[stdout/stderr write from: ...%s, line %s]\n" % fileinfo
                )

        def isatty(self):
            return False
        def flush(self):
            pass

    HEADERS = ("content-type:", "status: 301")#, "status: 200")
    class HeaderChecker(BaseOut):
        """
        Very slow! But in some case very helpfully ;)
        Check if the first line is a html header. If not, a header line will
        be send.
        """
        def __init__(self, out):
            self.out = out

        def check(self, txt):
            txt_lower = txt.lower()
            for header in HEADERS:
                if txt_lower.startswith(header):
                    return True
            return False

        def write(self, *txt):
            txt = " ".join([i for i in txt])
            if self.header_send:
                # headers was send in the past
                pass
            elif self.check(txt) == True:
                # the first Line is a header line -> send it
                self.header_send = True
            else:
                self.wrong_header_info()
                txt = cgi.escape(txt)

            self.out.write(txt)

        def wrong_header_info(self):
            # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
            self.out.write("Content-type: text/html; charset=utf-8\r\n\r\n")
            self.out.write("Wrong Header!!!\n")
            self.header_send = True
            self.send_info()

    class StdErrorHandler(BaseOut):
        """
        redirects messages from stderr to stdout.
        Sends a header, if the header were not already sent.
        """
        def __init__(self, out):
            self.out = out
            self.header_send = False

        def write(self, *txt):
            txt = " ".join([i for i in txt])
            if not self.header_send:
                self.out.write("Content-type: text/html; charset=utf-8\r\n\r\n")
                self.out.write("Write to stderr!!!\n")
                self.header_send = True

            self.send_info()
            self.out.write("<pre>%s</pre>" % txt)

    old_stdout = sys.stdout
    sys.stdout = HeaderChecker(old_stdout)
    sys.stderr = StdErrorHandler(old_stdout)
#_____________________________________________________________________________


# Add a custom Python path, you'll want to add the parent folder of
# your project directory. (Optional.)
#BASE_PATH = os.path.abspath(os.path.dirname(__file__))
#sys.path.insert(0, BASE_PATH)

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/django/PyLucid/")

try:
    #~ from django.core.servers.cgi import runcgi
    # Normaly the cgi_server.py should be saved in dajngo/core/servers
    # But we used svn:externals to include the django source ;)
    from cgi_server import runcgi
except Exception, e:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "<h1>Error:</h1><h2>Can't import the CGI Server:</h2>"
    print "<h3>%s</h3>" % e
    traceback_end()

# Run PyLucid for one request:
try:
    runcgi()
except Exception, e:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "Low-Level-Error:", e
    print
    print "-"*80
    print
    if str(e) == "no such table: django_session":
        print "You must install PyLucid first. Go into the _install section."
        print
        print "Deactivate temporaly the MIDDLEWARE_CLASSES:"
        print " - django.contrib.sessions.middleware.SessionMiddleware"
        print " - django.contrib.auth.middleware.AuthenticationMiddleware"
        print
        print "After 'syncdb' you must activate the middleware classes!"

    traceback_end()