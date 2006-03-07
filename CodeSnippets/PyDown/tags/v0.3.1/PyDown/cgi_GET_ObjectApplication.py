#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Eine abgewandelte Form von colubrid.ObjectApplication
statt auf request.environ['PATH_INFO'] zu setzten wird
einfach request.GET['action'] genommen, ansonsten
ist eigentlich alles genau wie bei der original ObjectApplication
"""

from colubrid import ObjectApplication
from colubrid.exceptions import *

# Import für ObjectApplication
import inspect
from colubrid.utils import ERROR_PAGE_TEMPLATE, splitpath, fix_slash

class ObjectApplication(ObjectApplication):
    """
        Tauschen von
        path_info = self.request.environ.get('PATH_INFO', '/')
        mit
        path_info = self.request.GET.get('action', '/')
    """

    def process_request(self):
        if not hasattr(self, 'root'):
            raise AttributeError, 'ObjectApplication requires a root object.'

        #~ path_info = self.request.environ.get('PATH_INFO', '/')
        path_info = self.request.GET.get('action', '/')
        self._process_request(path_info)

    def _process_request(self, path_info):
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

        raise PageNotFound