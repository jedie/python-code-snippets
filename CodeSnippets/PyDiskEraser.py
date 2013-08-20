#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.1.0"

### History
# v0.1.0
#   Neue Statistikausgabe
# v0.0.7
#   Einige Verbesserungen zur Linux-Ausführbarkeit umgesetzt
# v0.0.6
#   getFreeSpace() auch für posix kompatibel gemacht
#   Bessere Handhabung beim Programm abbruch (EraserFile wird auch dann gelöscht)
# v0.0.5
#   getFreeSpace() dir-Ausgabe mit Parameter /ah (Versteckte Einträge anzeigen)
#   einige statistische Ausgaben hinzugefügt

print """
  %s v%s (GNU General Public License) - by www.jensdiemer.de
""" % (__file__, __version__)

import os
import sys
import time
import optparse
import string

if sys.platform.startswith("win32"):
    IS_WIN = True
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    IS_WIN = False
    # On most other platforms the best timer is default_timer()
    default_timer = default_timer

###
### OptionParser "konfigurieren"
###

# Opt-Parser Instanz erzeugen
OptParser = optparse.OptionParser(usage = "%prog [options] Drive/mountpoint")

# Parameter hinzufügen
OptParser.add_option("-r",
    dest    = "WritesRandomTrash",
    action  = "store_true",
    help    = "writes random bytes (slow) contra NULL-Bytes")
OptParser.add_option("-b",
    dest    = "BlockSize",
    type    = "int",
    default = 1024 * 1024 * 10,
    help    = "block size (writes n-Bytes at once")

# Parameter Parsen
options, args = OptParser.parse_args()

if len(args) != 1:
    # Kein Argument (Drive) angegeben -> Hilfe ausgeben
    print "No drive/mountpoint specified!\n"
    OptParser.print_help()
    sys.exit()


###
### Parameter Auswerten
###

# Drive welches "gelöscht" werden soll
Drive               = args[0]
# Datei in die der Datenmüll geschrieben wird, festlegen
EraserFile          = os.path.join( Drive, "DiskEraser.dat" )
# Sollen Zufällige Zeichen (=True) oder NULL-Bytes (=False) geschrieben werden?
WritesRandomTrash   = options.WritesRandomTrash
# Anzahl der Bytes, die auf einmal geschrieben werden
BlockSize           = options.BlockSize

if os.name == "nt":
    if len(Drive)!=2 or Drive[1]!=":":
        # Angabe des Laufwerks ist wohl falsch -> Hilfe ausgeben
        print "Wrong driveletter [%s]" % Drive
        OptParser.print_help()
        sys.exit()
else:
    if not os.path.exists( Drive ):
        print "Wrong Mountpoint [%s]" % Drive
        OptParser.print_help()
        sys.exit()


###
### Ein paar Hilfs-Funktionen
###


def human_time(t):
    if t > 3600:
        divisor = 3600.0
        unit = "h"
    elif t > 60:
        divisor = 60.0
        unit = "min"
    else:
        divisor = 1
        unit = "sec"

    return "%.1f%s" % (round(t / divisor, 2), unit)


def DeleteFile( File ):
    "Löscht evtl. vorhandene Datei"
    if os.path.isfile( File ):
        # Vorhandene Datei löschen
        print "Delete exist File [%s]..." % File,
        os.remove( File )
        print "OK\n"



def getFreeSpace( Drive ):
    "Liefert den freien Speicherplatz in Bytes eines Laufwerks/mountpoints zurück"
    if os.name == "nt":
        # Benutze DIR-Ausgabe um freinen Speicherplatz zu ermitteln
        ## Wenn auf dem Laufwerk keine Dateien existieren bzw. alle vorhanden versteckt
        ## sind, dann funktioniert das parsen der dir-Ausgabe nicht, weil in der Ausgabe
        ## nicht angezeigt wird, wieviel Bytes frei sind.
        s = os.popen( 'dir %s\\ /ah' % Drive )
        txt = s.readlines()
        s.close()
        txt = txt[-1]
        txt = txt.split(",")[1]
        txt = txt.split("Bytes")[0]
        txt = "".join( txt.split(".") )
        return int( txt )
    elif os.name == "posix":
        # Unter Linux ist alles einfacher ;)
        stats = os.statvfs( Drive )
        return stats.f_bavail * stats.f_bsize
    print "Platform not supported ;("
    sys.exit()

