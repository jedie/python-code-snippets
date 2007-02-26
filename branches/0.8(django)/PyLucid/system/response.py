#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
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


from django.http import HttpResponse

import sys, os, re, cgi


from PyLucid.system.module_manager import handleTag, handleFunction

lucidSplitRE = re.compile("<lucid(.*?)")

ignore_tag = ("page_msg", "script_duration")




class PyLucidResponse(HttpResponse):
    def __init__(self, request, *args, **kwargs):
        super(PyLucidResponse, self).__init__(*args, **kwargs)
        self.request = request
        self.request.tag_info = {}
        
    def isatty(self):
        return False

    def write(self, txt):
        assert isinstance(txt, basestring)

        if not "<lucid" in txt:
            self._container.append(txt)
            return

        txt = lucidSplitRE.split(txt)
        for part in txt:
            if part.startswith("Tag:"):
                # Bsp part => Tag:page_body/><p>jau</p>

                tag, post = part.split(">",1)
                # tag  => Tag:page_body/
                # post => <p>jau</p>

                tag = tag[4:].rstrip("/")

                # Tag über Module-Manager ausführen
                self.handleTag(tag)

                # Teil hinter dem Tag schreiben
                self._container.append(post)
            elif part.startswith("Function:"):
                # Bsp part:
                # Function:IncludeRemote>http://www.google.de</lucidFunction><p>jau</p>

                try:
                    function, post = part.split("</lucidFunction>",1)
                    # function  => Function:IncludeRemote>http://www.google.de
                    # post      => <p>jau</p>
                except ValueError:
                    # Der End-Tag wurde vergessen -> work-a-round
                    function, post = part.split(">",1)
                    function = function.split(":")[1]
                    function_info = None
                    self.page_msg(
                        "End tag not found for lucidFunction '%s'" % function
                    )
                else:
                    function, function_info = function.split(">")
                    # function      => Function:IncludeRemote
                    # function_info => http://www.google.de

                    function = function.split(":")[1]
                    # function => IncludeRemote

                self.handleFunction(function, function_info)

                # Teil hinter dem Tag schreiben
                self._container.append(post)
            else:
                self._container.append(part)

    def handleTag(self, tag):
        if tag in ignore_tag:
            # save tag position for a later replace, see self.replace_tag()
            self.request.tag_info[tag] = len(self._container)
            self._container.append("<lucidTag:%s/>" % tag)
            return

        return handleTag(tag, self.request, self)
        print tag
        return

        #~ elif tag in self.staticTags:
            #~ self.response.append(self.staticTags[tag])
        #~ else:
            #~ self.module_manager.run_tag(tag)

    def handleFunction(self, function, function_info):
        print ">>>", function, function_info
        return handleFunction(function, function_info)

    def replace_tag(self, tag, txt):
        """
        Replace a saved Tag
        """
        position = self.request.tag_info[tag]
        self._container[position] = txt


'''
OBSOLETE?!?!

    def get(self):
        "zurückliefern der bisher geschriebene Daten"
        content = self.response
        # FIXME: unicode-Fehler sollten irgendwie angezeigt werden!
        result = ""
        for line in content:
            if type(line)!=unicode:
                line = unicode(line, errors="replace")
            result += line

        self.response = []
        return result

    def startFileResponse(self, filename, contentLen=None, \
                    content_type='application/octet-stream; charset=utf-8'):
        """
        Gibt einen Header aus, um einen octet-stream zu "erzeugen"

        Bsp:
        self.response.startFileResponse(filename, buffer_len)
        self.response.write(content)
        return self.response
        """
        if sys.platform == "win32":
            # force Windows input/output to binary
            try:
                import msvcrt
                msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
                msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
            except:
                pass

        self.response = [] # Evtl. schon gemachte "Ausgaben" verwerfen
        #~ print "reset:", self.response

        self.headers['Content-Disposition'] = \
            'attachment; filename="%s"' % filename
        if contentLen:
            self.headers['Content-Length'] = '%s' % contentLen
        self.headers['Content-Transfer-Encoding'] = '8bit' #'binary'
        self.headers['Content-Type'] = content_type

    def startFreshResponse(self, content_type='text/html; charset=utf-8'):
        """
        Eine neue leere Seite ausgeben

        Bsp:
        self.response.startFreshResponse()
        self.response.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
            ' "xhtml1-strict.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n'
            '<head><title>BSP</title></head>\n'
            '<body><h1>Text</h1></body></html>\n'
        )
        return self.response
        """
        self.response = [] # Evtl. schon gemachte "Ausgaben" verwerfen
        self.headers['Content-Type'] = content_type

'''
