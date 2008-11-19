# -*- coding: utf-8 -*-

import os, sys, string, subprocess
from pprint import pprint


def human_filesize(bytes):
    """
    >>> human_filesize(1*1024)
    '1.0KB'
    >>> human_filesize(1*1024*1024)
    '1.0MB'
    >>> human_filesize(1.5*1024*1024)
    '1.5MB'
    """
    bytes = float(bytes)
    for unit in ['bytes','KB','MB','GB','TB']:
        if bytes < 1000:
            return "%s%s" % (round(bytes,1), unit)
        bytes /= 1024.0




ALLOW_CHARS = string.ascii_letters + string.digits + "+-,."

def make_slug(txt, join_string=" ", allow_chars=ALLOW_CHARS):
    """
    delete all non-ALLOW_CHARS characters
    
    >>> make_slug("a test")
    'a test'
    >>> make_slug("")
    ''
    >>> make_slug("A other test 1*2/3\\4/*/*/5")
    'A other test 1 2 3 5'
    """
    parts = [""]
    for char in txt:
        if char not in allow_chars:
            if parts[-1] != "":
                # No double "-" e.g.: "foo - bar" -> "foo-bar" not "foo---bar"   
                parts.append("")
        else:
            parts[-1] += char

    item_name = join_string.join(parts)
    item_name = item_name.strip(join_string)
    
    return item_name



def makeUnique(item_name, name_list, max_no=1000):
    """
    returns a unique shortcut.
    - delete all non-ALLOW_CHARS characters.
    - if the shotcut already exists in name_list -> add a sequential number
    
    >>> makeUnique("two", ["one", "two", "three"])
    'two1'
    >>> makeUnique("two", ["one", "three"])
    'two'
    >>> makeUnique("two", ["one", "two", "two1", "three"])
    'two2'
    >>> makeUnique("", [])
    ''
    """
    name_list2 = [i.lower() for i in name_list]

    # make double shortcut unique (add a new free sequential number)
    if item_name.lower() in name_list2:
        for i in xrange(1, max_no):
            testname = "%s%i" % (item_name, i)
            if testname.lower() not in name_list2:
                item_name = testname
                break

    return item_name




def subprocess2(cmd, debug=False):
    """
    start a subprocess and display all output
    """
    print "_"*80
    print "subprocess2():"
    pprint(cmd)
    print " -"*40
    if debug:
        print "(Debug only, nothing would be started.)"
        return
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        shell=True,
    )
    output = ""
    char_count = 0
    while True:
        char = process.stdout.read(1)
        if char=="":
            break

        if char in ("\r", "\x08"):
            continue
        
        if char == "\n":
            char_count = 0
        else:
            char_count += 1

        output += char
        sys.stdout.write(char)
        if char_count>79:
            sys.stdout.write("\n")
            char_count = 0            
        sys.stdout.flush()

    return process, output





if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    print "DocTest end."