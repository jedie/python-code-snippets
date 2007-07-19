#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
A small Wrapper aound djangos user messages system:
http://www.djangoproject.com/documentation/authentication/#messages

enhanced features:
  - easy callable to print a messages
  - simple color output: self.page_msg.green()
  - use pprint for dicts and lists
  - special debug mode: Inserts informationen, where from the message has come.

In PyLucid modules/plugins, you can use the old system, but it use the django
messages to store the data:
  self.page_msg("I am a new django user message in the old PyLucid style ;)")
  self.page_msg.red("Alert!")


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

from django.conf import settings

import os, sys, cgi, pprint
import inspect


#class PrintLocator(object):
#    """
#    redirect all writes into the page_msg object.
#    """
#    def __init__(self, page_msg):
#        self.page_msg = page_msg
#        self.oldFileinfo = ""
#
#    def write(self, *txt):
#        """
#        write into the page-messages
#        """
#        #~ sys.__stdout__.write(">>>%s<<<\n" % txt)
#
#        # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
#        for stack_frame in inspect.stack():
#            # Im stack vorwärts gehen, bis außerhalb dieser Datei
#            filename = stack_frame[1]
#            lineno = stack_frame[2]
#            if filename != __file__:
#                break
#
#        filename = "...%s" % filename[-25:]
#        fileinfo = "%-25s line %3s: " % (filename, lineno)
#
#        self.page_msg.data.append(
#            "%s - %s" % (filename, __file__)
#        )
#
#        if fileinfo != self.oldFileinfo:
#            self.oldFileinfo = fileinfo
#            self.page_msg.data.append(
#                "<br />[stdout/stderr from ...%s, line %s:] " % fileinfo
#            )
#
#        txt = " ".join([str(i) for i in txt])
#        txt = cgi.escape(txt)
#        txt = txt.replace("\n", "<br />")
#
#        self.page_msg.data.append(txt)

#_____________________________________________________________________________

class PageMessages(object):
    """
    http://www.djangoproject.com/documentation/authentication/#messages
    TODO: Should be inherit from dict.
    """
    raw = False # Append <br /> ?
    debug_mode = settings.DEBUG

    def __init__(self, context):
        try:
            self.messages = context["messages"]
        except KeyError:
            # No django messages inserted by RequestContext
            # In the _install section we use no RequestContext ;)
            self.messages = []

        self._charset = settings.DEFAULT_CHARSET

    #_________________________________________________________________________

    def write(self, *msg):
        self.append_color_data("blue", *msg)

    def __call__(self, *msg):
        """ Alte Methode um Daten "auszugeben", Text ist dann schwarz """
        self.append_color_data("blue", *msg)

    def DEBUG(self, *msg):
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

        #~ self.request.user.message_set.create(message=msg)
        self.messages.append(msg)

    def _get_fileinfo(self):
        """
        Append the fileinfo: Where from the announcement comes?
        Only, if debug_mode is on.
        """
        if not self.debug_mode:
            return ""

        try:
            self_basename = os.path.basename(__file__)
            if self_basename.endswith(".pyc"):
                # cut: ".pyc" -> ".py"
                self_basename = self_basename[:-1]
#                result.append("1%s1" % self_basename)

            for stack_frame in inspect.stack():
                # go forward in the stack, to outside of this file.
                filename = stack_frame[1]
                lineno = stack_frame[2]
#                    result.append("2%s2" % os.path.basename(filename))
                if os.path.basename(filename) != self_basename:
#                        result.append("\n")
                    break

            filename = "...%s" % filename[-25:]
            fileinfo = "%-25s line %3s: " % (filename, lineno)
        except Exception, e:
            fileinfo = "(inspect Error: %s)" % e

        return fileinfo

    def prepare(self, *msg):
        """
        -if debug_mode is on: insert a info from where the message sended.
        -for dict, list use pprint ;)
        """
        result = [self._get_fileinfo()]

        for item in msg:
            if isinstance(item, dict) or isinstance(item, list):
                item = pprint.pformat(item)
                item = item.split("\n")
                for line in item:
                    line = self.encode_and_prepare(line)
                    result.append("%s\n" % line)
            else:
                item = self.encode_and_prepare(item)
                result.append(item)
                result.append(" ")

        result = "".join(result)
        return cgi.escape(result)

    def encode_and_prepare(self, txt):
        """
        returns the given txt as a string object.
        """
        if isinstance(txt, unicode):
            return txt.encode(self._charset)

        # FIXME: Is that needed???
        try:
            return str(txt)
        except:
            return repr(txt)

    #________________________________________________________________
    # Some methods for the django template engine:

    def __iter__(self):
        """
        used in: {% for message in page_msg %}
        """
        for message in self.messages:
            yield message

    def __len__(self):
        """
        used in: {% if page_msg %}
        """
        return len(self.messages)





