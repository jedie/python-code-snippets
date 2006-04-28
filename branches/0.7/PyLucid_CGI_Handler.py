#!/usr/bin/python
# -*- coding: UTF-8 -*-

#~ print "Content-type: text/html; charset=utf-8\r\n"
#~ import cgitb;cgitb.enable()


from PyLucid import PEP333_WSGI_CGIServer as CGIServer

from colubrid.debug import DebuggedApplication


if __name__ == "__main__":
    app = DebuggedApplication('PyLucid_app:app')
    CGIServer.run_with_cgi(app)
