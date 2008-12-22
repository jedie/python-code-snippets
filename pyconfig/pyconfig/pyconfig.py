# -*- coding: utf-8 -*-

"""
    PyConfig
    ~~~~~~~~

    Alternative for ConfigParser/shelve/pickle. Stores a dict as python source
    code into a file.

    How it works:
        * Stores a dict data with pformat
        * Load and Evaluate the dict string with data_eval.py

    data_eval.py doesn't use exec/eval.

    example
    ~~~~~~~

    py = PyConfig(filename="FooBar.txt)
    py["foo"] = "bar"
    py[1] = "FooBar"
    py.save()

    py = PyConfig(filename="FooBar.txt)
    print py # would look like: {"foo": "bar, 1: "FooBar"}


    :copyleft: 2008 by Jens Diemer, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
from pprint import pformat


from data_eval import data_eval


class PyConfig(dict):

    def __init__(self, filename, verbose=1, defaults={}):
        self.filename = filename
        self.verbose = verbose

        self.update(defaults)

        if os.path.isfile(self.filename):
            self._read()
        else:
            if self.verbose:
                print "PyConfig info: file '%s' doesn't exist, yet." % (
                    self.filename
                )

    def _read(self):
        if self.verbose:
            print "Reading %r ..." % self.filename

        f = file(self.filename, "r")
        raw_data = f.read()
        f.close()

        self.string_update(raw_data)

    def save(self):
        if self.verbose:
            print "Save into %r ..." % self.filename,

        f = file(self.filename, "w")
        f.write(self.pformatted())
        f.close()
        if self.verbose:
            print "OK, data saved."

    #--------------------------------------------------------------------------

    def string_new(self, dict_string):
        """
        Set new dict data from the given string.
        """
        if self.verbose:
            print "string new: %r" % dict_string
        data = data_eval(dict_string)
        self.clear()
        self.update(data)

    def string_update(self, dict_string):
        """
        Update the existing dict data from the given string.
        """
        if self.verbose:
            print "string update: %r" % dict_string
        data = data_eval(dict_string)
        self.update(data)

    #--------------------------------------------------------------------------

    def pformatted(self):
        return pformat(self)

    def debug(self):
        print "PyConfig debug:"
        print self.pformatted()
        print "-"*80