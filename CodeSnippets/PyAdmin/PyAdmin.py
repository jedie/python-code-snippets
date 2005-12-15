#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

"""
    install     - Install PyAdmin as inetd services
    deinstall   - DeInstall PyAdmin (inetd services)
    start       - Start stand alone PyAdmin server
    stop        - Stops a runing stand alone PyAdmin server

install, deinstall not supported yet.

/etc/services
PyAdmin     9000/tcp

/etc/inetd.conf
PyAdmin 	stream	tcp	nowait	root	/.../PyAdminInetdServer.py PyAdminInetdServer

"""

import sys, os, optparse


__version__ = "0.1.0"


print """
  %s v%s (GNU General Public License) - by www.jensdiemer.de
""" % (__file__, __version__)



def install():
    "als inetd Service einrichten"
    OptParser.error("not supported yet!")

def deinstall():
    "als inetdService deinstallieren"
    OptParser.error("not supported yet!")



def start_server():
    # Ausgelagerte .py-Dateien in den Pfad aufnehmen
    sys.path.append( os.path.join( os.getcwd(), "routines" ) )

    from routines import PyAdminCGIHTTPServer

    print "Starte Server..."

    PyAdminCGIHTTPServer.ServerStart()


def stop_server():
    "ps -C PyAdmin.py -o pid="
    pid_list = os.popen("ps -C PyAdmin.py").read()#.splitlines()
    print pid_list

    from routines import config

    cfg = config.Parser()

    cfg.set_section( "Server" )
    ListenPort  = cfg.get( "ListenPort", "int" )

    shutdown_url = "http://127.0.0.1:%s/routines/ServerShutdownCGI.py" % ListenPort

    print "Server shutdown:"
    print shutdown_url

    import urllib2
    urllib2.urlopen( shutdown_url )


    pid_list = os.popen("ps -C PyAdmin.py").read()#.splitlines()
    print pid_list




if __name__ == "__main__":
    OptParser = optparse.OptionParser( usage = __doc__ )

    options, args = OptParser.parse_args()

    if len(args) != 1:
        OptParser.error("wrong argument!")

    action = args[0]

    if action == "install":
        #~ install()
    elif action == "deinstall":
        #~ deinstall()
    elif action == "start":
        start_server()
    elif action == "stop":
        stop_server()
    else:
        OptParser.error("wrong argument!")



