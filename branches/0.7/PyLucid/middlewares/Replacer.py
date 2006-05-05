#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfache Middelware um <script_duration /> in den
Ausgaben zu ersetzten.
"""

import time, re

WSGIrequestKey = "colubrid.request"


# Als erstes Mal die Zeit stoppen ;)
start_time = time.time()
start_clock = time.clock()


class ReplacerBase(object):

    def __init__(self, app):
        self.app = app

    def rewrite(self, line, environ):
        raise NotImplementedError

    def __call__(self, environ, start_response):
        result = iter(self.app(environ, start_response))
        for line in result:
            yield self.rewrite(line, environ)
        if hasattr(result, 'close'):
            result.close()


class ReplaceDurationTime(ReplacerBase):
    """
    <lucidTag:script_duration/> - ersetzten
    """
    def __init__(self, app, durationTag):
        self.app = app
        self.durationTag = durationTag

    def rewrite(self, line, environ):
        end_time = time.time()
        end_clock = time.clock()
        time_string = "%.2fCPU %.2fsec" % (end_clock-start_clock, end_time-start_time)

        line = line.replace(self.durationTag, "%s" % time_string)

        return line


class ReplacePageMsg(ReplacerBase):
    """
    <lucidTag:page_msg/> - ersetzten
    """
    def __init__(self, app, pageMsgTag):
        self.app = app
        self.pageMsgTag = pageMsgTag
        #self.data = None

    def rewrite(self, line, environ):
        request = environ[WSGIrequestKey]
        page_msg = request.page_msg

        line = line.replace(self.pageMsgTag, page_msg.get())
        return line


class ReplacePyLucidTags(ReplacerBase):
    """
    Alle Tags in der Seite ersetzten...
    """
    def __init__(self, app):
        self.app = app
        #self.data = None

        self.tag_data = {} # "Statische" Tags-Daten
        self.ignore_tag = ("page_msg", "script_duration")

        self.lucidTagRE = re.compile("<lucidTag:(.*?)/?>")
        self.lucidFunctionRE = re.compile("<lucidFunction:(.*?)>(.*?)</lucidFunction>")


    def rewrite(self, line, environ):
        request = environ[WSGIrequestKey]
        if request.runlevel == "install":
            return line

        # Shorthands
        self.page_msg       = request.page_msg
        self.module_manager = request.module_manager
        self.staticTags     = request.staticTags

        if "<lucidTag:" in line:
            line = self.lucidTagRE.sub(self.handle_tag, line)
        if "<lucidFunction:" in line:
            line = self.lucidFunctionRE.sub(self.handle_function, line)

        #~ line = line.replace(self.pageMsgTag, page_msg.get())
        return line

    def handle_tag(self, matchobj):
        """
        Abarbeiten eines <lucidTag:... />
        """
        return_string = self.appy_tag(matchobj)
        if type(return_string) != str:
            self.page_msg("result of tag '%s' is not type string! Result: '%s'" % (
                    matchobj.group(1), cgi.escape( str(return_string) )
                )
            )

            return_string = str(return_string)

        return return_string


    def appy_tag(self, matchobj):
        tag = matchobj.group(1)

        #~ self.page_msg("tag: %s" % tag)

        if tag in self.ignore_tag:
            # Soll ignoriert werden. Bsp.: script_duration, welches wirklich am ende
            # erst "ausgefüllt" wird ;)
            return matchobj.group(0)

        if self.staticTags.has_key(tag):
            # Als "Statische" Information vorhanden
            return self.staticTags[tag]

        content = self.module_manager.run_tag(tag)
        if type(content) != str:
            content = "<p>[Content from module '%s' is not type string!] Content:</p>%s" % (
                tag, str(content)
            )
        return content

        return matchobj.group(0)


    def handle_function(self, matchobj):
        function_name = matchobj.group(1)
        function_info = matchobj.group(2)

        #~ print function_name, function_info

        content = self.module_manager.run_function( function_name, function_info )
        if type(content) != str:
            content = "<p>[Content from module '%s' is not type string!] Content:</p>%s" % (
                function_name, str(content)
            )
        return content












