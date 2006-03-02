#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Ein Decorator-Handler damit Methoden einfach Templates
benutzten k�nnen.
"""

# Jinja-Template-Engine
try:
    from jinja import Template, Context, FileSystemLoader
except ImportError, e:
    print "Content-type: text/plain; charset=utf-8\r\n"
    print "<h1>Jinja-Template-Engine, Import Error: %s</h1>" % s
    print "Download at: http://wsgiarea.pocoo.org/jinja/"
    import sys
    sys.exit()


# set here the path to your templates
# you can also use a CachedFileSystemLoader
# but this decorator keeps the templates in the memory
loader = FileSystemLoader('templates/')

def render(name):
    # move this definition into the
    # on_call method to disable caching
    t = Template(name, loader)
    def proxy(f):
        def on_call(*args, **kwargs):
            req = None
            if args:
                if hasattr(args[0], 'request'):
                    req = args[0].request
                elif isinstance(args[0], Request):
                    req = args[0]
            if req is None:
                raise TypeError, 'can\'t decorate non colubrid handler'
            result = f(*args, **kwargs)
            if isinstance(result, dict):
                c = Context(result)
            else:
                c = Context()
            req.write(t.render(c))
        return on_call
    return proxy