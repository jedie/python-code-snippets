#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

"""
Create and check MD5sum of file(s)

Ich erstelle mir eine Verknüpfung auf dem Desktop.
Dann kann man eine einzelne Datei, mehrere Dateien oder ein Verzeichnis
per Drag&Drop auf die Verknüpfung ziehen.

Ist keine *.md5 Datei vorhanden, wird diese erstellt.

Ist eine *.md5 Datei vorhanden, wird die eine aktuelle MD5sum von der
Datei erstellt und mit der aus der md5-Datei verglichen.
"""

__author__  = "Jens Diemer"
__license__ = "GNU General Public License http://www.opensource.org/licenses/gpl-license.php"
__info__    = "md5sum_calc"
__url__     = "http://www.jensdiemer.de"

__version__ = "0.2.6"

__history__ = """
v0.2.6
    - Speichert mtime in einem Hübscheren Format
        (Updated alte .MD5 Dateien automatisch)
v0.2.5
    - Bugfix(Dank an Egmont Fritz):
        -nur "w" statt "wU" filemode beim schreiben der md5 info Datei
        -speichern der mtime mit repr() und umwandeln mit float() beim lesen
    - raw_input() am Ende entfernt, macht ja die pause in der CMD Datei ;)
v0.2.4
    - Bugfix: ZeroDivisionError bei sehr kleinen Dateien und der
        Preformance Berechnung
v0.2.3
    - NEU: Overall performance ;)
v0.2.2
    - Fehler in Verarbeitung mehrere Dateien behoben (Dateien wurden ausgelassen)
v0.2.1
    - Fehler bei Abarbeitung eines Verz., wenn sich darin wieder ein Verz. befindet
    - NEU: andere Dateibenennung der md5-Dateien!
v0.2
    - Die Hintergundfarbe ändert sich unter Win, wenn die MD5 summe Falsch ist von blau nach rot
v0.1
    - erste Version
"""

import sys, os, md5, ConfigParser, datetime, time

BUFSIZE = 65536



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
            seconds=-time.altzone
        else:
            # keine Sommerzeit
            seconds=-time.timezone

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









print "_" * 79
print "  %s v%s\n" % (__info__, __version__)


