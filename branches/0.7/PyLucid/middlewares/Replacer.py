#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfache Middelware um <script_duration /> in den
Ausgaben zu ersetzten.
"""

WSGIrequestKey = "colubrid.request"


# Als erstes Mal die Zeit stoppen ;)
import time
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

    def __init__(self, app, pageMsgTag):
        self.app = app
        self.pageMsgTag = pageMsgTag
        #self.data = None

    def rewrite(self, line, environ):
        request = environ[WSGIrequestKey]
        page_msg = request.page_msg

        line = line.replace(self.pageMsgTag, page_msg.get())
        return line
        
        
