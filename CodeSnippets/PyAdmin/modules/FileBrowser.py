#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.3"



## Revisions-History
# v0.0.3
#   - schnellerer Aufbau im Browser, weil Informationen zu Dateien erst im
#       zweiten Durchlauf eingelesen werden und nachträglich per JavaScript in
#       die Tabelle eingefügt werden.
# v0.0.2
#   - time.sleep() eingebaut, damit der Server Zeit hat andere Daten (CSS-Dateien)
#       auszuliefern. Ist insbesondere bei ThreadingServer wichtig!
#   - per JavaScript ein Fortschritt-Titel eingebaut
# v0.0.1
#   - Erste Version



## ToDo
# Fehler, bei leerem Verzeichnis:
#       ZeroDivisionError: float division
#       133             percent = int( currentcount/itemcount * 100 )




import cgitb ; cgitb.enable()
import os, sys, urllib, subprocess, time


os.environ["HTTP_ACCEPT_ENCODING"] = ""

#~ sys.path.append("../routines")

# Eigene Module
import ansi2html, CGIdata, config, thread_subprocess
import menu


head_script = '''<script type="text/javascript">
function s( percent ) {
    document.title = percent + "%% - FileBrowser [%(current_dir)s]";
}
function l( id, txt, url ) {
    // Link zu einer Datei hinzufügen
    Objekt = document.getElementById( id );

    Link = document.createElement("a");
    Link.href = url;

    Link.appendChild( document.createTextNode( txt ) );

    Objekt.appendChild( Link );
    // Leerzeichen nach dem Link einfügen
    Objekt.appendChild( document.createTextNode( " " ) );
}
function i( id, txt ) {
    // Information zur Datei hinzufügen
    Objekt = document.getElementById( id );
    Objekt.appendChild( document.createTextNode( txt ) );
}
</script>
</head>'''

html_start = '''<noscript><h2>Please switch JavaScript on!!!</h2></noscript>
<h2>%(current_dir)s</h2>
<p><a href="console?current_dir=%(current_dir)s">console</a></p>
<table border="0" cellpadding="0" cellspacing="0">
'''

# für die Fortschrittsanzeige ;)
js_info = '<script>s("%s");</script>'

tr_tag = '''<tr>
    <td>%(item)s</td>
    <td>%(action)s</td>
    <td%(id)s>%(info)s</td>
</tr>'''

dir_tag = '<a href="%(self)s?cwd=%(cwd)s">%(dirname)s</a>'

edit_link = 'editor?edit=edit&edit_file=%(filename)s'
view_link = 'viewer?file=%(filename)s'

html_end = '''</table>'''







def cmd( command ):
    process = subprocess.Popen( command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    result = process.stdout.read()
    result += process.stderr.read()
    return result


class FileBrowser:
    def __init__( self, current_dir, selfURL ):
        # Ins verz. wechseln
        os.chdir( current_dir )
        self.current_dir = current_dir
        self.selfURL = selfURL
        self.file_list = []
        # Auslesen und Tabelle Aufbauen
        self.readdir()
        # Datei-Informationen sammeln und per JS "einfügen"
        self.readfileinfo()

    def readdir( self ):
        "Verzeichnis auslesen"
        dirlist = os.listdir( self.current_dir )
        dirlist.sort()
        itemcount = float( len( dirlist ) )
        currentcount = 0
        filecount = 0
        for i in [".."] + dirlist:
            #~ time.sleep(0.01) # Beim verwenden vom ThreadingServer wichtig!

            if os.path.isfile( i ):
                filecount += 1
                self.file_list.append( i ) # Liste für spätere verarbeitung
                self.handle_file( i, file_id = filecount )
            elif os.path.isdir( i ):
                self.handle_dir( i )
            else:
                self.handle_unknown( i )

            percent = int( currentcount/itemcount * 100 )
            print js_info % percent
            currentcount += 1

            sys.stdout.flush()

    def handle_dir( self, dir ):
        "Verzeichniseintrag ausgeben"
        target_dir = os.path.join( self.current_dir, dir )
        target_dir = os.path.normpath( target_dir )
        dir_link = dir_tag % {
                "self"      : self.selfURL,
                "cwd"       : urllib.quote( target_dir ),
                "dirname"   : dir
                }
        self.print_item( dir_link, info="<small>dir</small>" )

    def handle_file( self, file, file_id ):
        "Dateieintrag ausgeben"
        id = ' id="file_%s"' % file_id
        self.print_item( file, "", "", id )

    def readfileinfo( self ):
        """
        Liest Informationen per >file< ein und trägt es JS ein!
        """
        file_id = 0
        currentcount = 0
        itemcount = float( len( self.file_list ) )
        for file in self.file_list:
            file_id += 1
            id = "file_%s" % file_id

            FileInfo = cmd( "file '%s'" % file ).strip()
            FileInfo = FileInfo.split(": ",1)

            print "<script>"
            currentcount += 1
            percent = int( currentcount/itemcount * 100 )
            print 's("%s");' % percent

            if len(FileInfo) == 2:
                FileInfo = FileInfo[1]
            if "text" in FileInfo:
                filename = os.path.join( self.current_dir, file )

                url = edit_link % { "filename": filename }
                print 'l( "%s", "edit", "%s");' % (id, url)

                url = view_link % { "filename": filename }
                print 'l( "%s", "view", "%s");' % (id, url)


            if '"' in FileInfo:
                FileInfo = FileInfo.replace('"', '\\"' )

            print 'i( "%s", "%s");' % ( id, FileInfo )
            print "</script>"

    def handle_unknown( self, item ):
        "unbekannten Eintrag ausgeben"
        self.print_item( self.current_dir + item, "<strong>unknow dir item</strong>" )

    def print_item( self, item, action="&nbsp;", info="&nbsp;", id="" ):
        "Zeile mit den Informationen raus printen"
        print tr_tag % {
            "item"      : item,
            "action"    : action,
            "id"        : id,
            "info"      : info
            }



def start_module( selfURL ):
    if CGIdata.has_key("cwd") and os.path.isdir( CGIdata["cwd"] ):
        current_dir = CGIdata["cwd"]
    else:
        current_dir = "/"

    menu.cfg.css        = "filebrowser.css"
    menu.cfg.title      = "FileBrowser"
    menu.cfg.headings   = head_script % { "current_dir" : current_dir }
    menu.Menu()

    print html_start % { "current_dir" : current_dir }

    #~ time.sleep(1) # Beim verwenden vom ThreadingServer wichtig!

    # Verz-Tabelle ausgeben
    FileBrowser( current_dir, selfURL )

    # Fussdaten ausgeben
    print html_end
    menu.print_footer()



if __name__ == "__main__":
    selfURL = os.environ['SCRIPT_NAME']

    CGIdata = CGIdata.GetCGIdata()

    start_module( selfURL )


def inetd_start():
    "durch inetd-Server gestartet"
    selfURL = "FileBrowser"

    #~ print "FileBrowser!"
    #~ print "CGIdata:"
    #~ print CGIdata

    start_module( selfURL )

