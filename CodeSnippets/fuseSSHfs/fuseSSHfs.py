#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer"
__license__ = "GNU General Public License v2 or above - http://www.opensource.org/licenses/gpl-license.php"
__url__     = "http://www.jensdiemer.de"

__version__ = "v0.1"

__info__ = """fuseSSHfs.py (%s) - Menu to easy mount a remote SSH filesystem using sshfs""" % __version__


urlsFilename = "fuseSSHfs_URLs.txt"


urlsFileInfo = """
    You must create/edit the server adress file './%s':
        - one URL in one line.
        - Comments startet with '#'-char
        - URL format: [<username>@]<host>[:<dir>], look at 'man sshfs'
""" % urlsFilename


usage = """%prog [options]

Note:

    sshfs must be installed. To do this use:
        - sudo apt-get install sshfs
    You must be in the 'fuse' user group:
        - sudo adduser <your username> fuse"""

usage += urlsFileInfo




import sys, os, subprocess, optparse

def get_urls():
    """
    Liefert eine Liste aller Adressen aus der Textdatei zurück
    """
    try:
        f = file(urlsFilename, "r")
    except IOError, e:
        print "Can't read URL text file:"
        print e
        print
        print "Note:"
        print urlsFileInfo
        sys.exit()

    lines = f.readlines()

    urls = [i.strip() for i in lines if i[0]!="#"]
    urls = [i for i in urls if i!=""]

    return urls

def menu(urls):
    """
    Menü für die Auswahl der URL erstellen und Eingabe
    vom User entgegen nehmen. Liefert die URL zurück
    """
    while 1:
        for no, line in enumerate(urls):
            print "%-3s - %s" % (no+1, line)

        no = raw_input("Please select (Strg-C to abort: ")
        print
        try:
            no = int(no)
        except ValueError:
            print "You must input a number!"
            continue

        try:
            return urls[no-1]
        except IndexError:
            print "No %s not exists!" % no

def get_url(urls):
    """
    Menu "starten" und Auswahl anzeigen & zurückliefern
    """
    try:
        url = menu(urls)
    except KeyboardInterrupt:
        print "\n(KeyboardInterrupt)"
        sys.exit()

    print "You selected: %s" % url
    return url

def getMountDir(url):
    """
    Baut den absoluten Pfad zum mountDir zusammen
    """
    return os.path.join(
        os.getcwd(),
        url
    )

def make_dir(url):
    """
    Erstellt das Mount-Verz und liefert den absoluten Pfad dahin zurück
    """
    print "Make dir '%s'..." % url,
    try:
        os.mkdir(url)
    except OSError, e:
        print e
    else:
        print "OK"

    mountdir = getMountDir(url)
    return mountdir

def remove_dir(url):
    """
    Löscht das mountpoint
    """
    print "\nRemove dir '%s'..." % url,
    try:
        os.rmdir(url)
    except OSError, e:
        print e
    else:
        print "OK"

def umount(mountdir):
    """
    unmount von einem mountpoint
    """
    print "\npossibly unmount"
    cmd("sudo fusermount -u '%s'" % mountdir)
    print

def umountAll(urls):
    """
    Alle im Menü definierten mountpoints unmounten und mountpoint löschen
    """
    for url in urls:
        mountdir = getMountDir(url)
        umount(mountdir)
        remove_dir(url)

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




def main():
    """
    Hauptprog.
    """
    print "_"*79
    print __info__
    print

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-v", "--version",
        dest="version",
        default=False,
        action="store_true",
        help="print program versions and exit")
    parser.add_option("-d", "--debug",
        dest="debug",
        default=False,
        action="store_true",
        help="Debug/verbose mode")
    parser.add_option("-u", "--umount",
        dest="umount",
        default=False,
        action="store_true",
        help="umount all possibly mounts, with fusermount -u <path>")

    (options, args) = parser.parse_args()

    if options.version:
        print __info__
        sys.exit()

    if options.debug:
        sshfsOptions = " -d -f"
    else:
        sshfsOptions = ""

    urls = get_urls() # Adressen aus Textdatei lesen

    if options.umount:
        umountAll(urls)
        sys.exit()

    url = get_url(urls) # Menu mit eingabe

    cmd("sudo modprobe fuse")
    print

    mountdir = make_dir(url) # Verz. mit Namen der url erstellen

    # Die zu mountende Verbindung evtl. unmounten
    umount(mountdir)

    cmd(
        "sudo sshfs %s:/ '%s'%s" % (url, mountdir, sshfsOptions)
    )


if __name__ == '__main__':
    main()