def DeactivateNTFScompression( File ):
    "Hebt mit die NTFS-Kompression für die angegebene Datei auf"
    if os.name != "nt": return
    print "\nDeactivate NTFS-compression:"
    s = os.popen( 'compact /u %s' % EraserFile )
    txt = s.read()
    s.close()
    txt = txt.strip()
    print "-"*80
    print txt
    print "-"*80
    print

def WriteBlocks( FileHandle, BlockSize, BytesFree, BlocksToWrite, WritesRandomTrash, TotalStartTime ):
    "Schreibt Blockweise in die Eraser-Datei"
    NullBytesBlock = "\x00" * BlockSize
    bytes_written = old_bytes_written = 0
    time_threshold = start_time = default_timer()
    for i in xrange( BlocksToWrite ):
        bytes_written += BlockSize

        if WritesRandomTrash:
            # Schreibt einen Block zufälliger Zeichen
            FileHandle.write( os.urandom(BlockSize) )
        else:
            # Schreibt einen Block NULL-Bytes
            FileHandle.write( NullBytesBlock )

        current_time = default_timer()
        if current_time > (time_threshold + 0.5):

            elapsed = float(current_time - start_time)      # Vergangene Zeit
            estimated = elapsed / bytes_written * BytesFree # Geschätzte Zeit
            remain = estimated - elapsed

            diff_bytes = bytes_written - old_bytes_written
            diff_time = current_time - time_threshold
            performance = diff_bytes / diff_time / 1024.0 / 1024.0

            percent = round(float(bytes_written) / BytesFree * 100.0, 2)

            infoline = (
                "\r%(written)dMB %(percent).1f%%"
                "  current: %(elapsed)s"
                "  total: %(estimated)s"
                "  remain: %(remain)s"
                "  %(perf).1fMB/sec"
            ) % {
                "written"  : (bytes_written/1024/1024),
                "percent"  : percent,
                "elapsed"  : human_time(elapsed),
                "estimated": human_time(estimated),
                "remain"   : human_time(remain),
                "perf"     : performance,
            }
            sys.stdout.write("\r")
            sys.stdout.write(string.ljust(infoline, 79))

            time_threshold = current_time
            old_bytes_written = bytes_written

def WriteRemainingBytes( FileHandle ):
    "Schreibt die restlichen Bytes in die Eraser-Datei"
    BytesFree       = getFreeSpace( Drive )
    print "\nWrites remaining %s Bytes..." % BytesFree,
    FileHandle.write( "\x00" * BytesFree )
    print "OK, %s Bytes free\n" % getFreeSpace( Drive )

def CleanUp( EraserFile, Drive ):
    print
    DeleteFile( EraserFile )
    BytesFree = getFreeSpace( Drive )
    print "%s MB free [%s]" % (BytesFree / 1024 / 1024, Drive)

# Evtl. vorhandene Eraser-Datei löschen
DeleteFile( EraserFile )

BytesFree       = getFreeSpace( Drive )
BlocksToWrite   = BytesFree / BlockSize

print "Erase drive [%s]" % Drive
print "Blocksize: %s Bytes" % BlockSize,
if WritesRandomTrash:
    print "(Random-Bytes-Trash)"
else:
    print "(NULL-Bytes)"
print "%s MB free [%s]" % (BytesFree / 1024 / 1024, Drive)
print "Writes %s blocks a %s MB\n" % (BlocksToWrite, BlockSize / 1024 / 1024)

raw_input("\t(Press ENTER to start, Strg-C to abort)")

TotalStartTime = time.time()

# Eraser-Datei erzeugen
FileHandle = file( EraserFile , "w" )

# NTFS-Kompression ausschalten
DeactivateNTFScompression( EraserFile )


aborted = False
try:
    # Schreibt die Eraser-Datei in Blöcken voll
    WriteBlocks( FileHandle, BlockSize, BytesFree, BlocksToWrite, WritesRandomTrash, TotalStartTime )

    # Schreibt die Datei randvoll...
    WriteRemainingBytes( FileHandle )
except KeyboardInterrupt:
    print "\naborted!"
    aborted = True


FileHandle.close()

if not aborted:
    raw_input("\t(Press ENTER to delete the EraserFile)")

CleanUp( EraserFile, Drive )

