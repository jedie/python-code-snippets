#!/usr/bin/python

#print "Content-type: text/html; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#print "Content-type: text/plain; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#import cgitb;cgitb.enable()

import sys, os

# Add a custom Python path, you'll want to add the parent folder of
# your project directory. (Optional.)
#BASE_PATH = os.path.abspath(os.path.dirname(__file__))
#sys.path.insert(0, BASE_PATH)

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/django/PyLucid/")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "PyLucid.settings"

from django.core.servers.fastcgi import runfastcgi
#~ runfastcgi(daemonize="false", method="threaded")
runfastcgi(daemonize="false", socket="fcgi.sock")
