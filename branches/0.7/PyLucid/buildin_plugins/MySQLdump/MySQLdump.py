#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Erzeugt einen Download des MySQL Dumps
http://dev.mysql.com/doc/mysql/de/mysqldump.html
"""

__version__="0.4"

__history__="""
v0.4
    - Anpassung an PyLucid v0.7
v0.3.2
    - Quick hack to display mysql version informations
v0.3.1
    - Bugfix: options kann nun auch leer sein
v0.3
    - Anpassung an neuen ModuleManager, auslagern der Config.
v0.2.2
    - Nutzt die module_manager Einstelung "sys_exit", damit der Dumpdownload
        richtig beendet wird
    - In additional_dump_info ist in sys.version ein \n Zeichen, welches nun
        rausfliegt.
v0.2.1
    - Anpassung an self.db.print_internal_page()
v0.2.0
    - HTML-Ausgaben nun über interne Seite
v0.1.2
    - Umbenennung in MySQLdump, weil's ja nur für MySQL geht...
    - NEU: Nun kann man auch den Pfad zu mysqldump angeben.
        Standard ist "." (aktuelles Verzeichnis) damit wird mysqldump im Pfad
        gesucht. Das klappt nun auch unter Windows
v0.1.1
    - NEU: Man kann nun genau auswählen was von welcher Tabelle man haben will
v0.1.0
    - Anpassung an Module-Manager
    - Umau an einigen Stellen
v0.0.4
    - Es ist nun möglich kein "--compatible=" Parameter zu benutzen
        (wichtig bei MySQL server <v4.1.0)
v0.0.3
    - Module-Manager Angabe "direct_out" hinzugefügt, damit der Download des
      Dumps auch funktioniert.
v0.0.2
    - Großer Umbau: Anderes Menü, anderer Aufruf von mysqldump, Möglichkeiten
        Dump-Parameter anzugeben
v0.0.1
    - Erste Version
