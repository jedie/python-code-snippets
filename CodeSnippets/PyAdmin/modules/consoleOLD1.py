#!/usr/bin/python

__version__ = "0.0.4"

#~ import cgitb ; cgitb.enable()
import os, sys, locale, subprocess, re
import xml.sax.saxutils, base64, bz2



maxHistoryLines = 1000

html='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=%(charset)s" />
<title>console @ %(uname)s</title>
<script type="text/javascript">
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
<body onLoad="setFocus();">
    %(stdout)s
<form name="form" id="form" method="post" action="%(self)s">
    <input type="hidden" name="stdout" value="%(stdout_raw)s">
    <input type="hidden" name="current_dir" value="%(current_dir)s">
    <p><input name="cmd" type="text" id="cmd" size="150" /></p>
</form>
</body>
</html>'''


def putHTML( HTMLdata ):
    print "Content-Type: text/html"
    if os.environ.has_key('HTTP_ACCEPT_ENCODING'):
        modes = os.environ['HTTP_ACCEPT_ENCODING'].split(',')

        if "gzip" in modes:
            from gzip import GzipFile

            print 'Content-Encoding: gzip\n'
            oldstdout = sys.stdout
            sys.stdout = GzipFile(mode='wb', fileobj=sys.stdout)
            print HTMLdata
            sys.stdout = oldstdout
            return
        elif "deflate" in modes:
            from zlib import compress

            print "Content-Encoding: deflate\n"
            print compress( HTMLdata )
            return
    # Encoding Mode nicht gzip/deflate oder Environ-Variable nicht gesetzt.
    print
    print HTMLdata


def compress( txt ):
    txt = bz2.compress( txt, 9 )
    return base64.urlsafe_b64encode( txt ).replace("\n","")

def decompress( txt ):
    txt = base64.urlsafe_b64decode( txt )
    return bz2.decompress( txt )

def cutLines( txt, maxLines ):
    return '\n'.join( txt.splitlines()[-maxLines:] )

def GetCGIdata():
    "CGI POST und GET Daten zur einfacheren Verarbeitung zusammen in ein Dict packen"
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


def escape( txt ):
    # Evtl. vorhandene Escape Sequenzen rausfiltern
    txt = re.sub(r"\033\[.*?m","",txt)
    # Für Anzeige im Browser escapen
    txt = xml.sax.saxutils.escape( txt )
    return txt


def cmd( command ):
    process = subprocess.Popen( command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    out = process.stdout.read()
    err = process.stderr.read()

    out = escape( out )
    err = escape( err )
    return out, err





CGIdata = GetCGIdata()



if CGIdata.has_key("stdout"):
    # Alte Ausgaben wieder anzeigen
    txt = CGIdata["stdout"]
    compressLen = len( txt )
    # Ausgaben dekomprimieren
    txt = decompress( txt )
    decompressLen = len( txt )
else:
    compressLen = 0
    decompressLen = 0
    txt = ""


## Alte Verzeichnis wieder herstellen
if CGIdata.has_key("current_dir"):
    current_dir = CGIdata["current_dir"]
    if os.path.isdir( current_dir ):
        # Ins alte Verzeichnis wechseln
        os.chdir( current_dir )
    else:
        current_dir = os.getcwd()
else:
    current_dir = os.getcwd()

## Befehl Ausführen
if CGIdata.has_key("cmd"):
    command = CGIdata["cmd"]
    # Eingabe an altem Prompt anhängen
    txt += " <strong>%s</strong>\n" % command
    # Eingegebener Befehl ausführen + "pwd" (Aktuelles Verzeichnis anzeigen lassen) dranhängen
    out, err = cmd( command + ";echo $~$;pwd" )
    result = out.rsplit("$~$",1)
    current_dir = result[1].strip()
    txt += result[0] + err

# Neues, aktuelles Prompt anhängen
txt += "<strong>%s&gt;</strong>" % current_dir

# Ausgaben kürzen und Komprimieren, damit der Client weniger Daten wieder zurück senden muß
# Die Kompression zahlt sich nach zwei, drei Befehlen i.d.R. aus...
stdout_raw = compress( cutLines( txt, maxHistoryLines ) )

txt += "<p><small>compress: %d  decompress: %d</small></p>" % (compressLen, decompressLen)


html = html % {
    "charset"       : locale.getdefaultlocale()[1],
    "uname"         : cmd("uname -a")[0],
    "self"          : os.environ['SCRIPT_NAME'],
    "stdout"        : txt.replace("\n","<br>\n"),
    "stdout_raw"    : stdout_raw,
    "current_dir"   : current_dir
    }

# Seite Ausgeben
putHTML( html )








