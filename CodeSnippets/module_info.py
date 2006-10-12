#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Python Module Info CGI

Zeigt alle installierten Module an und gibt details dazu aus.

Zur Info:
In PyLucid gibt es diese Modul in einer besseren Variante
schon eingebaut: http://www.pylucid.org
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.python-forum.de/viewtopic.php?t=3816"
__version__ = "0.4"

__history__ = """
v0.4
    - Geht nun auch, wenn modPython (?) im Spiel ist!
v0.3.1
    - Mehr Info's am Ende der Seite
v0.3
    - spuckt auch in moduleinfo den help() Text aus
v0.2
    - Informationen eines Moduls können angezeigt werden
    - umgebaut zum CGI Progie
v0.1
    - erste Version
"""

import cgitb;cgitb.enable()
print "Content-type: text/html; charset=utf-8\r\n"
print "<h1>Module Info v%s</h1>" % __version__


import os, sys, glob, imp


class modules:
    """
    Auflisten aller installierten Module
    """
    def __init__( self ):
        self.glob_suffixes = self.get_suffixes()

        filelist = self.scan()
        modulelist = self.test( filelist )
        self.print_result( modulelist )

    def get_suffixes( self ):
        """
        Liste aller Endungen aufbereitet für glob()
        """
        suffixes = ["*"+i[0] for i in imp.get_suffixes()]
        suffixes = "[%s]" % "|".join(suffixes)
        return suffixes

    def get_files( self, path ):
        """
        Liefert alle potentiellen Modul-Dateien eines Verzeichnisses
        """
        files = []
        for suffix in self.glob_suffixes:
            searchstring = os.path.join( path, suffix )
            files += glob.glob(searchstring)
        return files

    def scan( self ):
        """
        Verzeichnisse nach Modulen abscannen
        """
        filelist = []
        pathlist = sys.path
        for path_item in pathlist:
            if not os.path.isdir( path_item ):
                continue

            for file in self.get_files( path_item ):
                file = os.path.split( file )[1]
                if file == "__init__.py":
                    continue

                filename = os.path.splitext( file )[0]

                if filename in filelist:
                    continue
                else:
                    filelist.append( filename )

        return filelist

    def test( self, filelist ):
        """
        Testet ob alle gefunden Dateien auch als Modul
        importiert werden können
        """
        modulelist = []
        for filename in filelist:
            try:
                imp.find_module( filename )
            except:
                continue
            modulelist.append( filename )
        return modulelist

    def print_result( self, modulelist ):
        """
        Anzeigen der Ergebnisse
        """
        print '<table>'
        Link = '<a href="%s?' % os.environ['REQUEST_URI']
        Link += '%s">more Info</a>'
        modulelist.sort()
        for modulename in modulelist:
            print "<tr>"
            print "<td>%s</td>" % modulename
            print "<td>%s</td>" % Link % modulename
            print "</tr>"
        print "</table>"
        print "%s Modules found." % len( modulelist )



class moduleinfo:
    """
    Information über ein bestimmtes Modul anzeigen
    """
    def __init__( self, module_name, backurl ):
        self.print_info( module_name, backurl )

    def print_info( self, module_name, backurl ):
        try:
            t = imp.find_module( module_name )
        except Exception,e:
            print "Can't import '%s':" % module_name
            print e
            return
        print "<ul>"
        print "<li>pathname: %s</li>" % t[1]
        print "<li>description: %s</li>" % str(t[2])
        print "</ul>"

        print backurl

        try:
            module = __import__( module_name )
        except Exception,e:
            self.response.write("<p>Can't import module ;(</p>")
            return

        print "<h4>help:</h4>"
        print "<hr /><pre>"
        help(module)
        print "</pre><hr />"

        print backurl

        print "<h4>SourceCode:</h4>"
        filehandle = t[0]
        print "<hr /><pre>"
        for i in filehandle:
            sys.stdout.write( i )
        print "</pre><hr />"

        print backurl


def print_information():
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


#~ print_information()


if __name__ != "__main__":
    # Kann passieren, wenn das Skript nicht als CGI läuft, sondern
    # evtl. über modPython
    print "<hr /><h1>Error:</h1>"
    print "<p>__name__ == %s (should be __main__!)</p>" % __name__
    gateway = os.environ.get(
        "GATEWAY_INTERFACE", "[Error:GATEWAY_INTERFACE not in os.environ!]"
    )
    if gateway!="CGI/1.1":
        print "<h3>Running not as CGI!</h3>"

    print "<p>GATEWAY_INTERFACE: <strong>%s</strong></p>" % gateway
    print "<hr />"



## Nutzt extra kein import-Hook, wie:
##      if __name__ == "__main__":
## damit das Skript auch mit modPython (?) funktioniert


query_string = os.environ["QUERY_STRING"]
if query_string == "":
    # Alle Module auflisten
    print "<h3>module list:</h3>"
    modules()

    # Zusätzliche Informationen ausgeben:
    print "<hr />"
    print_information()
else:
    # Information über ein Modul anzeigen
    backurl = '<p><a href="%s">back</a></p>' % \
        os.environ['REQUEST_URI'].split("?",1)[0]

    moduleinfo( query_string, backurl )


