#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.python-forum.de/viewtopic.php?t=3816"
__version__ = "0.2"

__history__ = """
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

        print "SourceCode:"
        filehandle = t[0]
        print "<hr><pre>"
        for i in filehandle:
            sys.stdout.write( i )
        print "</pre><hr>"

        print backurl

if __name__ == "__main__":
    #~ print "<pre>"
    #~ for i,v in os.environ.iteritems(): print i,v
    #~ print "</pre>"

    query_string = os.environ["QUERY_STRING"]
    if query_string == "":
        # Alle Module auflisten
        modules()
    else:
        # Information über ein Modul anzeigen
        backurl = '<p><a href="%s">back</a></p>' % \
            os.environ['REQUEST_URI'].split("?",1)[0]

        moduleinfo( query_string, backurl )