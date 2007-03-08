#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" kombiniert difflib.Differ() mit Pygments

Used request.render.highlight or request.render.get_hightlighted


 example-1:
----------
    from PyLucid.tools.Diff import display_diff
    display_diff(file_content, db_content, self.request)

 example-2:
----------
    from PyLucid.tools.Diff import get_diff
    html_diff_page = get_diff(file_content, db_content, self.request)
    self.response.write(html_diff_page)


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""


import difflib


def display_diff(content1, content2, request):
    """
    write the Diff hightlighted with Pygments directly into the response Object
    """
    diff = make_diff(content1, content2)
    diff = "\n".join(diff)

    # Mit Pygments anzeigen
    request.render.highlight("diff", diff)

def display_html_diff(content1, content2, response):
    """
    HtmlDiff without pygments. Writes directly into the response object.
    """
    diff = make_diff(content1, content2, mode="HtmlDiff")
    response.write(diff)
    
def display_plaintext_diff(content1, content2, response):
    """
    Display a diff without pygments.
    """
    diff = make_diff(content1, content2)
    
    def is_diff_line(line):
        for char in ("-","+","?"):
            if line.startswith(char):
                return True
        return False
    
    response.write("line | text\n-------------------------------------------\n")
    old_line = ""
    in_block = False
    old_lineno = lineno = 0
    for line in diff:
        if line.startswith(" ") or line.startswith("+"):
            lineno += 1
            
        if old_lineno == lineno:
            display_line = "%4s | %s\n" % ("", line.rstrip())
        else:
            display_line = "%4s | %s\n" % (lineno, line.rstrip())
            
        if is_diff_line(line):
            if not in_block:
                response.write("...\n")
                # Display previous line
                response.write(old_line)
                in_block = True
                
            response.write(display_line)
            
        else:
            if in_block:
                # Display the next line aber a diff-block
                response.write(display_line)
            in_block = False
        
        old_line = display_line
        old_lineno = lineno
    response.write("...\n")

def get_diff(content1, content2):
    """
    returns the HTML-Diff hightlighted with Pygments
    """
    diff = make_diff(content1, content2)
    diff = "\n".join(diff)

    # Mit Pygments hightlighten
    diff = request.render.get_hightlighted("diff", diff)

    return diff

def make_diff(content1, content2, mode="Differ"):
    """
    returns the diff as a String, made with difflib.Differ.
    """
    def prepare(content):
        if isinstance(content, (list, tuple)):
            return content

        return content.splitlines()

    content1 = prepare(content1)
    content2 = prepare(content2)

    if mode=="Differ":
        diff = difflib.Differ().compare(content1, content2)
    elif mode=="HtmlDiff":
        diff = difflib.HtmlDiff(tabsize=4).make_table(content1, content2)

    return diff