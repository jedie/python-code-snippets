#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-


import os, sys, urllib

def GetCGIdata():
    """
    CGI POST und GET Daten zur einfacheren Verarbeitung zusammen in ein Dict packen
    (bei normalen CGIHTTP-Server oder Apache!)
    """
    CGIdata={}
    if os.environ.has_key('QUERY_STRING'):
        # GET URL-Parameter parsen
        for i in os.environ['QUERY_STRING'].split("&"):
            i=i.split("=")
            if len(i)==1:
                if i[0]!="":
                    CGIdata[ i[0] ] = ""
            else:
                CGIdata[ i[0] ] = i[1]

    from cgi import FieldStorage
    FieldStorageData = FieldStorage()
    # POST Daten auswerten
    for i in FieldStorageData.keys():
        CGIdata[i]=FieldStorageData.getvalue(i)

    return CGIdata






class CGI_data_Parser:
    """
    parsen/speichern und abrufen der POST/GET Daten
    """
    def __init__( self ):
        self.data = {}
        self.content_length_bytes = 0

    def content_length( self, content_length_line ):
        "Holt sich die POST-Daten aus dem HTML-Header"
        self.content_length_bytes = int( content_length_line.split(":")[1] )

    def parse_POST_data( self ):
        "Eine POST-Zeile in self.data speichern"

        POST_data = sys.stdin.read( self.content_length_bytes )

        if not "&" in POST_data: return

        POST_data = urllib.unquote( POST_data.replace('+', ' ') )

        for i in POST_data.split("&"):
            item = i.split("=")
            if len(item) == 2:
                self.data[ item[0] ] = item[1]
            else:
                print "CGI_data_Parser Fehler:", item, POST_data

    def parse_GET_data( self, path ):
        "ermittelt die GET-Daten aus der Request-Zeile und speicher sie in self.data"

        # GET-Daten vorhanden ?
        if not "?" in path: return

        GET_data = path.split("?")[1]
        GET_data = GET_data.rsplit(" ",1)[0]

        for item in GET_data.split("&"):
            item = item.split("=")
            if len(item) == 2:
                self.data[ item[0] ] = item[1]
            else:
                self.data[ item[0] ] = ""

    def get_data( self ):
        return self.data


class environ_data_Parser:
    """
    Speichert die environ-Daten
    """
    def __init__( self ):
        self.data = {}

    def parse( self, line ):
        line = line.split(":")
        line = [i.strip() for i in line]
        if len(line) == 2:
            #~ os.environ[ line[0] ] = line[1]
            self.data[ line[0] ] = line[1]

    def get_data( self ):
        return self.data


if __name__ == "__main__":
    print "HTTP/1.1 200 OK"
    print "Content-Type: text/html\n"

    print "<hr><pre>"

    MyCGIdata       = CGI_data_Parser()
    MyEnvironData   = environ_data_Parser()


    for i in xrange(20):
        line = sys.stdin.readline()
        if line == "\r\n": break

        MyEnvironData.parse( line )

        if "POST" in line:
            MyCGIdata.parse_GET_data( line )
        elif "content-length" in line.lower():
            MyCGIdata.content_length( line )
        print line.replace("\n","")

    MyCGIdata.parse_POST_data()

    print "\n*** CGI-daten ***"
    for k,v in MyCGIdata.get_data().iteritems():
        print k,":",v

    print "\n*** Environ-Data ***"
    for k,v in MyEnvironData.get_data().iteritems():
        print k,":",v

    print "</pre><hr>"


    print """<form name="form" id="form" method="post" action="inetd_test.py?GET1=jo&GET2=buh&biii">
        <input name="feld1" type="text" size="20" />
        <input name="feld2" type="text" size="20" /></p>
        <input type="submit" name="Submit" value="Senden" />
    </form>"""


    print __file__



