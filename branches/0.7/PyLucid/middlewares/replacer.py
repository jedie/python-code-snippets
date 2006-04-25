#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Als erstes Mal die Zeit stoppen ;)
import time
start_time = time.time()
start_clock = time.clock()

class replacer(object):

    def __init__(self, app):
        self.app = app

    def rewrite(self, line):
        end_time = time.time()
        end_clock = time.clock()
        time_string = "%.2fCPU %.2f" % (end_clock-start_clock, end_time-start_time)

        line += "XXX %s" % time_string
        line = line.replace('<lucidTag:script_duration/>', "%s" % time_string)
        line = line.replace('<lucidTag:script_duration>', "%s" % time_string)

        return line

    def __call__(self, environ, start_response):
        result = iter(self.app(environ, start_response))
        for line in result:
            yield self.rewrite(line)
        if hasattr(result, 'close'):
            result.close()

