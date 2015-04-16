#!/usr/bin/python
# coding: ISO-8859-1

"""
    Create and compare MD5, SHA1, SHA256 hashes from file(s)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Ich erstelle mir eine Verknüpfung auf dem Desktop.
    Dann kann man eine einzelne Datei, mehrere Dateien oder ein Verzeichnis
    per Drag&Drop auf die Verknüpfung ziehen.

    Ist keine *.md5 Datei vorhanden, wird diese erstellt.

    Ist eine *.md5 Datei vorhanden, wird die eine aktuelle MD5sum von der
    Datei erstellt und mit der aus der md5-Datei verglichen.

    :copyleft: 2005-2015 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

__author__ = "Jens Diemer"
__license__ = "GNU General Public License v3 or above - http://www.opensource.org/licenses/gpl-license.php"
__info__ = "md5sum_calc"
__url__ = "http://www.jensdiemer.de"

__version__ = "0.4.2"

__history__ = """
v0.5.0 - 16.04.2015
    - Fixes for Python 3 (runs also with Python 2 ;) )
v0.4.1 - 18.03.2014
    - Bugfix in posix systems
v0.4 - 02.12.2013
    - NEW: Display and compare SHA256 hash, too.
    - Old .hash files would be updated
v0.3 - 28.11.2011
    - NEW: Display and compare SHA1 hash, too.
    - Old .md5 files would be updated (New files are named *.hash)
v0.2.8 - 14.11.2008
    - more status information
    - status performance calculated for a short term only
v0.2.7
    - Work-a-round if under Windows only a Driveletter given, see:
        http://www.python-forum.de/topic-16615.html (de)
v0.2.6
    - Speichert mtime in einem Hübscheren Format
        (Updated alte .MD5 Dateien automatisch)
v0.2.5
    - Bugfix(Dank an Egmont Fritz):
        -nur "w" statt "wU" filemode beim schreiben der md5 info Datei
        -speichern der mtime mit repr() und umwandeln mit float() beim lesen
    - raw_input() am Ende entfernt, macht ja die pause in der CMD Datei ;)
v0.2.4 - 15.11.2006
    - Bugfix: ZeroDivisionError bei sehr kleinen Dateien und der
        Preformance Berechnung
v0.2.3
    - NEU: Overall performance ;)
v0.2.2 - 15.12.2005
    - Fehler in Verarbeitung mehrere Dateien behoben (Dateien wurden ausgelassen)
v0.2.1
    - Fehler bei Abarbeitung eines Verz., wenn sich darin wieder ein Verz. befindet
    - NEU: andere Dateibenennung der md5-Dateien!
v0.2
    - Die Hintergundfarbe ändert sich unter Win, wenn die MD5 summe Falsch ist von blau nach rot
v0.1
    - erste Version
