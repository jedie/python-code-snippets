#!/usr/bin/python
# coding: ISO-8859-1

from __future__ import print_function

"""
umbenennen einer Render Image Sequenz

kopiert alle Dateien einer Image Sequenz von SOURCE_PATH nach DEST_PATH und
nummeriert dabei die Dateien neu durch.

Anwendungsfall - negative Zeitleiste
------------------------------------
In 3dsmax ist es z.B. möglich die Zeitleiste in den negativen Bereich zu
erweitern. In diesem Falle haben die einzelnen Dateien allerdings ungünstige
Namen.
z.B.:
    Frame-003.png
    Frame-002.png
    Frame-001.png
    Frame-003.png
    Frame0000.png
    Frame0001.png
    Frame0002.png
Zum einen kann diese Sequenz nicht in einem eingelesen werden (z.B. mit
VirtualDub) und zum anderen würde der negative Bereich umgekehrt eingelesen
werden.

Das Skript macht nun aus der Sequenz folgendes:
    Frame-003.png -> Frame_0000.png
    Frame-002.png -> Frame_0001.png
    Frame-001.png -> Frame_0002.png
    Frame-003.png -> Frame_0003.png
    Frame0000.png -> Frame_0004.png
    Frame0001.png -> Frame_0005.png
    Frame0002.png -> Frame_0006.png


Anwendungsfall - fehlende Frames
--------------------------------
Wenn innerhalb einer Image Sequenz Frames fehlen (oder aber auch nur jedes x'te
Frame absichtlich rausgerechnet hat) kann man ebenfalls die Sequenz nicht mit
VirtualDub eingelesen werden.
In dem Falle, sollte das Skript auch wieder eine korrekte Nummerierung
vornehmen. ACHTUNG: Das ist nicht getestet!


Created by Jens Diemer

update:
    v1.1 - update to python 3

license:
    GNU General Public License v3 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import os, re, shutil, time

__version__ = "v1.1"

SOURCE_PATH = r"X:\foo\bar\rendered_image_sequence"
DEST_PATH = r"D:\foo\bar\my_project\assets"

fn_regex = re.compile(r"^(.*[^\-0-9])?(\-?[0-9]+)$")

start_time = time.time()

filelist = {}
basename = None
for filename in os.listdir(SOURCE_PATH):
    fn, ext = os.path.splitext(filename)
    #~ print fn, ext

    basename_test, fileno = fn_regex.match(fn).groups()
    #~ print basename, fileno
    if basename == None:
        basename = basename_test
    else:
        # Der Basisname darf sich nicht ändern!
        assert basename == basename_test, "Basename not the same!"

    fileno = int(fileno)

    assert fileno not in filelist, "fileno not unique!"
    filelist[fileno] = filename

print("read %s filenames in %.2fsec." % (
    len(filelist), time.time()-start_time
))


start_time = int(time.time())

destination = os.path.join(DEST_PATH, basename)
print("destination:", destination)
try:
    os.mkdir(destination)
except Exception as e:
    print("mkdir error:", e)

print()
print("copy...")
print()

filecount = len(filelist)
for no, fileno in enumerate(sorted(filelist)):
    print("%5s %5s %s" % (fileno, no, filelist[fileno]), end=' ')
    src = os.path.join(SOURCE_PATH, filelist[fileno])
    new_filename = "%s_%04i%s" % (basename, no, ext)
    print(new_filename)
    dst = os.path.join(destination, new_filename)

    current_time = int(time.time())
    elapsed = float(current_time-start_time)        # Vergangene Zeit
    estimated = elapsed / (no+1) * (filecount+1)    # Geschäzte Zeit
    if estimated>60:
        time_info = "%.2f/%.2fmin %.2fmin" % (
            elapsed/60.0, estimated/60.0, (estimated-elapsed)/60.0
        )
    else:
        time_info = "%i/%isec %isec" % (
            elapsed, estimated, estimated-elapsed
        )

    print("copy %s/%s %s left (%s)..." % (
        no+1, filecount, filecount-(no+1), time_info
    ), end=' ')
    #~ break
    shutil.copy2(src, dst)
    print("OK")
    print()

