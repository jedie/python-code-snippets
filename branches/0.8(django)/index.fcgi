#!/usr/bin/python

print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
import cgitb;cgitb.enable

import sys, os

from os.path import join, dirname, abspath
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Add a custom Python path.
sys.path.insert(0, BASE_PATH)

# Switch to the directory of your project. (Optional.)
#os.chdir("/home/jens/servershare/www/0.8(django)")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

from django.core.servers.fastcgi import runfastcgi
#~ runfastcgi(method="threaded", daemonize="false")
runfastcgi(daemonize="false", socket="fcgi.sock")
