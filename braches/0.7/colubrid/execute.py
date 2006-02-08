# -*- coding: utf-8 -*-
"""
    Colubrid Execute
    ----------------
    when importing colubrid it calls the register() method of this file.
    the register method looks for the main application frame and for a
    application object.

    If you define a class called "app" somewhere in your application
    which name isn't "app" and you execute this file colubrid spawns
    a wsgi server on localhost:8080.

    When called as CGI or FastCGI application it tries to find the flup
    FastCGI wrapper, when not found it returns a simple CGI Wrapper.
"""

from __future__ import generators
import os
import sys
import atexit
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse
import socket
from colubrid.debug import DebuggedApplication


class CGIServer(object):

    def __init__(self, application, exports={}):
        self.application = application
        self.exports = exports

    def send_files(self, path_info):
        for search_path, file_path in self.exports.iteritems():
            if not search_path.endswith('/'):
                search_path += '/'
            if path_info.startswith(search_path):
                real_path = os.path.join(file_path, path_info[len(search_path):])
                if os.path.exists(real_path) and os.path.isfile(real_path):
                    return self.serve_file(real_path)
                return False
        return False

    def serve_file(self, filename):
        from mimetypes import guess_type
        guessed_type = guess_type(filename)
        if guessed_type[0] is None:
            mime_type = 'text/plain'
        else:
            if guessed_type[1] is None:
                mime_type = guessed_type[0]
            else:
                mime_type = ';charset='.join(guessed_type)
            sys.stdout.write('Status: 200\r\n')
            sys.stdout.write('Content-Type: %s\r\n\r\n' % mime_type)
            for line in file(filename):
                sys.stdout.write(line)
        return True

    def run(self):
        environ = dict(os.environ.items())

        if self.send_files(environ.get('PATH_INFO', '')):
            return

        environ['wsgi.input']        = sys.stdin
        environ['wsgi.errors']       = sys.stderr
        environ['wsgi.version']      = (1,0)
        environ['wsgi.multithread']  = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once']     = True

        if environ.get('HTTPS','off') in ('on','1'):
            environ['wsgi.url_scheme'] = 'https'
        else:
            environ['wsgi.url_scheme'] = 'http'

        headers_set = []
        headers_sent = []

        def write(data):
            if not headers_set:
                    raise AssertionError("write() before start_response()")

            elif not headers_sent:
                    # Before the first output, send the stored headers
                    status, response_headers = headers_sent[:] = headers_set
                    sys.stdout.write('Status: %s\r\n' % status)
                    for header in response_headers:
                        sys.stdout.write('%s: %s\r\n' % header)
                    sys.stdout.write('\r\n')

            sys.stdout.write(data)
            sys.stdout.flush()

        def start_response(status,response_headers,exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        # Re-raise original exception if headers sent
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None     # avoid dangling circular ref
            elif headers_set:
                raise AssertionError("Headers already set!")

            headers_set[:] = [status,response_headers]
            return write

        result = self.application(environ, start_response)
        try:
            for data in result:
                if data:    # don't send headers until body appears
                    write(data)
            if not headers_sent:
                write('')   # send headers now if body was empty
        finally:
            if hasattr(result,'close'):
                result.close()


class WSGIHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path_info, parameters, query = urlparse(self.path)[2:5]

        for search_path, file_path in self.server.exports.iteritems():
            if not search_path.endswith('/'):
                search_path += '/'
            if path_info.startswith(search_path):
                real_path = os.path.join(file_path, path_info[len(search_path):])
                print real_path
                if os.path.exists(real_path) and os.path.isfile(real_path):
                    return self.serve_file(real_path)
                self.send_error(404, 'File not found')
                return

        self.run_application(path_info, parameters, query)

    def do_POST(self):
        self.run_application(*urlparse(self.path)[2:5])

    def run_application(self, path_info, parameters, query):
        app = self.server.application
        environ = {
            'wsgi.version':         (1,0),
            'wsgi.url_scheme':      'http',
            'wsgi.input':           self.rfile,
            'wsgi.errors':          sys.stderr,
            'wsgi.multithread':     1,
            'wsgi.multiprocess':    0,
            'wsgi.run_once':        0,
            'REQUEST_METHOD':       self.command,
            'SCRIPT_NAME':          '',
            'QUERY_STRING':         query,
            'CONTENT_TYPE':         self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH':       self.headers.get('Content-Length', ''),
            'REMOTE_ADDR':          self.client_address[0],
            'REMOTE_PORT':          self.client_address[1],
            'SERVER_NAME':          self.server.server_address[0],
            'SERVER_POST':          self.server.server_address[1],
            'SERVER_PROTOCOL':      self.request_version,
            'DOCUMENT_ROOT':        os.getcwd(),
        }
        if path_info:
            from urllib import unquote
            environ['PATH_INFO'] = unquote(path_info)
        for key, value in self.headers.items():
            environ['HTTP_' + key.upper().replace('-', '_')] = value

        headers_set = []
        headers_sent = []

        def write(data):
            if not headers_set:
                raise AssertionError, 'write() before start_response'

            elif not headers_sent:
                status, response_headers = headers_sent[:] = headers_set
                code, msg = status.split(' ', 1)
                self.send_response(int(code), msg)
                for line in response_headers:
                    self.send_header(*line)
                self.end_headers()

            self.wfile.write(data)

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None
            elif headers_set:
                raise AssertionError, 'Headers already set!'

            headers_set[:] = [status, response_headers]
            return write

        self.application_iter = app(environ, start_response)
        try:
            try:
                for data in self.application_iter:
                    write(data)
            finally:
                if hasattr(self.application_iter, 'close'):
                    self.application_iter.close()
        except (socket.error, socket.timeout):
            return

    def serve_file(self, filename):
        from mimetypes import guess_type
        guessed_type = guess_type(filename)
        if guessed_type[0] is None:
            mime_type = 'text/plain'
        else:
            if guessed_type[1] is None:
                mime_type = guessed_type[0]
            else:
                mime_type = ';charset='.join(guessed_type)
            self.send_response(200, 'OK')
            self.send_header('Content-Type', mime_type)
            self.end_headers()
            for line in file(filename):
                self.wfile.write(line)

    def log_request(self, *args, **kwargs):
        if self.server.quiet:
            return
        BaseHTTPRequestHandler.log_request(self, *args, **kwargs)

    def close(self):
        pass


class StandaloneServer(ThreadingMixIn, HTTPServer):

    def __init__(self, application, exports, hostname, port, noreload, quiet):
        print "Starting standalone Server at '%s' port:%s" % (hostname, port)
        HTTPServer.__init__(self, (hostname, port), WSGIHandler)
        self.application = application
        self.exports = exports
        self.quiet = quiet
        self.noreload = noreload

    def reload_modules(self):
        if self.noreload:
            return False
        if not hasattr(self, '_module_mtimes'):
            self._module_mtimes = {}
        for mod in sys.modules.values():
            try:
                mtime = os.stat(mod.__file__).st_mtime
            except (AttributeError, OSError, IOError):
                continue
            if mod.__file__.endswith('.pyc') or mod.__file__.endswith('.pyo')\
               and os.path.exists(mod.__file__[:-1]):
                mtime = max(os.stat(mod.__file__[:-1]).st_mtime, mtime)
            if mod not in self._module_mtimes:
                self._module_mtimes[mod] = mtime
            elif self._module_mtimes[mod] < mtime:
                return True
        return False

    def serve_forever(self):
        raise NotImplementedError, 'use run() to start the server.'

    def run(self):
        while True:
            try:
                if self.reload_modules():
                    req = self.get_request()[0]
                    if hasattr(req, 'application_iter'):
                        if hasattr(req.application_iter, 'close'):
                            self.req.application_iter.close()
                        del self.req.application_iter
                    self.close_request(req)
                    self.server_close()
                    return True
                self.handle_request()
            except KeyboardInterrupt:
                break
        return False


class CommandlineApplication(object):

    def __init__(self, root):
        self.root = root
        self.app = None
        self.exports = {}

    def run(self):
        if 'app' in self.root.f_globals:
            app = self.root.f_globals['app']
            if not hasattr(app, '__name__'):
                app.__name__ = app.__class__.__name__
            if app.__name__ != 'app' and app.__name__ in self.root.f_globals:
                self.app = DebuggedApplication(app)
                if 'exports' in self.root.f_globals:
                    self.exports = self.root.f_globals['exports']
        if self.app is None:
            return

        self.handle_parameters()

    def handle_parameters(self):
        from optparse import OptionParser
        usage = 'usage: %prog ACTION [options]'
        parser = OptionParser(usage)
        parser.add_option('-v', '--version', dest='version', action='store_true',
                          help='print Colubrid version')
        parser.add_option('-i', '--hostname', dest='hostname',
                          help='the hostname the standalone server should '\
                          'listen on. default is localhost')
        parser.add_option('-p', '--port', dest='port', type='int',
                          help='the port the standalone server should '\
                          'listen on. default is 8080')
        parser.add_option('-q', '--quiet', dest='quiet', action='store_true',
                          help='disable webserver access informations')
        parser.add_option('-n', '--no-reload', dest='no_reload',
                          action='store_true', help='disable code reloading')
        parser.add_option('--interface-type', dest='interface_type',
                          help='eighter cgi or fastcgi. cgi is default')
        parser.add_option('--path', dest='path',
                          help='path to the webapplication. default is "/"')
        parser.add_option('--vhost', dest='vhost',
                          help='name of the virtual host. default is None')
        parser.add_option('--server', dest='server',
                          help='servertype. currently only apache is supported.')
        parser.add_option('--forking', dest='forking', action='store_true',
                          help='generate a forking handler')
        options, args = parser.parse_args()

        if options.version:
            return self.display_version()

        if not args:
            parser.error('no action given')

        if args[0] == 'runserver':
            if options.hostname == None: options.hostname = "localhost"
            self.run_standalone(options.hostname,
                                options.port or 8080, bool(options.no_reload),
                                bool(options.quiet))
        elif args[0] == 'genconfig':
            server = options.server or 'apache'
            server = server.lower()
            if server == 'apache':
                self.gen_apacheconfig(options.interface_type or 'cgi',
                                      options.path or '/', options.vhost)
            else:
                print 'Server %s not supported' % server
        elif args[0] == 'genhandler':
            self.gen_handler(options.interface_type or 'cgi',
                             options.forking or False)
        else:
            parser.error('invalid action %s' % args[0])

    def display_version(self):
        from colubrid import __version__
        print 'Colubrid Version %s' % __version__

    def gen_apacheconfig(self, interface, path, vhost):
        interface = interface.lower()
        if interface in ('fastcgi', 'fcgi'):
            handler = self.gen_fastcgi_config
        elif interface == 'cgi':
            handler = self.gen_cgi_config
        else:
            print 'Unsupported Interface %s' % interface
            sys.exit(1)

        indent = ''
        if vhost:
            indent = '    '
            print '<VirtualHost *>'
            print '    ServerName %s' % vhost

        for line in handler(path, vhost):
            print '%s%s' % (indent, line)

        if vhost:
            print '</VirtualHost>'

    def gen_fastcgi_config(self, path, vhost):
        yield 'AddType fastcgi-script .fcg'
        for k, v in self.exports.iteritems():
            yield 'Alias %s %s' % (k, os.path.realpath(v))
        yield 'ScriptAlias %s %s.fcg%s' % (
            path,
            os.path.realpath(sys.argv[0].split('.')[0]),
            (path == '/') and '/' or ''
        )

    def gen_cgi_config(self, path, vhost):
        for k, v in self.exports.iteritems():
            yield 'Alias %s %s' % (k, os.path.realpath(v))
        yield 'ScriptAlias %s %s.cgi%s' % (
            path,
            os.path.realpath(sys.argv[0].split('.')[0]),
            (path == '/') and '/' or ''
        )

    def gen_handler(self, interface, forking):
        interface = interface.lower()
        if interface == 'fastcgi':
            interface = 'fcgi'
        elif interface == 'cgi':
            return self.gen_cgihandler()
        elif interface in ('fcgi', 'scgi', 'ajp'):
            return self.gen_fluphandler(interface, forking)

    def gen_fluphandler(self, interface, forking):
        handler = '%s%s' % (interface, (forking) and '_fork' or '')
        print '#!%s' % sys.executable
        print 'from flup.server.%s import WSGIServer' % handler
        print 'from %s import app' % sys.argv[0].rsplit('/')[-1].split('.')[0]
        print
        print 'if __name__ == "__main__":'
        print '    WSGIServer(app).run()'

    def gen_cgihandler(self):
        module = sys.argv[0].rsplit('/')[-1].split('.')[0]
        print '#!%s' % sys.executable
        print 'import os'
        print 'import sys'
        print 'from colubrid.execute import CGIServer'
        print 'from %s import app' % module
        print 'try:'
        print '    from %s import exports' % module
        print 'except ImportError:'
        print '    exports = {}'
        print
        print 'if __name__ == "__main__":'
        print '    CGIServer(app, exports).run()'

    def run_standalone(self, hostname, port, noreload=False, quiet=False):
        import gc
        if self.app is None:
            raise RuntimeError, 'no application found'
        srv = StandaloneServer(self.app, self.exports, hostname, port, noreload, quiet)
        if not srv.run() or noreload:
            return

        for obj in gc.get_objects():
            if hasattr(obj, '__del__'):
                try:
                    obj.__del__()
                except:
                    pass
        args = [sys.executable] + sys.argv
        os.execv(sys.executable, args)


def register():
    root = sys._getframe()
    while root.f_back:
        root = root.f_back
    atexit.register(lambda: CommandlineApplication(root).run())
