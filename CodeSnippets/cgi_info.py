#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cgitb; cgitb.enable() # Debugging für CGI-Skripte 'einschalten'

print "Content-Type: text/html; charset=utf-8\n"
print "<h1>Hello World!</h1>"
print "<hr/>"

import sys, os

print "<h3>Python v%s</h3>" % sys.version

print "<h3>os.uname():</h3>%s<br />" % " - ".join(os.uname())
print "<h3>sys.path:</h3>"
sys_path = sys.path[:]
sys_path.sort()
for p in sys_path:
    print "%s<br />" % p

print "<h3>OS-Enviroment:</h3>"
print '<dl id="environment">'
keys = os.environ.keys()
keys.sort()
for key in keys:
    value = os.environ[key]
    print "<dt>%s</dt>" % key
    print "<dd>%s</dd>" % value
print "</dl>"
