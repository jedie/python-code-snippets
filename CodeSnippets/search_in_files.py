#!/usr/bin/python -O
# -*- coding: UTF-8 -*-

"""
Sucht rekursiv in Dateiinhalten und listet die Fundstellen auf.
"""

__author__  = "Jens Diemer"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__     = "http://www.jensdiemer.de"
__version__ = "0.1"



import os, time


class search:
    def __init__( self, path, search_string ):
        self.search_path    = path
        self.search_string  = search_string

        print "Search '%s' in [%s]..." % (
            self.search_string, self.search_path
        )
        print "_"*80

        time_begin = time.time()
        file_count = self.walk()
        print "_"*80
        print "%s files searched in %0.2fsec." % (
            file_count, (time.time()-time_begin)
        )

    def walk( self ):
        file_count = 0
        for root, dirlist, filelist in os.walk(self.search_path):
            for filename in filelist:
                filename = os.path.join( root, filename )
                self.search_file( filename )
                file_count += 1
        return file_count

    def search_file( self, filepath ):
        f = file( filepath, "r" )
        content = f.read()
        f.close()
        if self.search_string in content:
            print filepath
            string_pos = content.find( self.search_string )
            content = content[string_pos-content_window:string_pos+content_window]
            content = content.replace("\n","")
            print ">>>", content
            print


if __name__ == "__main__":
    search_path     = r"c:\texte"
    search_string   = "history"
    content_window  = 35
    search( search_path, search_string )