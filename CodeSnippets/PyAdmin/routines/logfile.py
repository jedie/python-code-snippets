#!/usr/bin/python

__version__ = "0.0.1"


import os, locale

html='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=%(charset)s" />
<title>LogFile</title>
<script type="text/javascript">
function scroll() {
    window.scrollBy(0,99999);
}
</script>
<style type="text/css">
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
<body onLoad="scroll();">
%(txt)s
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




#~ print "Content-Type: text/html\n\n"
#~ for i in os.environ: print i,os.environ[i],"<br>"

logFile = "logs/LogFile.txt"

logFile = os.path.join( os.environ["DOCUMENT_ROOT"], logFile )

FileHandle = file( logFile, "r" )
txt = FileHandle.read()
FileHandle.close()

txt = txt.replace("\n","<br>\n")

txt = html % {
    "charset"       : locale.getdefaultlocale()[1],
    "txt"           : txt
    }

putHTML( txt )