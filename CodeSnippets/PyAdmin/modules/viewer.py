#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.1"

import cgitb ; cgitb.enable()
import os, sys, locale, urllib


import CGIdata
import menu






def error( msg ):
    print "<h2>%s</h2>" % msg
    print htmlPost
    sys.exit()


def start_module( selfURL ):
    if not CGIdata.has_key("file"):
        menu.Menu() # HTML-Seite aufbauen
        error( "no filename!" )

    filename = urllib.unquote( CGIdata["file"] )

    menu.cfg.title = "Viewer [%s]" % filename
    menu.Menu() # HTML-Seite aufbauen

    if not os.path.isfile( filename ):
        error( "File [%s] does not exists!" % filename )

    print "<h3>%s</h3>" % filename

    print "<hr><pre>"

    f = file( filename, "r" )
    while 1:
        line = f.readline()
        if line == "": break
        print line

    print "</pre><hr>"

    menu.print_footer()




if __name__ == "__main__":
    CGIdata = CGIdata.GetCGIdata()
    selfURL = os.environ['SCRIPT_NAME']
    start_module( selfURL )

def inetd_start():
    "durch inetd-Server gestartet"
    selfURL = "viewer"
    start_module( selfURL )









