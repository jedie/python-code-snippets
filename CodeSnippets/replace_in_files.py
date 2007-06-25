#!/usr/bin/python -O
# -*- coding: UTF-8 -*-

"""
-replace string in files (rekusive)
-display the difference.
"""

__author__  = "Jens Diemer"
__license__ = """GNU General Public License v2 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__     = "http://www.jensdiemer.de"
__version__ = "0.1"



import os, time, fnmatch, difflib


class search:
    def __init__(self, search_path, search_string, replace_string,
                                        search_only=True, file_filter=("*.*",)):
        self.search_path       = search_path
        self.search_string     = search_string
        self.replace_string    = replace_string
        self.search_only       = search_only
        self.file_filter       = file_filter

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

    def walk(self):
        file_count = 0
        for root, dirlist, filelist in os.walk(self.search_path):
            for filename in filelist:
                for file_filter in self.file_filter:
                    if fnmatch.fnmatch(filename, file_filter):
                        self.search_file(os.path.join(root, filename))
                        file_count += 1
        return file_count

    def search_file(self, filepath):
        f = file(filepath, "r")
        old_content = f.read()
        f.close()
        if self.search_string in old_content:
            print filepath
            new_content = self.replace_content(old_content, filepath)
            self.display_plaintext_diff(old_content, new_content)

    def replace_content(self, old_content, filepath):
        new_content = old_content.replace(
            self.search_string, self.replace_string
        )
        if self.search_only != False:
            return new_content

        print "Write new content into %s..." % filepath,
        try:
            f = file(filepath, "w")
            f.write(new_content)
            f.close()
        except IOError, msg:
            print "Error:", msg
        else:
            print "OK"
        print
        return new_content

    def display_plaintext_diff(self, content1, content2):
        """
        Display a diff.
        """
        content1 = content1.splitlines()
        content2 = content2.splitlines()

        diff = difflib.Differ().compare(content1, content2)

        def is_diff_line(line):
            for char in ("-", "+", "?"):
                if line.startswith(char):
                    return True
            return False

        print "line | text\n-------------------------------------------"
        old_line = ""
        in_block = False
        old_lineno = lineno = 0
        for line in diff:
            if line.startswith(" ") or line.startswith("+"):
                lineno += 1

            if old_lineno == lineno:
                display_line = "%4s | %s" % ("", line.rstrip())
            else:
                display_line = "%4s | %s" % (lineno, line.rstrip())

            if is_diff_line(line):
                if not in_block:
                    print "..."
                    # Display previous line
                    print old_line
                    in_block = True

                print display_line

            else:
                if in_block:
                    # Display the next line aber a diff-block
                    print display_line
                in_block = False

            old_line = display_line
            old_lineno = lineno
        print "..."


if __name__ == "__main__":
    search(
        search_path     = r"./example/path",
        search_string   = 'the old string',
        replace_string  = 'the new string',
        search_only     = True, # Display only the difference
#        search_only     = False, # write the new content
        file_filter     = ("*.py",), # fnmatch-Filter
    )