"""


import sys
import os
import string
try:
    import configparser # Py3
except ImportError:
    import ConfigParser as configparser # Py2
import datetime
import time

# time.clock() on windows and time.time() on linus
from timeit import default_timer

import hashlib
md5_constructor = hashlib.md5
sha1_constructor = hashlib.sha1
sha256_constructor = hashlib.sha256


CONFIG_HASH_SECTION="HashChecker"
BUFSIZE = 64 * 1024
IS_WIN = sys.platform.startswith("win32")


class FileDateTime(object):
    """
    Small helper class for generate the datetime string of a file date and
    compare it.

    >>> file_stat = os.stat(__file__)
    >>> fdt = FileDateTime(file_stat)
    >>> info = fdt.get_offset_info() # u'+02:00 (Mitteleuropäische Sommerzeit)'
    >>> utc_mtime_string = fdt.utc_mtime_string # 'Fri, 05 Sep 2008 16:18:23'
    >>> fdt.compare_string(utc_mtime_string)
    True
    """
    DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S"

    def __init__(self, file_stat):
        self.mtime = file_stat.st_mtime
        self.utc_mtime_string = self._strftime()

    def _strftime(self):
        """
        Generate the datetime string from the current file stat mtime
        """
        utc_datetime = datetime.datetime.utcfromtimestamp(self.mtime)
        return utc_datetime.strftime(self.DATETIME_FORMAT)

    def get_offset_info(self):
        """
        Returns a string with the currente local time offset information
        """
        if time.daylight != 0:
            # Sommerzeit
            seconds = -time.altzone
        else:
            # keine Sommerzeit
            seconds = -time.timezone

        offset = "%+03d:%02d" % (seconds // 3600, (seconds // 60) % 60)

        return "%s (%s)" % (offset, time.tzname[1])

    def compare_string(self, utc_mtime_string):
        """
        compare the datetime string from the MD5 file with the current file
        stat mtime.

        We don't use datetime.strptime() here, because it's exist only since
        Python 2.5
        """
        return self.utc_mtime_string == utc_mtime_string









print("_" * 79)
print("  %s v%s\n" % (__info__, __version__))


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


class BaseClass(object):
    def set_color(self, color):
        """
        ändert die Komplette Hintergrundfarbe
        """
        if IS_WIN:
            if color == "red":
                os.system("color 4f")
            elif color == "blue":
                os.system("color 1f")


HASHES = ("md5", "sha1", "sha256")

class Hasher(dict):
    def __init__(self):
        super(Hasher, self).__init__()
#        dict.__setitem__(self, "md5", md5_constructor())
#        dict.__setitem__(self, "sha1", sha1_constructor())
        self["md5"] = md5_constructor()
        self["sha1"] = sha1_constructor()
        self["sha256"] = sha256_constructor()

    def update(self, data):
        self["md5"].update(data)
        self["sha1"].update(data)
        self["sha256"].update(data)


class HashChecker(BaseClass):
    def __init__(self, argv):
        self.overall_performance = []
        if type(argv) != list:
            print("sys.argv not type list!")
            return
        self.set_color("blue")
        for arg in argv:
            if os.path.isfile(arg):
                self.process_file(arg)
            elif os.path.isdir(arg):
                self.calc_dir(arg)
            else:
                sys.stderr.write("'%s' no file/dir!\n" % arg)

        try:
            overall_performance = (
                sum(self.overall_performance) / len(self.overall_performance)
            )
            print("Overall performance: %.1fMB/sec" % overall_performance)
            print()
        except ZeroDivisionError:
            # Evtl. war die Datei so klein, das es in Windeseile fertig war ;)
            pass

    def calc_dir(self, dirname):
        print(dirname)
        for file_name in os.listdir(dirname):
            file_name_path = os.path.join(dirname, file_name)
            if not os.path.isfile(file_name_path):
                continue
            self.process_file(file_name_path)

    def process_file(self, file_name_path):
        self.update_hash_file = False

        self.file_name_path = file_name_path
        self.file_path, self.file_name_ext = os.path.split(self.file_name_path)
        self.file_name, self.file_ext = os.path.splitext(self.file_name_ext)
        if self.file_ext.lower() in (".hash", ".md5"):
            return

        self.hash_data_filename = self.file_name_path + ".hash"
        self.old_md5_filename = self.file_name_path + ".md5"

        #~ print "file_name_path:", self.file_name_path
        #~ print "file_path.....:", self.file_path
        #~ print "file_name_ext.:", self.file_name_ext
        #~ print "file_name.....:", self.file_name
        #~ print "file_ext......:", self.file_ext
        #~ print "md5_file......:", self.md5_file

        new_hash_file = False
        old_md5_file = False
        if os.path.isfile(self.hash_data_filename):
            # New hash data file found
            new_hash_file = True
            read_func = self.read_hash_file
        elif os.path.isfile(self.old_md5_filename):
            # Old .md5 file found
            old_md5_file = True
            self.update_hash_file = True
            read_func = self.read_md5file

        if new_hash_file or old_md5_file:
            print("Compare hashes for '%s'..." % self.file_name_ext)
            try:
                hash_file_data, size, utc_mtime_string = read_func()
            except Exception as e:
                self.set_color("red")
                sys.stderr.write("ERROR: Can't read md5-file: %s\n" % e)
                import traceback
                print(traceback.format_exc())
            else:
                hashes = self.compare_file(hash_file_data, size, utc_mtime_string)
                print()
                if self.update_hash_file:
                    self.write_hash_file(hashes)
                    if old_md5_file:
                        # old md5 hash is ok -> delete the old MD5 file and create the new one
                        try:
                            os.remove(self.old_md5_filename)
                        except Exception as err:
                            print("Error: Can't delete old file: %s - %s" % (self.old_md5_filename, err))
                return

        print("Create hashes for '%s'..." % self.file_name_ext)

        hashes = self.create_hashes()
        if not hashes:
            # Something went wrong
            return

        for hash_type, hash in list(hashes.items()):
            print("%s: %s" % (hash_type, hash.hexdigest()))

        self.write_hash_file(hashes)

    def compare_file(self, hash_file_data, size, utc_mtime_string):
        file_stat = os.stat(self.file_name_path)

        if utc_mtime_string:
            fdt = FileDateTime(file_stat)
            if fdt.compare_string(utc_mtime_string) != True:
                print("Note: Time of last modification not equal:")
                print("      %r != %r" % (fdt.utc_mtime_string, utc_mtime_string))
        else:
            print("Info: Skip file modification time compare.")

        if file_stat.st_size != size:
            self.set_color("red")
            print("ERROR: Size is not equal (diff: %iBytes)" % (
                file_stat.st_size - size
            ))
            return

        hashes = self.create_hashes()
        if not hashes:
            # Something went wrong
            return

        tests_ok = True
        for hash_type, hash in list(hash_file_data.items()):
            current_hash = hashes[hash_type].hexdigest()

            if hash is None:
                print("Skip %s compare." % hash_type)
                print("%s %s" % (hash_type, current_hash))
                self.update_hash_file = True # insert missing hash value
                continue

            if current_hash == hash:
                print("%s %s is OK." % (hash_type, current_hash))
            else:
                self.set_color("red")
                print("ERROR: %s checksum wrong:" % hash_type)
                print("%s (currrent) is not %s (saved)" % (current_hash, hash))
                tests_ok = False

        if tests_ok:
            return hashes


    def create_hashes(self):
        file_size = os.stat(self.file_name_path).st_size
        time_threshold = start_time = default_timer()
        hashes = Hasher()
        try:
            with open(self.file_name_path, "rb") as f:
                bytesreaded = old_readed = 0
                threshold = file_size / 10
                while 1:
                    data = f.read(BUFSIZE)
                    bytesreaded += BUFSIZE
                    if not data:
                        break

                    current_time = default_timer()
                    if current_time > (time_threshold + 0.5):

                        elapsed = float(current_time - start_time)      # Vergangene Zeit
                        estimated = elapsed / bytesreaded * file_size # Geschätzte Zeit
                        remain = estimated - elapsed

                        diff_bytes = bytesreaded - old_readed
                        diff_time = current_time - time_threshold
                        performance = diff_bytes / diff_time / 1024.0 / 1024.0

                        percent = round(float(bytesreaded) / file_size * 100.0, 2)

                        infoline = (
                            "   "
                            "%(percent).1f%%"
                            " - current: %(elapsed)s"
                            " - total: %(estimated)s"
                            " - remain: %(remain)s"
                            " - %(perf).1fMB/sec"
                            "   "
                        ) % {
                            "percent"  : percent,
                            "elapsed"  : human_time(elapsed),
                            "estimated": human_time(estimated),
                            "remain"   : human_time(remain),
                            "perf"     : performance,
                        }
                        sys.stdout.write("\r")
                        sys.stdout.write(string.center(infoline, 79))

                        time_threshold = current_time
                        old_readed = bytesreaded

                    hashes.update(data)

                end_time = default_timer()
                try:
                    performance = float(file_size) / (end_time - start_time) / 1024 / 1024
                except ZeroDivisionError as err:
                    print("Warning: %s" % err)
                    print(end_time, start_time, (end_time - start_time))

                self.overall_performance.append(performance)

                sys.stdout.write("\r")
                sys.stdout.write(" "*79) # Zeile "löschen"
                sys.stdout.write("\r")

            print("Performance: %.1fMB/sec" % performance)

            return hashes
        except IOError as e:
            sys.stderr.write("%s: IOError, Can't create HashChecker: %s\n" % (self.file_name_ext, e))
        except KeyboardInterrupt:
            try:
                f.close()
            except:
                pass

    def write_hash_file(self, hashes):
        file_stat = os.stat(self.file_name_path)

        with open(self.hash_data_filename, 'w') as configfile:
           config = configparser.ConfigParser()
           config.add_section(CONFIG_HASH_SECTION)

           config.set(CONFIG_HASH_SECTION, "filename", self.file_name_ext)
           for hash_type, hash in list(hashes.items()):
                config.set(CONFIG_HASH_SECTION, hash_type, hash.hexdigest())
           config.set(CONFIG_HASH_SECTION, "size", "%s" % file_stat.st_size)

           fdt = FileDateTime(file_stat)

           utc_mtime_string = fdt.utc_mtime_string # 'Fri, 05 Sep 2008 16:18:23'
           config.set(CONFIG_HASH_SECTION, "utc_mtime_string", utc_mtime_string)

           tzinfo = fdt.get_offset_info() # u'+02:00 (Mitteleuropäische Sommerzeit)'
           config.set(CONFIG_HASH_SECTION, "timezone_info", tzinfo)

           # config.set(CONFIG_HASH_SECTION, "mtime", repr(file_stat.st_mtime))

           config.write(configfile)

        print("Hash file %s written." % self.hash_data_filename)

    def read_hash_file(self):
        config = configparser.ConfigParser()
        config.read(self.hash_data_filename)
        
        hash_file_data = {}
        for hash_type in HASHES:
            try:
                hash_file_data[hash_type] = config.get(CONFIG_HASH_SECTION, hash_type)
            except (configparser.NoOptionError, configparser.NoSectionError):
                sys.stderr.write("WARING: Hash value for '%s' doesn't exists.\n" % hash_type)
                hash_file_data[hash_type] = None

        size = int(config.get(CONFIG_HASH_SECTION, "size"))

        try:
            utc_mtime_string = config.get(CONFIG_HASH_SECTION, "utc_mtime_string")
        except configparser.NoOptionError:
            print("Info: .md5 sum file has the old mtime information.")
            utc_mtime_string = None

        return hash_file_data, size, utc_mtime_string

    def read_md5file(self):
        """
        read old .md5 file
        """
        config = configparser.ConfigParser()
        config.read(self.old_md5_filename)

        hash_file_data = {"md5sum": config.get("md5sum", "md5sum")}
        size = int(config.get("md5sum", "size"))

        try:
            utc_mtime_string = config.get("md5sum", "utc_mtime_string")
        except configparser.NoOptionError:
            print("Info: .md5 sum file has the old mtime information.")
            utc_mtime_string = None

        return hash_file_data, size, utc_mtime_string



if __name__ == '__main__':
    args = sys.argv[1:]

    if IS_WIN:
        # Work-a-round if under Windows only a Driveletter given
        # see: http://www.python-forum.de/topic-16615.html (de)
        args = [arg.strip('"') for arg in args]

    # HashChecker(args)

    print("SelfTest")
    HashChecker([__file__])
    os.remove("%s.hash" % __file__)
    HashChecker([__file__])

    # DocTest
    import doctest
    print("DocTest:", doctest.testmod(verbose=False))
