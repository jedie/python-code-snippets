#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
A Ubuntu Human theme Patcher

Kopiert das original Human-Theme zu einem neuen Human2-Theme und
ändert dies. Dabei werden einfach alle "xthickness" und "ythickness"
auskommentiert.
Das gepatchte Theme ist dann unter usr/share/themes/Human2 zu finden.


Achtung: Muß mit ->sudo<- ausgeführt werden:

    sudo ./UbuntuHumanThemePatch.py


Nach dem Patchen kann das "neue" Theme unter

    System -> Einstellungen -> Theme

ausgewählt werden.
"""

__author__  = "Jens Diemer"
__license__ = "GNU General Public License v2 or above - http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://www.jensdiemer.de"

__version__ = "v0.1"


import subprocess, os

print


def cmd(command):
    """
    Kommando ausführen
    """
    print "> %s" % command
    try:
        process = subprocess.Popen(command, shell=True)
        process.wait() # warten, bis der gestartete Prozess zu Ende ist
    except KeyboardInterrupt:
        print "\n(KeyboardInterrupt)"
        sys.exit()
    print "(returncode: %s)" % process.returncode

class Patcher:
    """
    Patch die Dateien
    """
    def __init__(self):
        self.makePatch(
            src_path = "/usr/share/themes/Human2/gtk-2.0/gtkrc",
            rewriteMethod = self.thicknessPatch
        )
        self.makePatch(
            src_path = "/usr/share/themes/Human2/index.theme",
            rewriteMethod = self.indexPatch
        )

    def thicknessPatch(self, line):
        if "thickness" in line:
            return "# %s" % line
        else:
            return line

    def indexPatch(self, line):
        if "GtkTheme=" in line or "Name=" in line:
            return line.replace("Human", "Human2")

        if "Comment=" in line:
            return "Comment=A Patched Ubuntu default theme\n"

        return line

    def makePatch(self, src_path, rewriteMethod):
        dst_path = "%s.tmp" % src_path
        src = file(src_path, "rU")
        dst = file(dst_path, "w")
        for line in src:
            line = rewriteMethod(line)
            dst.write(line)
        src.close()
        dst.close()

        os.rename(src_path, "%s.old" % src_path)
        os.rename(dst_path, src_path)




print "Delete old Human2 Theme"
cmd("rm /usr/share/themes/Human2 -R")
print

print "Copy Human Theme"
cmd("cp /usr/share/themes/Human /usr/share/themes/Human2 -R")
print

print "Patch Theme"
Patcher()
print "OK"
print
print "Now you can select the 'Human2' Theme!"
print
