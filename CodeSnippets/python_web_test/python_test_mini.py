#!/usr/bin/env python
# coding: utf-8

"""
    Python web handler test mini
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Detect web handler: mod_wsgi, fast_CGI, mod_python or CGI

    You should check if the shebang is ok for your environment!
        some examples:
            #!/usr/bin/env python
            #!/usr/bin/env python2.4
            #!/usr/bin/env python2.5
            #!/usr/bin/python
            #!/usr/bin/python2.4
            #!/usr/bin/python2.5
            #!C:\python\python.exe

    TODO:
        * Better differentiation between CGI and FastCGI
        * mod_python logs same lines very often, why?

    :copyleft: 2011 by Jens Diemer
    :license: GNU GPL v3 or above
"""

from cgi import escape
import atexit
import datetime
import logging
import os
import sys
import tempfile
import traceback


SCRIPT_FILENAME = os.path.abspath(__file__)
BASE_NAME = os.path.splitext(os.path.basename(SCRIPT_FILENAME))[0]
BASE_PATH = os.path.dirname(SCRIPT_FILENAME)
LOGFILE = os.path.join(BASE_PATH, BASE_NAME + ".log")


#______________________________________________________________________________
# Setup logging
log = logging.getLogger(BASE_NAME)

# Depending on the user that runs the process, we have different file write rights
# Try to find a filepath in which we can write out log output
possible_paths = (BASE_PATH, tempfile.gettempdir(), os.path.expanduser("~/tmp"), "tmp")
for path in possible_paths:
    LOGFILE = os.path.join(path, BASE_NAME + ".log")
    try:
        handler = logging.FileHandler(filename=LOGFILE)
    except IOError, err:
        continue
    else:
        log.addHandler(handler)
        break

formatter = logging.Formatter('%(asctime)s PID:%(process)d %(levelname)s: %(message)s')
handler.setFormatter(formatter)
log.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------


log.info("start up %r" % __file__)
atexit.register(log.info, "-- END --")


#------------------------------------------------------------------------------


MOD_WSGI = "mod_WSGI"
FASTCGI = "fast_CGI with old libapache2-mod-fastcgi Apache module"
FCGID = "fast_CGI with new libapache2-mod-fcgid Apache module"
MOD_PYTHON = "mod_Python"
SCGI_WSGI = "SCGI"
CGI = "CGI"

class RunningType(object):
    RUNNING_TYPE = None

    @classmethod
    def _set(self, run_type):
        log.info("Detect run type: %s" % run_type)
        self.RUNNING_TYPE = run_type

    @classmethod
    def set_mod_wsgi(self):
        self._set(MOD_WSGI)

    @classmethod
    def set_fcgid(self):
        self._set(FCGID)

    @classmethod
    def set_fastcgi(self):
        self._set(FASTCGI)

    @classmethod
    def set_mod_python(self):
        self._set(MOD_PYTHON)

    @classmethod
    def set_scgi_wsgi(self):
        self._set(SCGI_WSGI)

    @classmethod
    def set_cgi(self):
        self._set(CGI)


#------------------------------------------------------------------------------


def info_app(environ, start_response):
    """
    Fallback application, used to display the user some information, why the
    main app doesn't start.
    """
    log.info("info_app() - START")
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield "<!DOCTYPE HTML><html><body>"
    yield "<h1>Python web test mini</h1>"

    #_________________________________________________________________________
    yield "<p>run as: <strong>"
    if RunningType.RUNNING_TYPE is None:
        yield "unknown!"
    else:
        yield RunningType.RUNNING_TYPE
    yield "</stong></p>"

    #_________________________________________________________________________
    yield "<h2>System informations:</h2>"
    yield "<table>"
    yield '<tr><th>Python version</th><td>%s</td></tr>' % sys.version
    yield '<tr><th>sys.prefix</th><td>%s</td></tr>' % sys.prefix
    yield '<tr><th>__name__</th><td>%s</td></tr>' % __name__
    yield '<tr><th>os.uname</th><td>%s</td></tr>' % " ".join(os.uname())
    yield '<tr><th>script file</th><td>%s</td></tr>' % SCRIPT_FILENAME
    yield '<tr><th>sys.argv</th><td>%s</td></tr>' % sys.argv
    yield '<tr><th>PID</th><td>%s</td></tr>' % os.getpid()
    yield '<tr><th>UID</th><td>%s</td></tr>' % os.getuid()
    yield '<tr><th>GID</th><td>%s</td></tr>' % os.getgid()
    yield '<tr><th>Server time (UTC)</th><td>%s</td></tr>' % datetime.datetime.utcnow().isoformat(' ')
    yield "</table>"

    #_________________________________________________________________________
    yield "<h2>Environments</h2>"

    if RunningType.RUNNING_TYPE == MOD_PYTHON:
        env_name = "mod_python"
    else:
        env_name = "WSGI"
    yield "<h3>%s Environment</h3>" % env_name
    yield "<table>"
    for k, v in sorted(environ.items()):
        yield '<tr><th>%s</th><td>%s</td></tr>' % (escape(k), escape(repr(v)))
    yield "</table>"

    yield "<h3>OS Environment</h3>"
    yield "<table>"
    for k, v in sorted(os.environ.items()):
        yield '<tr><th>%s</th><td>%s</td></tr>' % (escape(k), escape(v))
    yield "</table>"

    #_________________________________________________________________________
    yield "<h2>python sys.path</h2>"
    yield "<ul>"
    for path in sys.path:
        yield "<li>%s</li>" % path
    yield "</ul>"

    yield "<hr />"
    yield "<p>-- END --</p>"
    yield "</body></html>"
    log.info("info_app() - END")


try:
    log.debug("__name__ == %s" % repr(__name__))
    if __name__.startswith('_mod_wsgi_'): # mod_wsgi
        RunningType.set_mod_wsgi()
        application = info_app

    elif __name__.startswith('_mp_'): # mod_python
        RunningType.set_mod_python()
        from mod_python import apache
        def fake_start_reponse(*args, **kwargs):
            pass
        def handler(req):
            req.content_type = "text/html"
            req.send_http_header()
            for line in info_app(req.subprocess_env, fake_start_reponse):
                req.write(line)
            return apache.OK

    elif __name__ == "__main__":

        if sys.argv[0] == "scgi-wsgi":
            RunningType.set_scgi_wsgi()
            raise NotImplemented

        elif "scgi" in sys.argv:
            # Startup a SCGI server (needs flup packages)
            if len(sys.argv) == 4:
                address = sys.argv[2], int(sys.argv[3])
            else:
                address = ('localhost', 4000)

            # Display own logs on console
            console = logging.StreamHandler()
            log.addHandler(console)

            RunningType.set_scgi_wsgi()

            log.info("Start SCGI server on %s:%s" % address)
            from flup.server.scgi import WSGIServer
            ret = WSGIServer(info_app, bindAddress=address, debug=True).run()
            sys.exit(ret and 42 or 0)

        # FIXME: How can we differentiate CGI, fast_CGI and fcgid better?
        if "CGI" in os.environ.get("GATEWAY_INTERFACE", ""): # normal CGI
            RunningType.set_cgi()
            from wsgiref.handlers import CGIHandler
            CGIHandler().run(info_app)
        elif "PATH" in os.environ:
            # New libapache2-mod-fcgid Apache module
            RunningType.set_fcgid()
        else:
            # Old libapache2-mod-fastcgi Apache module
            RunningType.set_fastcgi()

        from flup.server.fcgi import WSGIServer
        WSGIServer(info_app).run()
    else:
        log.error("Unknown __name__ value!")
except:
    log.error(traceback.format_exc())
    raise




