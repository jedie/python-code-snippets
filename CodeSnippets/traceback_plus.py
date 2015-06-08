#!/usr/bin/env python
# coding: utf-8

"""
    origin code from:
    https://code.google.com/p/scite-files/wiki/Customization_PythonDebug
    http://code.activestate.com/recipes/52215/

    if PLAT_WIN
        command.go.*.py=python -u C:\path\to\traceback_plus.py "$(FilePath)"
    if PLAT_GTK
        command.go.*.py=python -u /path/to/traceback_plus.py "$(FilePath)"
"""

from __future__ import print_function, unicode_literals

import os
import sys
import traceback


def print_exc_plus():
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    sys.stderr.flush()
    sys.stdout.flush()

    tb = sys.exc_info()[2]
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    print("="*79)
    traceback.print_exc()
    print(" -"*40)
    print("Locals by frame, innermost last")
    for frame in stack[1:]:
        print("\n *** Frame %s in %s at line %s" % (
            frame.f_code.co_name,
            frame.f_code.co_filename,
            frame.f_lineno)
        )
        for key, value in frame.f_locals.items():
            if key.startswith("__"):
                continue
            print("\t%20s = " % key, end="")
            #We have to be careful not to cause a new error in our error
            #printer! Calling str() on an unknown object could cause an
            #error we don't want.
            try:
                print(repr(value))
            except:
                print("<ERROR WHILE PRINTING VALUE>")
    print("="*79)


def demo():
    #A simplistic demonstration of the kind of problem this approach can help
    #with. Basically, we have a simple function which manipulates all the
    #strings in a list. The function doesn't do any error checking, so when
    #we pass a list which contains something other than strings, we get an
    #error. Figuring out what bad data caused the error is easier with our
    #new function.

    data = ["1", "2", 3, "4"] #Typo: We 'forget' the quotes on data[2]
    def pad4(seq):
        """
        Pad each string in seq with zeros, to four places. Note there
        is no reason to actually write this function, Python already
        does this sort of thing much better.
        Just an example.
        """
        return_value = []
        for thing in seq:
            return_value.append("0" * (4 - len(thing)) + thing)
        return return_value

    #First, show the information we get from a normal traceback.print_exc().
    try:
        pad4(data)
    except:
        traceback.print_exc()
    print("\n----------------\n")

    #Now with our new function. Note how easy it is to see the bad data that
    #caused the problem. The variable 'thing' has the value 3, so we know
    #that the TypeError we got was because of that. A quick look at the
    #value for 'data' shows us we simply forgot the quotes on that item.
    try:
        pad4(data)
    except:
        print_exc_plus()


def scite_run():
    try:
        script_file = sys.argv[1]
    except IndexError:
        print("ERROR: no filename given!")
        sys.exit(-1)

    script_file = os.path.abspath(os.path.normpath(script_file))
    assert os.path.isfile(script_file), "Skipt %r doesn't exists!" % sys.argv[1]

    filepath, filename = os.path.split(sys.argv[1])
    print("Start %r from %r:" % (filename, filepath))

    os.chdir(filepath)
    current_dir = os.getcwd()
    sys.path.insert(0, current_dir)

    locals_globals = {
        '__builtins__': __builtins__,
        '__name__': '__main__',
        '__file__': filename,
        #~ '__doc__': None,
        #~ '__package__': None
    }
    sys.argv = [script_file]

    try:
        with open(filename, "rb") as f:
            content = f.read()
            compiled = compile(content, filename, 'exec')
            exec(compiled, locals_globals, locals_globals)
    except SystemExit as err:
        sys.exit(err.code)
    except BaseException:
        print_exc_plus()


if __name__ == '__main__':
    # demo()
    scite_run()
