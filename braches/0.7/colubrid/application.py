# -*- coding: utf-8 -*-
"""
    Colubrid Base Applications
    --------------------------
    This file provides a list of colubrid application. Each of them inherits
    form BaseApplication and implements a full WSGI compatible web application.
    
    If you like to add your own you _have_ to inherit from BaseApplication or
    the Request object wont work properly.
"""

from __future__ import generators
from colubrid.request import Request
from colubrid.exceptions import ColubridException, RequestBreak, HttpRedirect,\
                                PageNotFoundException
from colubrid.utils import ERROR_PAGE_TEMPLATE, splitpath, fix_slash
from colubrid.const import HTTP_STATUS_CODES
from urllib import quote
import inspect
import re

__all__ = ['BaseApplication', 'RegexApplication', 'PathApplication',
           'ObjectApplication', 'WebpyApplication']


class RequestIterator(object):

    def __init__(self, request, close_method):
        self._next = iter(request).next
        self._close = close_method
        
    def __iter__(self):
        return self
        
    def next(self):
        return self._next()
        
    def close(self):
        self._close()


class RegexCompilerClass(type):

    def __new__(cls, name, bases, d):
        result = type.__new__(cls, name, bases, d)
        if type(bases[0]) == type:
            return result
        if not hasattr(result, 'urls'):
            raise TypeError, 'Regex application without url definition.'
        compiled_urls = []
        for args in result.urls:
            args = list(args)
            args[0] = re.compile(args[0])
            compiled_urls.append(tuple(args))
        result.urls = compiled_urls
        return result


class BaseApplication(object):

    def __init__(self, environ, start_response):
        self.request = Request(environ, start_response)
    
    def on_page_not_found(self, args):
        url = self.request.environ['APPLICATION_REQUEST']
        self.request.reset()
        self.request.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.request.status = 404
        self.request.write(ERROR_PAGE_TEMPLATE % {
            'title': '404 Page Not Found',
            'msg': 'The requested URL %s was not found on this server.' % url
        })
        
    def on_access_denied(self, args):
        url = self.request.environ['APPLICATION_REQUEST']
        self.request.reset()
        self.request.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.request.status = 403
        self.request.write(ERROR_PAGE_TEMPLATE % {
            'title': '403 Forbidden',
            'msg': 'You don\'t have permission to access %s on this server.' % url
        })
        
    def on_unknown_error(self, args):
        self.request.reset()
        self.request.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.request.status = 500
        self.request.write(ERROR_PAGE_TEMPLATE % {
            'title': '500 Internal Server Error',
            'msg': 'An unknown Exception occoured.'
        })
        
    def on_http_redirect(self, args):
        url = self.request.make_canonical(args[0])
        try:
            code = int(args[1])
        except:
            code = 302
        self.request.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.request.headers['Location'] = url
        self.request.status = code
        self.request.write(ERROR_PAGE_TEMPLATE % {
            'title': '%i %s' % (code, HTTP_STATUS_CODES[code]),
            'msg': 'Redirecting... If your browser doesn\'t redirect '\
                   'follow this link: <a href="%s">%s</a>' % (url, url)
        })
    
    def on_close(self):
        pass
    
    def process_request(self):
        raise NotImplementedError
    
    def __iter__(self):
        try:
            self.process_request()
        except RequestBreak:
            pass
        except Exception, e:
            if isinstance(e, ColubridException):
                e(self)
            else:
                raise
        return RequestIterator(self.request, self.on_close)


class RegexApplication(BaseApplication):
    __metaclass__ = RegexCompilerClass
    
    def process_request(self):
        path_info = self.request.environ.get('PATH_INFO', '/')[1:]
        if hasattr(self, 'slash_append') and self.slash_append:
            fix_slash(self.request, True)
        for url, module in self.urls:
            matchobj = url.search(path_info)
            if not matchobj is None:
                args = matchobj.groups()
                if not '.' in module:
                    handler = getattr(self, module)
                else:
                    mname, fname = module.rsplit('.', 1)
                    package = __import__(mname, '', '', [''])
                    handler = getattr(package.fname)
                    args = list(args)
                    args.insert(0, self.request)
                    args = tuple(args)
                if handler in (True, False):
                    return fix_slash(self.request, handler == True)
                return handler(*args)
        raise PageNotFoundException