"""


import os, sys, cgi, time
import re, StringIO, zipfile

from colubrid import HttpResponse



from PyLucid.system.BaseModule import PyLucidBaseModule


class MySQLdump(PyLucidBaseModule):

    def menu(self):
        """ Menü für Aktionen generieren """
        #~ self.URLs.debug()
        self.request.debug()

        if self.request.form.get("action", False):
            actions = {
                "display_dump": self.display_dump,
                "display_command": self.display_command,
                "install_dump": self.PyLucid_install_dump,
            }
            actionKey = self.request.form["action"]
            try:
                action = actions[actionKey]
            except KeyError, e:
                self.response("Subaction '%s' unknown!")
                return

            try:
                response = action()
            except CreateDumpError:
                return
            else:
                return response

        default_no_data = ["log", "session_data"]
        default_no_data = [
            self.preferences["dbTablePrefix"] + i for i in default_no_data
        ]

        table_data = ""
        for name in self.db.get_tables():
            if name in default_no_data:
                structure = ' checked="checked"'
                complete = ''
            else:
                structure = ''
                complete = ' checked="checked"'

            table_data += '<tr>\n'
            table_data += '\t<td>%s</td>\n' % name
            table_data += '\t<td><input type="radio" name="%s" value="ignore" /></td>\n' % name
            table_data += '\t<td><input type="radio" name="%s" value="structure"%s /></td>\n' % (
                name, structure
            )
            table_data += '\t<td><input type="radio" name="%s" value="complete"%s /></td>\n' % (
                name, complete
            )
            table_data += '</tr>\n'

        self.actions = [
            ("download_dump",   "download dump"),
            ("display_dump",    "display SQL dump"),
            ("install_dump",    "download PyLucid install dump"),
            ("display_help",    "mysqldump help" ),
            ("display_command", "display mysqldump command"),
        ]

        try:
            version_info = self.tools.subprocess2("mysql --version", ".", timeout=1).out_data
        except Exection, e:
            version_info = "ERROR:", e

        buttons = "<p>mysql version: <em>%s</em></p>" % version_info

        for action in self.actions:
            buttons += '<button type="submit" name="action" value="%s">%s</button>&nbsp;&nbsp;\n' % (
                    action[0], action[1]
                )

        context = {
            "version"       : __version__,
            "tables"        : table_data,
            "url"           : self.URLs["current_action"],
            "buttons"       : buttons
        }

        self.templates.write("MySQLdump_Menu", context)

    #_______________________________________________________________________

    def makedump(self):
        command_list = self._get_sql_commands()
        dump = self._run_command_list(command_list, timeout = 120, header=True)

        # Zusatzinfo's in den Dump "einblenden"
        dump = self.additional_dump_info() + dump
        dumpLen = len(dump)

        filename = "%s_%s%s.sql" % (
            time.strftime("%Y%m%d"),
            self.preferences["dbTablePrefix"],
            self.preferences["dbDatabaseName"]
        )

        return dump, dumpLen, filename

    #_______________________________________________________________________


    def FileResponse(self, content, contentLen, filename):
        # force Windows input/output to binary
        if sys.platform == "win32":
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


        # Ein "wirklich" frisches response-Object nehmen:
        response = HttpResponse()

        response.headers['Content-Disposition'] = \
            'attachment; filename="%s"' % filename
        response.headers['Content-Length'] = '%s' % contentLen
        response.headers['Content-Transfer-Encoding'] = '8bit' #'binary'
        response.headers['Content-Type'] = \
            'application/octet-stream; charset=utf-8'

        response.write(content)

        return response

    #_______________________________________________________________________

    def download_dump(self):
        """
        Erstellt den SQL Dump und bietet diesen direk zum Download an
        """
        dump, dumpLen, filename = self.makedump()

        return self.FileResponse(dump, dumpLen, filename)


    def PyLucid_install_dump(self):
        dump, dumpLen, dumpfilename = self.makedump()

        dbTablePrefix = self.preferences["dbTablePrefix"]
        dump = universalize_dump(self.response, dbTablePrefix).process(dump)

        self.response.write("Keys: %s<br />\n" % dump.keys())
        for k,v in dump.iteritems():
            self.response.write(
                "<strong>%s</strong> - %s<br />\n" % (k, cgi.escape(v))
            )

        buffer = StringIO.StringIO()
        z = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

        for filename,data in dump.iteritems():
            #~ if debug:
                #~ self.response.write("\n","-"*80)
                #~ self.response.write(filename)
                #~ self.response.write("- "*40)
                #~ self.response.write(data)
                #~ self.response.write("-"*80)
            z.writestr(filename,data)
        z.close()

        buffer.seek(0,2) # Am Ende der Daten springen
        buffer_len = buffer.tell() # Aktuelle Position
        buffer.seek(0) # An den Anfang springen


        content = buffer.read()
        filename = "%s.zip" % dumpfilename

        return self.FileResponse(content, buffer_len, filename)


    #_______________________________________________________________________

    def display_dump(self):
        """
        Zeigt den SQL dump im Browser an
        """
        start_time = time.time()
        dump, dumpLen, filename = self.makedump()

        dumpLen = self.tools.formatter(dumpLen, format="%0i")
        msg = (
            "<p><small>"
            "(mysqldump duration %.2f sec. - size: %s Bytes)"
            "</small></p>"
        ) % (
            (time.time() - start_time), dumpLen
        )
        self.response.write(msg)

        self.response.write("<pre>%s</pre>" % cgi.escape(dump))

        self.response.write('<a href="JavaScript:history.back();">back</a>')

    #_______________________________________________________________________

    def display_help( self ):
        """
        Zeigt die Hilfe von mysqldump an
        """
        command_list = ["mysqldump --help"]

        self.response.write('<p><a href="JavaScript:history.back();">back</a></p>')

        output = self._run_command_list( command_list, timeout = 2 )
        if output == False:
            # Fehler aufgereten
            return

        self.response.write("<pre>%s</pre>" % output)

        self.response.write('<a href="JavaScript:history.back();">back</a>')

    #_______________________________________________________________________

    def display_command( self ):
        """
        mysqldump Kommandos anzeigen, je nach Formular-Angaben
        """

        mysqldump_path = self.request.form["mysqldump_path"]
        self.response.write("<h3>Display command only:</h3>")
        self.response.write("<pre>")
        for command in self._get_sql_commands():
            self.response.write(
                "%s>%s" % (
                    mysqldump_path, command.replace(self.preferences["dbPassword"],"***")
                )
            )
        self.response.write("</pre>")
        self.response.write('<a href="JavaScript:history.back();">back</a>')


    def _get_sql_commands( self ):
        """
        Erstellt die Kommandoliste anhand der CGI-Daten bzw. des Formulars ;)
        """
        try:
            options = self.request.form["options"]
        except KeyError:
            options = ""
        else:
            options = " %s" % options

        try:
            compatible = self.request.form["compatible"]
        except KeyError:
            compatible = ""
        else:
            compatible = " --compatible=%s" % compatible

        default_command = (
            "mysqldump --default-character-set=%(cs)s%(cp)s%(op)s"
            " -u%(u)s -p%(p)s -h%(h)s %(n)s"
        ) % {
            "cs" : self.request.form["character-set"],
            "cp" : compatible,
            "op" : options,
            "u"  : self.preferences["dbUserName"],
            "p"  : self.preferences["dbPassword"],
            "h"  : self.preferences["dbHost"],
            "n"  : self.preferences["dbDatabaseName"],
        }

        tablenames = self.db.get_tables()
        structure_tables = []
        complete_tables = []
        for table in tablenames:
            dump_typ = self.request.form[table]

            if dump_typ == "ignore":
                # Die Tabelle soll überhaupt nicht gesichert werden
                continue
            elif dump_typ == "structure":
                structure_tables.append( table )
            elif dump_typ == "complete":
                complete_tables.append( table )
            else:
                raise

        result = []
        if structure_tables != []:
            result.append(
                default_command + " --no-data " + " ".join( structure_tables )
            )
        if complete_tables != []:
            result.append(
                default_command + " --tables " + " ".join( complete_tables )
            )

        return result


    def _run_command_list( self, command_list, timeout, header=False ):
        """
        Abarbeiten der >command_list<
        liefert die Ausgaben zurück oder erstellt direk eine Fehlermeldung
        """
        try:
            mysqldump_path = self.request.form["mysqldump_path"]
        except KeyError:
            # Wurde im Formular leer gelassen
            mysqldump_path = "."

        def print_error( out_data, returncode, msg ):
            if header == True:
                # Beim Ausführen von "download dump" wurde noch kein Header ausgegeben
                self.response.write("Content-type: text/html; charset=utf-8\r\n")
            self.response.write("<h3>%s</h3>" % msg)
            self.response.write("<p>Returncode: %s<br />" % returncode)
            self.response.write("output:<pre>%s</pre></p>" % cgi.escape( out_data ))

        result = ""
        for command in command_list:
            start_time = time.time()
            process = self.tools.subprocess2( command, mysqldump_path, timeout )
            result += process.out_data

            if process.killed == True:
                print_error(
                    result, process.returncode,
                    "Error: subprocess timeout (%.2fsec.>%ssec.)" % ( time.time()-start_time, timeout )
                )
                raise CreateDumpError
            if process.returncode != 0 and process.returncode != None:
                print_error( result, process.returncode, "subprocess Error!" )
                raise CreateDumpError

        return result

    #_______________________________________________________________________

    def additional_dump_info( self ):
        txt = "-- ------------------------------------------------------\n"
        txt += "-- Dump created %s with PyLucid's %s v%s\n" % (
            time.strftime("%d.%m.%Y, %H:%M"), os.path.split(__file__)[1], __version__
            )
        txt += "--\n"

        if hasattr(os,"uname"): # Nicht unter Windows verfügbar
            txt += "-- %s\n" % " - ".join( os.uname() )

        txt += "-- Python v%s\n" % sys.version.replace("\n","")

        txt += "--\n"

        command_list = ["mysqldump --version"]
        output = self._run_command_list( command_list, timeout = 1 )
        if output != False:
            # kein Fehler aufgereten
            txt += "-- used:\n"
            txt += "-- %s" % output

        txt += "--\n"
        txt += "-- This file should be encoded in utf8 !\n"
        txt += "-- ------------------------------------------------------\n"

        return txt




class CreateDumpError(Exception):
    """
    Beim erstellen des Dumps ist irgendwas schief gelaufen
    """
    pass






# Einträge die rausfallen
filter_startswith = (
    "INSERT INTO `$$archive`",
    "INSERT INTO `$$log`",
    "INSERT INTO `$$md5users`",
    "INSERT INTO `$$session_data`",
    "INSERT INTO `$$users`",
    "INSERT INTO `$$user_group`",

    "LOCK TABLES",
    "UNLOCK TABLES",
)

# Filter für zusätzliche SQL-Angaben im CREATE TABLE statement
pattern = "[^;, ]* *"
crate_table_filters = (
    "collate %s" % pattern,
    "ENGINE=%s" % pattern,
    "COLLATE=%s" % pattern,
    "character set %s" % pattern,
    "DEFAULT CHARSET=%s" % pattern,
    " TYPE=MyISAM(?<! COMMENT)" # (?<!\))
)

cleaning_filters = (
    "/\*.*?\*/;",
)

class universalize_dump:
    #FIXME: Völlig unnötig, wenn man eh die SQL-dump-Kommandos einzeln ausführen kann!!!
    def __init__(self, response, dbTablePrefix):
        self.response = response
        self.dbTablePrefix = dbTablePrefix

        self.in_create_table = False
        self.after_commend = False
        self.found_dbprefix = False


    def process(self, dumpData):
        """
        DUMP-Daten Konvertieren und in ZIP Datei schreiben
        """
        re_find_name = re.compile( r"`\$\$(.*?)`" )
        category = ""
        outdata = {}

        dumpData = dumpData.split("\n")
        #~ self.response.write("<br />\n".join(dumpData))

        for line in dumpData:
            line = self.preprocess(line)
            if line.startswith("--"):
                category = "info.txt"
            else:
                find_name = re_find_name.findall(line)
                if find_name != []:
                    category = find_name[0]+".sql"

            if not outdata.has_key(category):
                outdata[category] = ""

            if line=="": continue # Leere Zeilen brauchen wir nicht

            outdata[category] += line+"\n"

        return outdata

        if self.found_dbprefix == False:
            self.response.write("ERROR: No table prefix '%s' found!!!" % self.dbTablePrefix)


    def preprocess( self, line ):
        """
        -Filterung des aktuellen self.dbTablePrefix nach %(table_prefix)s
        -Einblendung der Dump-Informationen
        """
        # Prozentzeichen escapen
        prefix_mark = "`%s" % self.dbTablePrefix

        # Tabellen Prefixe ändern
        if prefix_mark in line:
            self.found_dbprefix = True
            line = line.replace( prefix_mark, "`$$" )

        # Zeilen filtern
        for filter in filter_startswith:
            if line.startswith( filter ):
                return ""

        # Spezielle SQL Kommandos rausschmeißen
        #~ if line.startswith( "/*" ) and line.endswith( "*/;\n" ):
            #~ self.response.write(">", line)
            #~ return ""

        if line.startswith( "CREATE TABLE" ):
            self.in_create_table = True

        if self.in_create_table == True:
            #~ self.response.write(line[:-1])
            for filter in crate_table_filters:
                line = re.sub( filter, "", line )
            #~ self.response.write(">",line)

        if line.endswith( ";" ):
            self.in_create_table = False

        for filter in cleaning_filters:
            line = re.sub( filter, "", line )

        return line