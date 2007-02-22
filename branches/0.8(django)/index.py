#!/usr/bin/python

#_____________________________________________________________________________
print "Content-type: text/html; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
import cgitb;cgitb.enable
import sys, inspect
class PrintLocator(object):
    """
    Very slow! But in some case very helpfully ;)
    """
    def __init__(self, out):
        self.out = out
        self.oldFileinfo = ""

    def write(self, *txt):
        # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
        stack = inspect.stack()[1]
        fileinfo = (stack[1].split("/")[-1][-40:], stack[2])

        if fileinfo != self.oldFileinfo:
            self.oldFileinfo = fileinfo
            self.out.write(
                "<br />[stdout/stderr write from: ...%s, line %s]\n" % fileinfo
            )

        txt = " ".join([str(i) for i in txt])
        self.out.write(txt)

    def isatty(self):
        return False

old_stdout = sys.stdout
sys.stdout = sys.stderr = PrintLocator(old_stdout)
#_____________________________________________________________________________


import sys, os


# Add a custom Python path, you'll want to add the parent folder of
# your project directory.
#sys.path.insert(0, "/home/user/django/")

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/django/myproject/")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

#~ from django.core.servers.cgi import runcgi
from cgi_server import runcgi
runcgi()