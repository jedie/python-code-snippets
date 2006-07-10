#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This CGI-Handler is for Python 2.4, without 'debugged application'!

You can rename this file! For example to 'index.py'
"""

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
#~ import cgitb;cgitb.enable()
import sys

from PyLucid import PEP333_WSGI_CGIServer as CGIServer

#~ from colubrid.debug import DebuggedApplication


if __name__ == "__main__":
    oldstdout = sys.stdout
    sys.stdout = sys.stderr

    # with 'debugged application':
    #~ app = DebuggedApplication('PyLucid_app:app')

    # without 'debugged application':
    from PyLucid_app import app

    sys.stdout = oldstdout

    CGIServer.run_with_cgi(app)
