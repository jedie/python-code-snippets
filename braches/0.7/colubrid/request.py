# -*- coding: utf-8 -*-
"""
    Colubrid Request Object
    -----------------------
"""

from __future__ import generators
from colubrid.utils import MultiDict, MergedMultiDict, ResponseCookie,\
                           FieldStorage, HttpHeaders, get_full_url
from colubrid.const import HTTP_STATUS_CODES
from colubrid.exceptions import RequestBreak
from colubrid.response import HttpResponse
from colubrid.debug import DebugRender

import os
import sys
import cgi
import re
import email
from urllib import quote
from email.Message import Message as MessageType
from cStringIO import StringIO


class Request(object):

    exposed = ['environ', 'GET', 'POST', 'REQUEST', 'FILES', 'COOKIES']

    def __init__(self, environ, start_response):
        self._start_response = start_response
        self._buffer = []
        self._response = False
        
        self.environ = environ
        self.environ['REQUEST_URI'] = self.get_full_url()
        self.environ['APPLICATION_REQUEST'] = self.get_application_request()
        self.headers = HttpHeaders()
        self.status = 200

    def debug_info(self):
        exposed = []
        for expose in self.exposed:
            exposed.append((expose, getattr(self, expose)))
        context = {'exposed': exposed}
        render = DebugRender(context)
        self.write(render.render())

    def expose_var(self, var):
        if not var in self.exposed:
            self.exposed.append(var)

    def get_full_url(self, append=None):
        return get_full_url(self.environ, append)
        
    def get_application_request(self):
        url = ''.join([
            quote(self.environ.get('SCRIPT_NAME', '')),
            quote(self.environ.get('PATH_INFO', ''))
        ])
        return (url.startswith('/')) and url or '/' + url
        
    def make_canonical(self, url):
        """FIXME: add code"""
        return url

    def send_response(self, response):
        self._buffer = response
        self._response = True
        if hasattr(response, 'header_modify'):
            for key, value, overwrite in response.header_modify():
                if overwrite:
                    self.headers[key] = value
                else:
                    self.headers.add(key, value)
        raise RequestBreak

    def reset(self):
        self.clear()
        self.headers.clear()
        self.status = 200

    def clear(self):
        self._buffer = []

    def echo(self, *args):
        if not args:
            raise ArgumentError, 'no data given'
        for arg in args:
            self.write(str(arg))

    def write(self, s):
        self._buffer.append(s)

    def read(self, *args):
        if not hasattr(self, '_buffered_stream'):
            self._buffered_stream = StringIO(self.DATA)
        return self._buffered_stream.read(*args)

    def readline(self, *args):
        if not hasattr(self, '_buffered_stream'):
            self._buffered_stream = StringIO(self.DATA)
        return self._buffered_stream.readline(*args)

    def readlines(self, *args):
        while True:
            line = self.readline(*args)
            if not line:
                raise StopIteration
            yield line

    def __iter__(self):
        if not self._response:
            result = HttpResponse(''.join(self._buffer))
        else:
            result = self._buffer

        status = '%i %s' % (self.status, HTTP_STATUS_CODES[self.status])
        headers = self.headers.get() + self.COOKIES.get_headers()
        self._start_response(status, headers)
        return result
    
    def _load_post_data(self):
        self._data = ''
        if self.environ['REQUEST_METHOD'] == 'POST':
            max = int(self.environ['CONTENT_LENGTH'])
            self._data = self.environ['wsgi.input'].read(max)
            if self.environ.get('CONTENT_TYPE', '').startswith('multipart'):
                lines = ['Content-Type: %s' % self.environ.get('CONTENT_TYPE', '')]
                for key, value in self.environ.items():
                    if key.startswith('HTTP_'):
                        lines.append('%s: %s' % (key, value))
                raw = '\r\n'.join(lines) + '\r\n\r\n' + self._data
                msg = email.message_from_string(raw)
                self._post = MultiDict()
                self._files = MultiDict()
                for sub in msg.get_payload():
                    if not isinstance(sub, MessageType):
                        continue
                    name_dict = cgi.parse_header(sub['Content-Disposition'])[1]
                    if 'filename' in name_dict:
                        assert type([]) != type(sub.get_payload()),\
                               'Nested MIME Messages are not supported'
                        if not name_dict['filename'].strip():
                            continue
                        filename = name_dict['filename']
                        filename = filename[filename.rfind('\\') + 1:]
                        if 'Content-Type' in sub:
                            content_type = sub['Content-Type']
                        else:
                            content_type = None
                        s = FieldStorage(name_dict['name'], filename,
                                         content_type, sub.get_payload())
                        self._files.appendlist(name_dict['name'], s)
                    else:
                        self._post.appendlist(name_dict['name'], sub.get_payload())
            else:
                self._post = MultiDict(cgi.parse_qs(self._data))
                self._files = MultiDict()
        else:
            self._post = MultiDict()
            self._files = MultiDict()
    
    def _get_get(self):
        if not hasattr(self, '_get'):
            query = cgi.parse_qs(self.environ.get('QUERY_STRING', ''))
            self._get = MultiDict(query)
        return self._get

    def _set_get(self, value):
        self._get = value
    
    def _get_post(self):
        if not hasattr(self, '_post'):
            self._load_post_data()
        return self._post

    def _set_post(self, value):
        self._post = value

    def _get_request(self):
        if not hasattr(self, '_request'):
            self._request = MergedMultiDict(self.GET, self.POST)
        return self._request

    def _get_files(self):
        if not hasattr(self, '_files'):
            self._load_post_data()
        return self._files

    def _get_data(self):
        if not hasattr(self, '_data'):
            self._load_post_data()
        return self._data
    
    def _get_cookies(self):
        if not hasattr(self, '_cookies'):
            self._cookies = ResponseCookie(self.environ)
        return self._cookies

    def _set_cookies(self, value):
        self._cookies = value
    
    GET = property(_get_get, _set_get)
    POST = property(_get_post, _set_post)
    FILES = property(_get_files)
    DATA = property(_get_data)
    COOKIES = property(_get_cookies, _set_cookies)
    REQUEST = property(_get_request)