class md5sum:
    def __init__(self, argv):
        self.overall_performance = []
        if type(argv) != list:
            print "sys.argv not type list!"
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
            print "Overall performance: %.1fMB/sec" % overall_performance
            print
        except ZeroDivisionError:
            # Evtl. war die Datei so klein, das es in Windeseile fertig war ;)
            pass

    def calc_dir(self, dirname):
        print dirname
        for file_name in os.listdir(dirname):
            file_name_path = os.path.join(dirname, file_name)
            if not os.path.isfile(file_name_path):
                continue
            self.process_file(file_name_path)

    def process_file(self, file_name_path):
        self.file_name_path = file_name_path
        self.file_path, self.file_name_ext  = os.path.split(self.file_name_path)
        self.file_name, self.file_ext       = os.path.splitext(self.file_name_ext)
        if self.file_ext == ".md5":
            return
        self.md5_file = self.file_name_path + ".md5"
        #~ print "file_name_path:", self.file_name_path
        #~ print "file_path.....:", self.file_path
        #~ print "file_name_ext.:", self.file_name_ext
        #~ print "file_name.....:", self.file_name
        #~ print "file_ext......:", self.file_ext
        #~ print "md5_file......:", self.md5_file

        if os.path.isfile(self.md5_file):
            # .md5-Datei existiert schon
            print "Compare md5sum for '%s'..." % self.file_name_ext
            self.compare_file() # vergleiche md5-Summe mit Datei
            print
            return

        print "Create md5sum for '%s'..." % self.file_name_ext

        md5sum, performance = self.create_md5sum()
        if md5sum == False:
            # Irgendein Fehler ist aufgetreten
            return
        print 'write md5sum %s...' % md5sum,
        try:
            self.write_md5file(md5sum)
        except Exception, e:
            print "Error:", e
        else:
            print "OK (%.1fMB/sec)" % performance
        print

    def set_color(self, color):
        """
        ändert die Komplette Hintergrundfarbe
        """
        if sys.platform == "win32":
            if color=="red":
                os.system("color 4f")
            elif color=="blue":
                os.system("color 1f")

    def compare_file(self):
        file_stat = os.stat(self.file_name_path)
        
        try:
            md5sum, size, utc_mtime_string = self.read_md5file()
        except Exception, e:
            self.set_color("red")
            sys.stderr.write("ERROR: Can't read md5-file: %s\n" % e)
            import traceback
            print traceback.format_exc()
            return

        if utc_mtime_string:
            fdt = FileDateTime(file_stat)
            if fdt.compare_string(utc_mtime_string) != True:
                print "Note: Time of last modification not equal:"
                print "      %r != %r" % (fdt.utc_mtime_string, utc_mtime_string)
        else:
            print "Info: Skip file modification time compare."

        if file_stat.st_size != size:
            self.set_color("red")
            print "ERROR: Size is not equal (diff: %iBytes)" % (
                file_stat.st_size-size
            )
            return

        md5sum_file, performance = self.create_md5sum()
        if md5sum != md5sum_file:
            self.set_color("red")
            print "ERROR: md5 checksum wrong! (%.1fMB/sec)" % performance
        else:
            print "md5 check is tested OK (%.1fMB/sec)" % performance
            if utc_mtime_string == None:
                print "Info: Update old md5 file format."
                self.write_md5file(md5sum)


    def create_md5sum(self):
        file_size = os.stat(self.file_name_path).st_size
        time_threshold = start_time = int(time.time())
        try:
            f = file(self.file_name_path, "rb")
            m = md5.new()
            bytesreaded = 0
            threshold = file_size / 10
            while 1:
                data = f.read(BUFSIZE)
                bytesreaded += BUFSIZE
                if not data:
                    break

                current_time = int(time.time())
                if current_time > time_threshold:

                    elapsed = float(current_time-start_time)      # Vergangene Zeit
                    estimated = elapsed / bytesreaded * file_size # Geschätzte Zeit
                    performance = bytesreaded / elapsed / 1024 / 1024

                    if estimated>60:
                        time_info = "%.1f/%.1fmin" % (elapsed/60, estimated/60)
                    else:
                        time_info = "%.0f/%.1fsec" % (elapsed, estimated)

                    sys.stdout.write("\r")
                    sys.stdout.write(
                        "%3.i%% %s %.1fMB/sec    " % (
                            round(float(bytesreaded)/file_size*100),
                            time_info,
                            performance
                        )
                    )
                    time_threshold = current_time
                m.update(data)
            end_time = time.time()
            performance = file_size / (end_time-start_time) / 1024 / 1024

            self.overall_performance.append(performance)

            sys.stdout.write("\r")
            sys.stdout.write(" "*79) # Zeile "löschen"
            sys.stdout.write("\r")
            f.close()
            return m.hexdigest(), performance
        except IOError, e:
            sys.stderr.write("%s: IOError, Can't create md5sum: %s\n" % (self.file_name_ext, e))
            return False
        except KeyboardInterrupt:
            try:
                f.close()
            except:
                pass
            return False


    def write_md5file(self, md5sum):
        file_stat = os.stat(self.file_name_path)

        f = file(self.md5_file, "w")
        config = ConfigParser.ConfigParser()
        config.add_section("md5sum")

        config.set("md5sum", "filename", self.file_name_ext)
        config.set("md5sum", "md5sum", md5sum)
        config.set("md5sum", "size", file_stat.st_size)

        fdt = FileDateTime(file_stat)
 
        utc_mtime_string = fdt.utc_mtime_string # 'Fri, 05 Sep 2008 16:18:23'
        config.set("md5sum", "utc_mtime_string", utc_mtime_string)
        
        tzinfo = fdt.get_offset_info() # u'+02:00 (Mitteleuropäische Sommerzeit)'
        config.set("md5sum", "timezone_info", tzinfo)

#        config.set("md5sum", "mtime", repr(file_stat.st_mtime))

        config.write(f)
        f.close()

    def read_md5file(self):
        f = file(self.md5_file, "rU")
        config = ConfigParser.ConfigParser()
        config.readfp(f)
        f.close()

        md5sum = config.get("md5sum", "md5sum")
        size = int(config.get("md5sum", "size"))
        
        try:
            utc_mtime_string = config.get("md5sum", "utc_mtime_string")
        except ConfigParser.NoOptionError:
            print "Info: .md5 sum file has the old mtime information."
            utc_mtime_string = None

        return md5sum, size, utc_mtime_string


if __name__ == '__main__':
    md5sum(sys.argv[1:])
    
#    print "SelfTest"
#    md5sum([__file__])

    # DocTest
#    import doctest
#    doctest.testmod(verbose=False)
#    print "DocTest end."
