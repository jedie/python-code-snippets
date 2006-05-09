#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfache Middelware um <script_duration /> in den
Ausgaben zu ersetzten.
"""

import time, re


# Als erstes Mal die Zeit stoppen ;)
start_time = time.time()
start_clock = time.clock()


#~ class ReplacerBase(object):

    #~ def __init__(self, app, WSGIrequestKey):
        #~ self.app = app
        #~ self.WSGIrequestKey = WSGIrequestKey

    #~ def rewrite(self, line, environ):
        #~ raise NotImplementedError

    #~ def __call__(self, environ, start_response):
        #~ result = iter(self.app(environ, start_response))
        #~ for line in result:
            #~ yield self.rewrite(line, environ)
        #~ if hasattr(result, 'close'):
            #~ result.close()



class ReplaceDurationTime(object):
    """
    <lucidTag:script_duration/> - ersetzten
    """
    def __init__(self, app, WSGIrequestKey, durationTag):
        #~ super(ReplaceDurationTime, self).__init__(app, WSGIrequestKey)
        self.app = app

        self.durationTag = durationTag

    def rewrite(self, line, environ):
        end_time = time.time()
        end_clock = time.clock()
        time_string = "%.2fCPU %.2fsec" % (end_clock-start_clock, end_time-start_time)

        line = line.replace(self.durationTag, "%s" % time_string)

        return line

    def __call__(self, environ, start_response):
        result = iter(self.app(environ, start_response))
        for line in result:
            yield self.rewrite(line, environ)
        if hasattr(result, 'close'):
            result.close()


