class WebpyApplication(BaseApplication):
    __metaclass__ = RegexCompilerClass
    
    def process_request(self):
        path_info = self.request.environ.get('PATH_INFO', '/')[1:]
        if hasattr(self, 'slash_append') and self.slash_append:
            fix_slash(self.request, True)
        for url, cls in self.urls:
            matchobj = url.search(path_info)
            if not matchobj is None:
                cls = cls()
                cls.request = self.request
                handler = getattr(cls, self.request.environ['REQUEST_METHOD'])
                if handler in (True, False):
                    return fix_slash(self.request, handler == True)
                return handler(*matchobj.groups())
        raise PageNotFoundException


class PathApplication(BaseApplication):

    def process_request(self):
        path_info = self.request.environ.get('PATH_INFO', '/').strip('/')
        parts = path_info.strip('/').split('/')
        if not len(parts) or not parts[0]:
            handler = 'show_index'
            args = ()
        else:
            handler = 'show_%s' % parts[0]
            args = tuple(parts[1:])
        if hasattr(self, handler):
            return getattr(self, handler)(*args)
        fix_slash(self.request, True)
        raise PageNotFoundException


class ObjectApplication(BaseApplication):
    """
        a rather complex application type.
        it uses python class structures to handler the user requests.
        
        an ObjectApplication might look like this:
        
            class HelloWorld(object):
                def index(self):
                    self.request.write('Hello World!')
                def name(self, name="Nobody"):
                    self.request.write('Hello %s!' % name)
            
            class AdminPanel(object):
                def index(self):
                    pass
                def login(self):
                    pass
            
            class DispatcherApplication(ObjectApplication):
                root = HelloWorld
                root.admin = AdminPanel
                
            app = DispatcherApplication
        
        Let's say that the application listens on localhost:
        
            http://localhost/               --> HelloWorld.index()
            http://localhost/name/          --> HelloWorld.name('Nobody')
            http://localhost/name/Max       --> HelloWorld.name('Max')
            http://localhost/admin/         --> AdminPanel.index()
            http://localhost/admin/login    --> AdminPanel.login()
    """

    def process_request(self):
        if not hasattr(self, 'root'):
            raise AttributeError, 'ObjectApplication requires a root object.'
        
        path_info = self.request.environ.get('PATH_INFO', '/')
        path = splitpath(path_info)
        handler, handler_args = self._find_object(path)
        if not handler is None:
            args, vargs, kwargs, defaults = None, None, None, None
            try:
                args, varargs, kwargs, defaults = inspect.getargspec(handler)
                args = args[1:]
            except:
                pass
            if defaults is None:
                defaults = ()
            min_len = len(args) - len(defaults)
            max_len = len(args)
            handler_len = len(handler_args)
            
            if not hasattr(handler, 'container'):
                if not handler_args and max_len != 0:
                    handler.__dict__['container'] = True
                else:
                    handler.__dict__['container'] = False
            # now we call the redirect method
            # if it forces an redirect the __iter__ method skips the next
            # part. call it magic if you like -.-
            fix_slash(self.request, handler.container)
            
            if min_len <= handler_len <= max_len:
                parent = handler.im_class()
                parent.request = self.request
                return handler(parent, *handler_args)
        
        raise PageNotFoundException
        
    def _find_object(self, path):
        """
            finds an object in the root of an application
            when the search method encounters an `index` method it
            checks for arguments. If there are no arguments and there is
            no container definition it will set container to true.
            This will only happen if there is no single argument. If you
            want to force container behaviour for the index method with
            a possible argument call you have to set container to true in
            the method definition.
        """
        info_path = ['root'] + path
        node = self
        trail = []
        for part in info_path:
            node = getattr(node, part, None)
            trail.append((part, node))
        
        result = []
        args = []
        for name, obj in trail:
            if name.startswith('_'):
                break
            if obj is None:
                if name:
                    args.append(name)
            else:
                result.append(obj)
        
        if result:
            if inspect.ismethod(result[-1]):
                handler = result[-1]
                if handler.__name__ == 'index':
                    # in this case the index method is the leaf of itself
                    # so we don't want an additional slash. even if forced.
                    handler.__dict__['container'] = False
                return handler, args
            else:
                # no method found. so let's try for an index method
                index = getattr(result[-1], 'index', None)
                if not index is None:
                    # we found a matching method. but is it an container?
                    if not hasattr(index, 'container') and not args:
                        index.__dict__['container'] = True
                    return index, args
        
        return None, None
