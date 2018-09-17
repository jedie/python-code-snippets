#!/usr/bin/python -O
# coding: UTF-8

from __future__ import print_function, unicode_literals

"""
-replace string in files (recursive)
-display the difference.

v0.3
 - update for Python v3
v0.2
 - search_string can be a re.compile() object -> use re.sub for replacing

v0.1
 - initial version


    Useable by a small "client" script, e.g.:

-------------------------------------------------------------------------------
#!/usr/bin/python -O
# coding: UTF-8

from __future__ import print_function, unicode_literals

import sys, re

#sys.path.insert(0,"/path/to/git/repro/") # Please change path

from replace_in_files import SearchAndReplace

SearchAndReplace(
    search_path = "/to/the/files/",

    # e.g.: simple string replace:
    search_string  = b'the old string',
    replace_string = b'the new string',

    # e.g.: Regular expression replacing (used re.sub)
    #search_string  = re.compile('{% url (.*?) %}'),
    #replace_string = "{% url '\g<1>' %}",

    search_only = True, # Display only the difference
    #search_only = False, # write the new content

    file_filter=("*.py",), # fnmatch-Filter
)
-------------------------------------------------------------------------------

:copyleft: 2009-2016 by Jens Diemer
"""

__author__ = "Jens Diemer"
__license__ = """GNU General Public License v3 or above -
 http://www.opensource.org/licenses/gpl-license.php"""
__url__ = "http://www.jensdiemer.de"
__version__ = "0.3"

import io
import os
import re
import time
import fnmatch
import difflib


# FIXME: see http://stackoverflow.com/questions/4730121/cant-get-an-objects-class-name-in-python
RE_TYPE = type(re.compile(""))


class SearchAndReplace(object):
    def __init__(self, search_path, search_string, replace_string,
                 search_only=True, file_filter=("*.*",)):
        self.search_path = search_path
        self.search_string = search_string
        self.replace_string = replace_string
        self.search_only = search_only
        self.file_filter = file_filter

        assert isinstance(self.file_filter, (list, tuple))

        # FIXME: see http://stackoverflow.com/questions/4730121/cant-get-an-objects-class-name-in-python
        self.is_re = isinstance(self.search_string, RE_TYPE)

        print("Search '%s' in [%s]..." % (
            self.search_string, self.search_path
        ))
        print("_" * 80)

        time_begin = time.time()

        file_count = self.walk()

        print("_" * 80)
        print("%s files searched in %0.2fsec." % (
            file_count, (time.time() - time_begin)
        ))

    def walk(self):
        file_count = 0
        for root, dirlist, filelist in os.walk(self.search_path):
            if ".svn" in root:
                continue
            for filename in filelist:
                for file_filter in self.file_filter:
                    if fnmatch.fnmatch(filename, file_filter):
                        try:
                            self.search_file(os.path.join(root, filename))
                        except FileNotFoundError as err:
                            print("Skip: %s" % err)
                            continue
                        file_count += 1
        return file_count

    def search_file(self, filepath):
        try:
            with io.open(filepath, "rb") as f:
                old_content = f.read()
        except UnicodeDecodeError as err:
            print("UnicodeDecodeError in %r: %s" % (filepath, err))
            return

        if self.is_re or self.search_string in old_content:
            new_content = self.replace_content(old_content, filepath)
            if self.is_re and new_content == old_content:
                return

            print(filepath)
            self.display_plaintext_diff(old_content, new_content)

    def replace_content(self, old_content, filepath):
        if self.is_re:
            new_content = self.search_string.sub(self.replace_string, old_content)
            if new_content == old_content:
                return old_content
        else:
            new_content = old_content.replace(
                self.search_string, self.replace_string
            )

        if self.search_only != False:
            return new_content

        print("Write new content into %s..." % filepath, end=' ')
        try:
            with io.open(filepath, "wb") as f:
                f.write(new_content)
        except IOError as msg:
            print("Error:", msg)
        else:
            print("OK")
        print()
        return new_content

    def display_plaintext_diff(self, content1, content2):
        """
        Display a diff.
        """
        content1 = content1.decode("UTF-8", errors="replace")
        content2 = content2.decode("UTF-8", errors="replace")

        content1 = content1.splitlines()
        content2 = content2.splitlines()

        diff = difflib.Differ().compare(content1, content2)

        def is_diff_line(line):
            for char in ("-", "+", "?"):
                if line.startswith(char):
                    return True
            return False

        print("line | text\n-------------------------------------------")
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
                    print("...")
                    # Display previous line
                    print(old_line)
                    in_block = True

                print(display_line)

            else:
                if in_block:
                    # Display the next line aber a diff-block
                    print(display_line)
                in_block = False

            old_line = display_line
            old_lineno = lineno
        print("...")


if __name__ == "__main__":
    SearchAndReplace(
        search_path=".",

        # e.g.: simple string replace:
        search_string=b'the old string',
        replace_string=b'the new string',

        # e.g.: Regular expression replacing (used re.sub)
        #search_string   = re.compile('{% url (.*?) %}'),
        #replace_string  = "{% url '\g<1>' %}",

        search_only=True, # Display only the difference
#        search_only     = False, # write the new content

        file_filter=("*.py",), # fnmatch-Filter
    )
