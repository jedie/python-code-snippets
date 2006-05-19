#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Middelware

Speichert Nachrichten die in der Seite angezeigt werden sollen
Wird am Ende des Reuqestes durch ein Replace Middleware in die
Seite eingesetzt.
"""


class page_msg_Container(object):
    """
    Kleine Klasse um die Seiten-Nachrichten zu verwalten
    page_msg wird in index.py den PyLucid-Objekten hinzugefugt.
    mit PyLucid["page_msg"]("Eine neue Nachrichtenzeile") wird Zeile
    für Zeile Nachrichten eingefügt.
    Die Nachrichten werden ganz zum Schluß in der index.py in die
    generierten Seite eingeblendet. Dazu dient der Tag <lucidTag:page_msg/>
    """
    def __init__(self, debug = False):
        self.debug = debug
        self.data = ""

    def __call__(self, *msg):
        """ Fügt eine neue Zeile mit einer Nachricht hinzu """
        if self.debug:
            try:
                import inspect
                # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
                filename = inspect.stack()[1][1].split("/")[-1][-20:]
                fileinfo = "%-20s line %3s: " % (filename, inspect.stack()[1][2])
                self.data += fileinfo.replace(" ","&nbsp;")
            except Exception, e:
                self.data += "<small>(inspect Error: %s)</small> " % e

        self.data += "%s <br />\n" % " ".join([str(i) for i in msg])

    def write(self, *msg):
        self.__call__(*msg)

    def get(self):
        if self.data != "":
            # Nachricht vorhanden -> wird eingeblendet
            return '<fieldset id="page_msg"><legend>page message</legend>%s</fieldset>' % self.data
        else:
            return ""



class page_msg(object):
    """
    Fügt in's environ das page_msg-Objekt hinzu
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):

        environ['PyLucid.page_msg'] = page_msg_Container(debug=True)

        return self.app(environ, start_response)

