#!/usr/bin/python -O
# -*- coding: UTF-8 -*-

"""
Sucht rekursiv in Dateiinhalten und listet die Fundstellen auf.
"""

__author__ = "Jens Diemer"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__ = "http://www.jensdiemer.de"
__version__ = "0.1"



import os, time, fnmatch


class Search:
    def __init__(self, path, search_string, file_filter, max_cutouts=20, content_extract = 35):
        self.search_path = path
        self.search_string = search_string
        self.file_filter = file_filter
        self.max_cutouts = max_cutouts
        self.content_extract = content_extract

        print "Search '%s' in [%s]..." % (
            self.search_string, self.search_path
       )
        print "_" * 80

        time_begin = time.time()
        file_count = self.walk()
        print "_" * 80
        print "%s files searched in %0.2fsec." % (
            file_count, (time.time() - time_begin)
       )

    def walk(self):
        file_count = 0
        for root, dirlist, filelist in os.walk(self.search_path, followlinks=True):
            for filename in filelist:
                for file_filter in self.file_filter:
                    if fnmatch.fnmatch(filename, file_filter):
                        self.search_file(os.path.join(root, filename))
                        file_count += 1
        return file_count

    def search_file(self, filepath):
        f = file(filepath, "r")
        content = f.read()
        f.close()
        if self.search_string in content:
            print filepath
            self.cutout_content(content)

    def cutout_content(self, content):
        current_pos = 0
        search_string_len = len(self.search_string)
        for i in xrange(self.max_cutouts):
            try:
                pos = content.index(self.search_string, current_pos)
            except ValueError:
                break

            content_window = content[ pos - self.content_extract : pos + self.content_extract ]
            print ">>>", content_window.encode("String_Escape")
            current_pos += pos + search_string_len
        print


if __name__ == "__main__":
    search_path = r"c:\texte"
    file_filter = ("*.py",) # fnmatch-Filter
    search_string = "history"
    content_extract = 35 # Gr��e des Ausschnittes der angezeigt wird
    max_cutouts = 20 # Max. Anzahl an Treffer, die Angezeigt werden sollen

    Search(search_path, search_string, file_filter, max_cutouts, content_extract)
