#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einfache Middelware um Tags in den
Ausgaben zu ersetzten.
"""

import time, re


init_clock = time.clock()

page_msg_tag        = "<lucidTag:page_msg/>"
script_duration_tag = "<lucidTag:script_duration/>"
# Fängt an mit PyLucid und nicht mit lucid, weil der Tag ansonsten durch
# RE im PyLucid-Response-Objekt ersetzt wird!
add_code_tag        = "<PyLucidInternal:addCode/>"



class Replacer(object):
    def __init__(self, app):
        self.app = app

    def replace_script_duration(self, line, environ):
        request_time = time.time() - environ["request_start"]
        overall_clock = time.clock() - init_clock

        time_string = "%.2fSec. - %.2foverall" % (
            request_time, overall_clock
        )

        line = line.replace(script_duration_tag, "%s" % time_string)

        return line

    def replace_page_msg(self, line, environ):
        page_msg = environ['PyLucid.page_msg']

        line = line.replace(page_msg_tag, page_msg.get())
        return line

    def addCode(self, line, environ):
        code = environ['PyLucid.addCode']
        code = code.get()

        line = line.replace(add_code_tag, code)
        return line


    def __call__(self, environ, start_response):
        result = iter(self.app(environ, start_response))

        for line in result:
            if script_duration_tag in line:
                line = self.replace_script_duration(line, environ)

            if page_msg_tag in line:
                line = self.replace_page_msg(line, environ)

            if add_code_tag in line:
                line = self.addCode(line, environ)

            yield line

        if hasattr(result, 'close'):
            result.close()



class AddCode(object):
    tag = add_code_tag

    def __init__(self, app):
        self.app = app
        self.data = ""

    def get(self):
        data = self.data
        self.data = ""
        return data

    def add(self, code):
        self.data += code

    def __call__(self, environ, start_response):
        environ['PyLucid.addCode'] = self
        return self.app(environ, start_response)















