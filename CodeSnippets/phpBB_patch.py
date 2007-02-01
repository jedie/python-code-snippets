#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
renaming the register link in phpBB

Info:
    Generell ist es bei phpBB so:
        -Registrier-Formular: profile.php?mode=register&agreed=true
        -Das Formular wird per POST an profile.php gesendet.


    Ein einfaches suchen nach "profile.php" geht nicht! Siehe Beispiele, in
    welcher Form "profile.php" vorkommt:

    Positiv Beispiel:
        ...append_sid("profile.$phpEx?mode=viewprofile...
                       ^^^^^^^
        ..."login.$phpEx?redirect=profile.$phpEx&mode=email&"...
                                  ^^^^^^^
        ...$script_name . '/profile.'.$phpEx : 'profile.'.$phpEx;...
                            ^^^^^^^

    Negativ Beispiel:
        ...'includes/usercp_viewprofile.'.$phpEx...
                                ^^^^^^^
        ...'Couldn\'t update the user\'s profile.';...
                                         ^^^^^^^
        ...this is done via your profile. Once created you...
                                 ^^^^^^^


$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

license: GNU General Public License v2 or above
"""


import sys, os, re, errno
from difflib import Differ


PHPBB_PATH = ".\phpBB2"
NEW_PROFILE_NAME = "user_info" # Ohne Endung angeben!

#~ SIMULATION = False
SIMULATION = True


RE_SOURCE = re.compile(r"([\"=/'])profile\.")
DESTINATION = r"\1" + NEW_PROFILE_NAME + "."

class Logger(object):
    """
    Ausgaben ausgeben und in Log-Datei schreiben.
    """
    def __init__(self, log_filename, stdout):
        self.stdout = stdout
        self.stdout.write("Log in: %s" % log_filename)
        self.log = file(log_filename, "a+")

    def write(self, line):
        self.stdout.write(line)
        self.log.write(line)

    def close(self):
        self.log.write("="*79)
        self.log.close()

def display_diff(content1, content2):
    diff = Differ().compare(content1.splitlines(), content2.splitlines())
    for line in diff:
        if line.startswith(" "):
            continue
        print line

def test(content):
    """
    Anzeigen, wo profile.php vorkommt, aber nur die Stellen, wenn direkt vor
    dem Dateinamen kein " steht.
    """
    cutout = 30
    current_pos = 0
    while 1:
        try:
            pos = content.index("profile.", current_pos )
        except ValueError:
            return
        current_pos = pos + 1

        if content[pos-1] != '"':
            print repr(content[pos-cutout:pos+cutout])


def patch_file(fn):
    f = file(fn)
    old_content = f.read()
    f.close()

    #~ test(old_content)
    #~ return

    new_content = RE_SOURCE.sub(DESTINATION, old_content)
    if new_content == old_content:
        return

    print "\n>>>", fn
    print "-"*79

    #~ new_content = old_content.replace(SOURCE_STRING, DESTINATION_STRING)
    display_diff(old_content, new_content)

    new_filename = os.path.splitext(fn)[0] + ".bak"

    if SIMULATION:
        return

    print "rename file to:", new_filename
    try:
        os.rename(fn, new_filename)
    except OSError, e:
        if e.errno == errno.EEXIST:
            print "Backup file allready exist, ok"

    print "write new content to:", fn
    try:
        # Neue Datei schreiben
        f = file(fn, "w")
        f.write(new_content)
        f.close()
    except IOError, e:
        print "Error:", e

        # Wiederherstellen
        try:
            os.remove(fn)
        except:
            pass

        try:
            os.rename(new_filename, fn)
        except:
            pass

        sys.exit()


def path_path(path):
    for dir,_,files in os.walk(path):
        for fn in files:
            if not fn.lower().endswith(".php"):
                continue
            fn = os.path.join(dir, fn)
            patch_file(fn)

def rename_file(path):
    old_fn = os.path.join(path, "profile.php")
    new_fn = os.path.join(path, "%s.php" % NEW_PROFILE_NAME)
    print "Rename %s to: %s" % (old_fn, new_fn)
    if SIMULATION:
        return
    try:
        os.rename(old_fn, new_fn)
    except IOError, e:
        print "Error:", e
        sys.exit()



if __name__ == '__main__':
    if not SIMULATION:
        old_stdout = sys.stdout
        log_filename = os.path.join(PHPBB_PATH, "_patch.log")
        sys.stdout = Logger(log_filename, old_stdout)
    else:
        print "\n>>> Simulation only! <<<\n"

    try:
        rename_file(PHPBB_PATH)
        path_path(PHPBB_PATH)
    finally:
        if not SIMULATION:
            sys.stdout.close()
            sys.stdout = old_stdout
