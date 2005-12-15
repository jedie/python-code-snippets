#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

import os, sys, time

#~ os.environ["HTTP_ACCEPT_ENCODING"] = ""
os.environ["HTTP_ACCEPT_ENCODING"] = "gzip"
#~ os.environ["HTTP_ACCEPT_ENCODING"] = "deflate"

import CompressedOut
MyOut = CompressedOut.AutoCompressedOut()
print "<p>Out-Compression:'%s'</p>" % MyOut.get_mode()

#~ print "Content-Type: text/html\n\n"

print '<link rel="stylesheet" href="/css/test1.css" type="text/css">'

#~ os.chdir("/etc")
os.chdir("/")
for file in os.listdir( "." ):
    if os.path.isfile( file ):
        print file, os.popen( "file '%s'" % file ).read()
        time.sleep(0.5)
        print "<br>"
        sys.stdout.flush()

print "<h1>fertig</h1>"

