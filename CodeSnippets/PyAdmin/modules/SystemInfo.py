#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.1"



## Revisions-History
# v0.0.1
#   - Erste Version






import cgitb ; cgitb.enable()
import os, sys, subprocess, time

# Eigene Module
import CGIdata, config, thread_subprocess
import menu



process_timeout = 1



def cmd( command ):
    subIO = thread_subprocess.subprocessIO()
    MySubprocess = thread_subprocess.subprocess2( command, "/", subIO )
    MySubprocess.start()                    # thread starten
    MySubprocess.join(process_timeout)      # ...laufen lassen...
    MySubprocess.stop()                     # Prozess evtl. abbrechen

    return subIO.get()


class SystemInfo:
    def __init__( self ):
        print "<h1>SystemInfo</h1>"
        print " - ".join( os.uname() )
        self.print_cmd( "uptime" )

        self.print_cmd( "who -H -u -l", "Angemeldete Benutzter" )

        self.print_cmd( "df -T -h", "Plattenplatz" )
        self.print_cmd( "free -m", "RAM Belegung in MB" )

        self.tail( "/var/log/syslog" )
        self.tail( "/var/log/daemon.log" )
        self.tail( "/var/log/auth.log" )

        self.print_cmd( "netstat -vplan", "Netzwerkverbindungen" )


    def print_cmd( self, command, info = "" ):
        if info != "": info = "%s: " % info
        print "<h3>%s%s</h3>" % ( info, command )
        print "<pre>"
        print cmd( command )
        print "</pre>"

    def tail( self, filename, max = 5 ):
        """
        Gibt die letzten >max<-Zeilen einer Datei aus
        """
        print "<h3>%s</h3>" % filename

        f = file(filename, "r")
        seekpos = -80*max
        if seekpos<0:
            seekpos = 0
        f.seek( seekpos, 2)
        print "<pre>"
        print " ".join( f.readlines()[-max:] )
        print "</pre>"



def start_module( selfURL ):
    menu.cfg.title      = "SystemInfo"
    menu.Menu()

    SystemInfo()

    menu.print_footer()



if __name__ == "__main__":
    selfURL = os.environ['SCRIPT_NAME']

    CGIdata = CGIdata.GetCGIdata()

    start_module( selfURL )


def inetd_start():
    "durch inetd-Server gestartet"
    selfURL = "SystemInfo"

    start_module( selfURL )

