#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import generators

#~ print "Content-type: text/html; charset=utf-8\r\n\r\n<pre>DEBUG:"
import cgitb;cgitb.enable()

from PyLucid.python_backports import backports

import sys

from PyLucid import PEP333_WSGI_CGIServer as CGIServer

from colubrid.debug import DebuggedApplication


if __name__ == "__main__":
    oldstdout = sys.stdout
    sys.stdout = sys.stderr

    app = DebuggedApplication('PyLucid_app:app')
    #~ from PyLucid_app import app

    sys.stdout = oldstdout

    CGIServer.run_with_cgi(app)
