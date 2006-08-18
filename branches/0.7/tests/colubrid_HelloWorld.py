#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,"..")

from colubrid import BaseApplication, HttpResponse

class HelloWorld(BaseApplication):

    def process_request(self):
        response = HttpResponse()
        response.headers['Content-Type'] = 'text/html'
        response.write("<h1>Hello World!</h1>")
        return response

app = HelloWorld

if __name__ == '__main__':
    from colubrid import execute
    execute(app, reload=True)