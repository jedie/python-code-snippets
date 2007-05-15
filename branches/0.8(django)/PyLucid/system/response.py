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

from PyLucid.system.module_manager import handleTag

lucidSplitRE = re.compile("<lucid(.*?)")

MIDDLEWARE_TAGS = ("page_msg", "script_duration")


class PyLucidResponse(HttpResponse):
    """
    Response object.
    replace all lucid-Tags and use the module_manager to get the result-content
    of these tags.
    """
    def __init__(self, request, *args, **kwargs):
        super(PyLucidResponse, self).__init__(*args, **kwargs)
        self.request = request
        try:
            self.page_msg = request.page_msg
        except AttributeError:
            # Install?`
            self.page_msg = sys.stderr
        self.request.tag_info = {}

    def isatty(self):
        return False

    def write(self, txt):
        """
        Parse the text and replace lucidTag
        """
        self.append_parsed(txt)

    def append_parsed(self, txt):
        """
        replace alle lucidTag in the content and append it to the container
        """
        assert isinstance(txt, basestring)

        if not "<lucid" in txt:
            self._container.append(txt)
            return

        txt = lucidSplitRE.split(txt)
        for part in txt:
            if not part.startswith("Tag:"):
                if part.startswith("Function:"):
                    # Obsolete!
                    self.page_msg("lucidFunction's are obsolete!")
                else:
                    self._container.append(part)
                continue

            # Handle a lucidTag

            # Bsp part => Tag:page_body/><p>jau</p>
            tag, post = part.split(">",1)
            # tag  => Tag:page_body/
            # post => <p>jau</p>

            tag = tag[4:].rstrip("/")

#            if "</lucidTag>" in post:
#                raise NotImplementedError

            # Tag über Module-Manager ausführen
#            try:
            self.handleTag(tag)
#            except Exception, e:
#                msg = "Handle Tag %s Error: %s" % (tag, e)
#                self.page_msg(msg)
#                self._container.append("[%s]" % msg)

            # Teil hinter dem Tag schreiben
            self._container.append(post)


    def handleTag(self, tag):
        if tag in MIDDLEWARE_TAGS:
            # save tag position for a later replace, see self.replace_tag()
            self.request.tag_info[tag] = len(self._container)
            self._container.append("<lucidTag:%s/>" % tag)
            return

        if tag in self.request.static_tags:
            content = self.request.static_tags[tag]
            if tag == "page_body":
                # replace
                self.append_parsed(content)
            else:
                assert isinstance(content, basestring), (
                    "static tag returns not a basestring! returns: '%s'"
                ) % repr(content)
                self._container.append(content)
            return

        local_module_response = handleTag(tag, self.request, self)
        if local_module_response:
            if isinstance(local_module_response, basestring):
                output = local_module_response
            else:
                try:
                    output = local_module_response.get()
                except Exception, e:
                    output = (
                        "[Error get module output: %s"
                        " - type: %s, repr: %s"
                    ) % (
                        e, cgi.escape(str(type(local_module_response))),
                        cgi.escape(repr(local_module_response))
                    )

                    raise ValueError(output)

            self._container.append(output)

    def replace_tag(self, tag, txt):
        """
        Replace a saved Tag
        Used by the middlewares to put "page_msg" and "script_duration"
        """
        position = self.request.tag_info[tag]
        self._container[position] = txt
