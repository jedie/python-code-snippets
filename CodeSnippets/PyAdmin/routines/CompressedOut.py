#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

import os, sys


class ZlibFile:
    def __init__( self, fileobj ):
        self.fileobj = fileobj
        from zlib import compress
        self.compress = compress

    def write( self, txt ):
        self.fileobj.write( self.compress(txt) )
        #~ self.fileobj.flush()

    def flush( self ):
        self.fileobj.flush()


class AutoCompressedOut:
    def __init__( self, ForceMode="auto" ):
        print "Content-Type: text/html"
        if ForceMode != "auto":
            self.mode = ForceMode
        else:
            self.mode = self.detect_mode()
        print 'Content-Encoding: %s\n' % self.mode
        self.set_mode()

    def detect_mode( self ):
        "Ermittle den möglichen Modus"
        if os.environ.has_key('HTTP_ACCEPT_ENCODING'):
            modes = os.environ['HTTP_ACCEPT_ENCODING'].split(',')
            if "deflate" in modes:
                return "deflate"
            elif "gzip" in modes:
                return "gzip"
        return "no compression - flat"

    def set_mode( self ):
        if self.mode == "gzip":
            from gzip import GzipFile
            sys.stdout = GzipFile( mode='wb', fileobj=sys.stdout )
        elif self.mode == "deflate":
            sys.stdout = ZlibFile( fileobj=sys.stdout )

    def get_mode( self ):
        return self.mode




if __name__ == "__main__":
    #~ os.environ['HTTP_ACCEPT_ENCODING'] = "deflate"
    os.environ['HTTP_ACCEPT_ENCODING'] = "gzip"
    MyOut = AutoCompressedOut()

    #~ print "Das ist ein toller Test Text!"
    #~ print "Und noch eine Zeile..."

    import time
    for i in xrange(10):
        print i
        time.sleep(0.1)
        sys.stdout.flush()

    #~ print "...und noch was..."
    #~ print "Verwendeter Modus: '%s'" % MyOut.get_mode()




