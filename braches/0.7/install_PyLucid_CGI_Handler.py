#!/usr/bin/python
# -*- coding: UTF-8 -*-

#~ print "Content-type: text/html; charset=utf-8\r\n"
import cgitb;cgitb.enable()

from install_PyLucid_app import app

try:
    from install_PyLucid_app import exports
except ImportError:
    exports = {}

from colubrid.server import CGIServer
from colubrid.debug import DebuggedApplication

if __name__ == "__main__":
    CGIServer(DebuggedApplication(app), exports).run()
