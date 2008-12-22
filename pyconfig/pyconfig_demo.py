# -*- coding: utf-8 -*-

"""
    PyConfig Demo
    ~~~~~~~~~~~~~
        
    :copyleft: 2008 by Jens Diemer, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pyconfig import PyConfig

py = PyConfig(filename="FooBar.txt", defaults={"one": "two"})
py["foo"] = "bar"
py[1] = "FooBar"
py.save()

print py
print "-"*79

# reload

py = PyConfig(filename="FooBar.txt")
print py
print "-"*79

for i in xrange(10):
    py[i] = "a long road..."

py.save()

f = file("FooBar.txt", "r")
print f.read()
f.close()

# Remove all items from the dictionary using the normal dict clear method.
py.clear()
py.save()

py = PyConfig(filename="FooBar.txt")
print py
print "-"*79

# Remove the config file.
import os
os.remove("FooBar.txt")