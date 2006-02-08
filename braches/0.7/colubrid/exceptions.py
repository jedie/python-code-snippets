# -*- coding: utf-8 -*-
"""
    Colubrid Exceptions
    -------------------
"""

class RequestBreak(Exception):
    """terminates the current request. the application will
    continue sending output."""


class ExceptionHandlerNotFound(Exception):
    """gets thrown when an exception can't find an exception handler
    in the application."""


class ColubridException(Exception):

    def __call__(self, application):
        handler = (hasattr(self, 'handler')) and self.handler or 'on_unknown_error'
        if not hasattr(application, self.handler):
            raise ExceptionHandlerNotFound, self.handler
        getattr(application, self.handler)(self.args)
        

class PageNotFoundException(ColubridException):
    """displays an error404 errorpage."""
    handler = 'on_page_not_found'


class AccessDeniedExceptions(ColubridException):
    """displays an error403 errorpage."""
    handler = 'on_access_denied'


class HttpRedirect(ColubridException):
    """redirects to another page."""
    handler = 'on_http_redirect'
