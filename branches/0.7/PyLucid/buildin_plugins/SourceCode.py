#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Zeigt auf dem Webserver eine Source-Datei an.
Python-Code wird mit einem Parser gehighlighted.

Anmerkung:
----------
Eigentlich könnte man prima mit CSS's "white-space:pre;" arbeiten und
somit alle zusätzlichen " " -> "&nbsp;" und "\n" -> "<br/>" umwandlung
sparen. Das Klappt aus mit allen Browsern super, nur nicht mit dem IE ;(
"""

__version__="0.2.6"

__history__="""
v0.2.6
    - Anpassung an änderung im SourceCode-Parser
v0.2.5
    - Anpassung an neuen ModuleManager
v0.2.4
    - lucidFunction() erwartet nun auch function_info vom ModulManager
v0.2.3
    - Python Source Code Parser ausgelagert nach sourcecode_parser.py, damit er auch
        mit tinyTextile genutzt werden kann
v0.2.2
    - Falscher <br>-Tag korrigiert
v0.2.1
    - zwei print durch sys.stdout.write() ersetzt, da ansonsten ein \n eingefügt wurde, der
      im Browser eine zusätzliches Leerzeichen produzierte und somit den Source-Code unbrauchbar
      machte :(
v0.2.0
    - Anpassung damit es mit lucidFunction funktioniert.
v0.1.1
    - Bug in Python-Highlighter: Zeilen mit einem "and /" am Ende wurden falsch dagestellt.
v0.1.0
    - erste Version
"""


import cgitb;cgitb.enable()
import sys, os, cgi, sys



from PyLucid.system.BaseModule import PyLucidBaseModule

class SourceCode(PyLucidBaseModule):

    def lucidFunction( self, function_info ):
        filename = function_info # Daten aus dem <lucidFunction>-Tag
        try:
            filepath = os.environ["DOCUMENT_ROOT"]
        except KeyError:
            return "Error: DOCUMENT_ROOT not defined!"

        filepath += filename
        filepath = os.path.normpath( filepath )

        try:
            f = file( filepath, "rU" )
            source = f.read()
            f.close()
        except Exception, e:
            return "Error to Display file '%s' (%s)" % ( filename, e )

        #~ print '<a href="%sdownload&file=%s" class="SourceCodeFilename">%s</a>' % (
            #~ self.action_url, filename, filename
        #~ )

        #~ print '<p class="SourceCodeFilename">%s</p>' % filename

        if os.path.splitext( filename )[1] == ".py":
            from PyLucid_system import sourcecode_parser
            parser = sourcecode_parser.python_source_parser(self.request)
            self.response.write(parser.get_CSS())
            self.response.write(
                '<fieldset class="SourceCode"><legend>%s</legend>\n' % filename
            )
            parser.parse(source.strip())
        else:
            self.response.write(
                '<fieldset class="SourceCode"><legend>%s</legend>\n' % filename
            )
            self.format_code( source )

        self.response.write('</fieldset>\n')

    def format_code( self, source ):
        """
        Source-Code außer Python-Source anzeigen
        """
        for line in source.split("\n"):
            line = cgi.escape( line )
            line = line.replace("\t","    ") # Tabulatoren nach Leerzeilen
            line = line.replace(" ","&nbsp;") # Leerzeilen nach non-breaking-Spaces
            self.response.write("%s<br />\n" % line)

    #~ def download(self, file):
        #~ print "Location: %s\n" % file
        #~ print "Content-type: text/plain\n";
        #~ sys.exit()












