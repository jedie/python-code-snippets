#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.5"

#~ import cgitb ; cgitb.enable()
import os, sys, locale, subprocess, re
import xml.sax.saxutils, base64, bz2

import ansi2html, CompressedOut, CGIdata, config


## Konfiguration
cfg = config.Parser()
cfg.set_section("console")
maxHistoryLines         = cfg.get( "maxHistoryLines", "int" )
forceHTMLCompression    = cfg.get( "forceCompression" )
# Breite der Eingabe Zeile
input_size              = cfg.get( "input size", "int" )


MyOut = CompressedOut.AutoCompressedOut( forceHTMLCompression )
print "<!-- Out-Compression:'%s' -->" % MyOut.get_mode()
#~ for i in os.environ: print i,os.environ[i],"<br>"



ansi2html_normalColor=('black', '#DDDDDD')

htmlPre='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=%(charset)s" />
<title>console @ %(uname)s</title>
<script type="text/javascript">
window.scrollBy(0,9999999);
function setFocus() {
    document.form.cmd.focus();
    window.scrollBy(0,30);
}
</script>
<style type="text/css">
#cmd {
   background-color:#FFEEEE;
}
#cmd:focus {
   background-color:#EEFFEE;
}
body {
    background-color: #CCCCCC;
    padding: 20px;
    padding-bottom: 50px;
    margin: 10px;
}
html {
    background-color: #FFFFFF;
    margin: 10px;
}
</style>
</head>
<body onLoad="setFocus();">'''
htmlPost='''<form name="form" id="form" method="post" action="%(self)s">
    <input type="hidden" name="stdout" value="%(stdout_raw)s">
    <input type="hidden" name="current_dir" value="%(current_dir)s">
    <p><input name="cmd" type="text" id="cmd" size="%(input_size)s" /></p>
</form>
</body>
</html>'''








def compress( txt ):
    txt = bz2.compress( txt, 9 )
    return base64.urlsafe_b64encode( txt ).replace("\n","")

def decompress( txt ):
    txt = base64.urlsafe_b64decode( txt )
    return bz2.decompress( txt )

def cutLines( txt, maxLines ):
    "Schneidet aus dem String >txt< >maxLines<-Anzahl Zeilen von unten ab"
    return '\n'.join( txt.splitlines()[-maxLines:] )




CGIdata = CGIdata.GetCGIdata()









class OutConverter:
    def __init__( self ):
        self.data = ""

    def write( self, txt ):
        sys.stdout.write( txt )

    def flush( self ):
        sys.stdout.flush()

    def readOutData( self, readObj ):
        writer = ansi2html.Writer( MyOutConverter, ansi2html_normalColor )
        while 1:
            line = readObj.readline()
            if line == "": break
            self.data += self.escape( line )
            writer.write( line )
        writer.close()

    def escape( self, txt ):
        # Evtl. vorhandene Escape Sequenzen rausfiltern
        txt = re.sub(r"\033\[.*?m","",txt)
        # Für Anzeige im Browser escapen
        txt = xml.sax.saxutils.escape( txt )
        return txt

    def put_data( self, txt ):
        self.data += txt

    def get_data( self ):
        return self.data


MyOutConverter = OutConverter()



def cmd( command, current_dir ):
    #~ If cwd is not None, the current directory will be changed to cwd before the child is executed.
    process = subprocess.Popen(
            command,
            cwd=current_dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    MyOutConverter.readOutData( process.stdout )
    MyOutConverter.readOutData( process.stderr )






# HTML-Pre Ausgeben
print htmlPre % {
    "charset"       : locale.getdefaultlocale()[1],
    "uname"         : os.uname()
}




if CGIdata.has_key("stdout"):
    # Alte Ausgaben wieder anzeigen
    txt = CGIdata["stdout"]
    compressLen = len( txt )
    # Ausgaben dekomprimieren
    txt = decompress( txt )
    decompressLen = len( txt )
    MyOutConverter.put_data( txt )
    print txt.replace("\n","<br>\n")
else:
    compressLen = 0
    decompressLen = 0
    txt = ""


## Alte Verzeichnis wieder herstellen
if CGIdata.has_key("current_dir") and os.path.isdir( CGIdata["current_dir"] ):
    current_dir = CGIdata["current_dir"]
    # Ins alte Verzeichnis wechseln
    os.chdir( current_dir )
else:
    current_dir = os.getcwd()



## Befehl Ausführen
if CGIdata.has_key("cmd"):
    command = CGIdata["cmd"]
    # Prompt mit Befehl anzeigen
    prompt = "<br><strong>%s>%s</strong><br>\n" % (current_dir, command)
    print prompt
    MyOutConverter.put_data( prompt )

    if command.startswith("cd "):
        # Verzeichnis wechsel
        destination_dir = command[3:]
        destination_dir = os.path.join( current_dir, destination_dir )
        destination_dir = os.path.normpath( destination_dir )
        if os.path.isdir( destination_dir ):
            # Neuer Zielpfad existiert
            current_dir = destination_dir
        else:
            print "Directory [%s] does not exists<br>" % destination_dir
    else:
        # Befehl ausführen
        cmd( command, current_dir )

# Neues, aktuelles Prompt anzeigen
print "<strong>%s&gt;</strong>" % current_dir

# Ausgaben kürzen und Komprimieren, damit der Client weniger Daten wieder zurück senden muß
# Die Kompression zahlt sich nach zwei, drei Befehlen i.d.R. aus...
stdout_raw = compress( cutLines( MyOutConverter.get_data(), maxHistoryLines ) )

print "<p><small>compress: %d  decompress: %d</small></p>" % (compressLen, decompressLen)



print htmlPost % {
    "self"          : os.environ['SCRIPT_NAME'],
    "stdout_raw"    : stdout_raw,
    "current_dir"   : current_dir,
    "input_size"    : input_size
    }










