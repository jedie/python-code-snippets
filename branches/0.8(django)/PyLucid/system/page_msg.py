#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Speichert Nachrichten die in der Seite angezeigt werden sollen
Wird am Ende des Reuqestes durch ein Replace Middleware in die
Seite eingesetzt.


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

debug = False


import os, cgi, pprint


def put_page_msg(request, page):
    page_msg = request.user.get_and_delete_messages()
    page_msg.reverse()

    page_msg = (
        '\n<fieldset id="page_msg"><legend>page message</legend>\n'
        '%s'
        '\n</fieldset>'
    ) % "\n".join(page_msg)
    page = page.replace("<lucidTag:page_msg/>", page_msg)
    return page


class PageMsgBuffer(object):
    """
    Kleine Klasse um die Seiten-Nachrichten zu verwalten
    page_msg wird in index.py den PyLucid-Objekten hinzugefugt.
    mit PyLucid["page_msg"]("Eine neue Nachrichtenzeile") wird Zeile
    für Zeile Nachrichten eingefügt.
    Die Nachrichten werden ganz zum Schluß in der index.py in die
    generierten Seite eingeblendet. Dazu dient der Tag <lucidTag:page_msg/>

    self.raw - Für Ausgaben ohne <br />

    """
    raw = False
    debug_mode = debug

    def __init__(self, request):
        self.request = request
        self.reset()

    def reset(self):
        old_msg = self.request.user.get_and_delete_messages()
        if old_msg == []:
            return

        self.red("Old messages:")
        for line in old_msg:
            self.red(line)
        self.red("-"*40)

    #_________________________________________________________________________

    def write(self, *msg):
        self.append_color_data("blue", *msg)

    def __call__(self, *msg):
        """ Alte Methode um Daten "auszugeben", Text ist dann schwarz """
        self.append_color_data("blue", *msg)

    def debug(self, *msg):
        self.append_color_data("gray", *msg)

    def black(self, *msg):
        self.append_color_data("black", *msg)

    def green(self, *msg):
        self.append_color_data("green", *msg)

    def red(self, *msg):
        self.append_color_data("red", *msg)

    #_________________________________________________________________________

    def append_color_data(self, color, *msg):
        if self.raw:
            msg = self.encode_and_prepare(
                "%s" % " ".join([str(i) for i in msg])
            )
        else:
            msg = '<span style="color:%s;">%s</span>' % (
                color, self.prepare(*msg)
            )

        self.request.user.message_set.create(message=msg)

    def prepare(self, *msg):
        """ Fügt eine neue Zeile mit einer Nachricht hinzu """
        result = []

        if self.debug_mode:
            try:
                import inspect
                for stack_frame in inspect.stack():
                    # Im stack vorwärts gehen, bis außerhalb dieser Datei
                    filename = stack_frame[1]
                    lineno = stack_frame[2]
                    if filename != __file__:
                        break

                filename = "...%s" % filename[-25:]
                fileinfo = "%-25s line %3s: " % (filename, lineno)
            except Exception, e:
                fileinfo = "(inspect Error: %s)" % e
            result.append(fileinfo)

        for item in msg:
            if isinstance(item, dict) or isinstance(item, list):
                item = pprint.pformat(item)
                item = item.split("\n")
                for line in item:
                    line = self.encode_and_prepare(line)
                    line = cgi.escape(line)
                    line = line.replace(" ","&nbsp;")
                    result.append("%s<br />\n" % line)
            else:
                result.append(self.encode_and_prepare(item))
                result.append(" ")

        result.append("<br />")

        return "".join(result)

    def encode_and_prepare(self, txt):
        # FIXME: Das ist mehr schlecht als recht... Die Behandlung von unicode
        # muß irgendwie anders gehen!
        if isinstance(txt, unicode):
            return txt.encode("UTF-8", "replace")
        try:
            return str(txt)
        except:
            return repr(txt)





