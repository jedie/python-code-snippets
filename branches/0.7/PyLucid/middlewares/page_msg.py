#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Middelware

Speichert Nachrichten die in der Seite angezeigt werden sollen
Wird am Ende des Reuqestes durch ein Replace Middleware in die
Seite eingesetzt.
"""


from PyLucid.system import sessiondata



class page_msg(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        page_msg = sessiondata.page_msg(debug=True)

        environ['PyLucid.page_msg'] = page_msg

        return self.app(environ, start_response)



class ReplacePageMsg(object):
    """
    Middleware um die page_msg in die Seite ein zu bauen

    <lucidTag:page_msg/> - wird ersetzt
    """
    def __init__(self, app, pageMsgTag):
        self.app = app
        self.pageMsgTag = pageMsgTag

    def rewrite(self, line, environ):
        page_msg = environ['PyLucid.page_msg']

        line = line.replace(self.pageMsgTag, page_msg.get())
        return line

    def __call__(self, environ, start_response):
        result = iter(self.app(environ, start_response))

        for line in result:
            if self.pageMsgTag in line:
                line = self.rewrite(line, environ)
            yield line

        if hasattr(result, 'close'):
            result.close()