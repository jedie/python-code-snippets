#!/usr/bin/env python
# coding: utf-8

"""
    Python web handler test
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Detect web handler: mod_wsgi, fast_CGI, mod_python or CGI and display many informations

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
        * update ModuleInfo()

    Tested with mod_rewrite and this .htaccess:
    ==========================================================================
        # Enable execution of scripts (not needed in every cases)
        # http://httpd.apache.org/docs/2.0/mod/core.html#options
        #Options +ExecCGI

        #-----------------------------------------------------------------------
        #
        # Activate script Handler (not needed in every cases)
        # http://httpd.apache.org/docs/2.0/mod/mod_mime.html#addhandler
        #

        # libapache2-mod-wsgi
        #AddHandler wsgi-script .py

        # Old libapache2-mod-fastcgi Apache module:
        #AddHandler fastcgi-script .py

        # New libapache2-mod-fcgid Apache module:
        #AddHandler fcgid-script .py

        # libapache2-mod-python
        #AddHandler mod_python .py
        #PythonHandler python_test
        #PythonDebug on

        # normal CGI
        #AddHandler cgi-script .py

        #-----------------------------------------------------------------------

        # http://httpd.apache.org/docs/2.0/mod/mod_rewrite.html
        RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ python_test.py/$1 [QSA,L]

    ==========================================================================

    :copyleft: 2011 by Jens Diemer
    :license: GNU GPL v3 or above
"""

from cgi import escape
import atexit
import datetime
import glob
import imp
import logging
import os
import sys
import time
import traceback

START_TIME = time.time()

try:
    import pwd
except Exception, err:
    pwd_availabe = err
else:
    pwd_availabe = True


SCRIPT_FILENAME = os.path.abspath(__file__)
BASE_NAME = os.path.splitext(os.path.basename(SCRIPT_FILENAME))[0]
BASE_PATH = os.path.dirname(SCRIPT_FILENAME)
LOGFILE = os.path.join(BASE_PATH, BASE_NAME + ".log")


# Setup logging
log = logging.getLogger(BASE_NAME)
handler = logging.FileHandler(filename=LOGFILE)
formatter = logging.Formatter('%(asctime)s PID:%(process)d %(levelname)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


log.info("start up %r" % __file__)
atexit.register(log.info, "-- END --")


MOD_WSGI = "mod_WSGI"
FASTCGI = "fast_CGI"
MOD_PYTHON = "mod_Python"
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
    def set_fastcgi(self):
        self._set(FASTCGI)

    @classmethod
    def set_mod_python(self):
        self._set(MOD_PYTHON)

    @classmethod
    def set_cgi(self):
        self._set(CGI)



def tail_log(max=20):
    """ returns the last >max< lines, from LOGFILE """
    try:
        f = file(LOGFILE, "r")
        seekpos = -80 * max
        try:
            f.seek(seekpos, 2)
        except IOError: # File is to small
            pass
        last_lines = "".join(f.readlines()[-max:])
        f.close()
        return last_lines
    except:
        return "Error, getting %r content:\n%s" % (
            LOGFILE, traceback.format_exc()
        )


def get_apache_load_files(path):
    """ Simply get a list of all *.load files from the path. """
    modules = []
    for item in os.listdir(path):
        filepath = os.path.join(path, item)
        if os.path.isfile(filepath):
            name, ext = os.path.splitext(item)
            if ext == ".load" and name not in modules:
                modules.append(name)
    return modules


class ModuleInfo(object):
    """
    Auflisten aller installierten Module
    """
    def __init__(self):
        self.glob_suffixes = self.get_suffixes()
        filelist = self.scan()
        self.modulelist = self.test(filelist)

    def get_suffixes(self):
        """
        Liste aller Endungen aufbereitet für glob()
        """
        suffixes = ["*" + i[0] for i in imp.get_suffixes()]
        suffixes = "[%s]" % "|".join(suffixes)
        return suffixes

    def get_files(self, path):
        """
        Liefert alle potentiellen Modul-Dateien eines Verzeichnisses
        """
        files = []
        for suffix in self.glob_suffixes:
            searchstring = os.path.join(path, suffix)
            files += glob.glob(searchstring)
        return files

    def scan(self):
        """
        Verzeichnisse nach Modulen abscannen
        """
        filelist = []
        pathlist = sys.path
        for path_item in pathlist:
            if not os.path.isdir(path_item):
                continue

            for filepath in self.get_files(path_item):
                filename = os.path.split(filepath)[1]
                if filename.startswith(".") or filename.startswith("_"):
                    continue
                if filename == "__init__.py":
                    continue

                filename = os.path.splitext(filename)[0]
                if filename in filelist:
                    continue
                else:
                    filelist.append(filename)

        return filelist

    def test(self, filelist):
        """
        Testet ob alle gefunden Dateien auch als Modul
        importiert werden können
        """
        modulelist = []
        for filename in filelist:
            try:
                imp.find_module(filename)
            except:
                continue
            modulelist.append(filename)
        modulelist.sort()
        return modulelist


def get_ip_info():
    try:
        import socket
        domain_name = socket.getfqdn()
    except Exception, err:
        domain_name = "[Error: %s]" % err
        ip_addresses = "-"
    else:
        try:
            ip_addresses = ", ".join(socket.gethostbyname_ex(domain_name)[2])
        except Exception, err:
            ip_addresses = "[Error: %s]" % err
    return ip_addresses, domain_name


def get_userinfo():
    uid = "???"
    username = "???"
    try:
        uid = os.getuid()
    except Exception, err:
        uid = "[Error: %s]" % err
        username = "-"

    if pwd_availabe != True:
        return uid, pwd_availabe

    try:
        username = pwd.getpwuid(uid)
    except Exception, err:
        username = "[Error: %s]" % err

    return uid, username


def human_duration(t):
    """ Converts a time duration into a friendly text representation. """
    chunks = (
      (60 * 60 * 24 * 365, 'years'),
      (60 * 60 * 24 * 30, 'months'),
      (60 * 60 * 24 * 7, 'weeks'),
      (60 * 60 * 24, 'days'),
      (60 * 60, 'hours'),
    )

    if t < 1: return "%.1f ms" % round(t * 1000, 1)
    if t < 60: return "%.1f sec" % round(t, 1)
    if t < 60 * 60: return "%.1f min" % round(t / 60, 1)

    for seconds, name in chunks:
        count = t / seconds
        if count >= 1:
            count = round(count, 1)
            break
    return "%.1f %s" % (count, name)


def _info_app(environ, start_response):
    """
    Fallback application, used to display the user some information, why the
    main app doesn't start.
    """
    request_start = time.time()

    log.info("info_app() - START")
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield "<!DOCTYPE HTML><html><body>"
    yield "<h1>Python web test</h1>"

    #_________________________________________________________________________
    yield "<p>run as: <strong>"
    if RunningType.RUNNING_TYPE is None:
        yield "unknown!"
    else:
        yield RunningType.RUNNING_TYPE
        if RunningType.RUNNING_TYPE is MOD_WSGI:
            try:
                from mod_wsgi import version
                yield " v%s" % ".".join([str(i) for i in version])
            except ImportError, err:
                yield " - %s" % err
        elif RunningType.RUNNING_TYPE is MOD_PYTHON:
            try:
                # http://www.dscpl.com.au/wiki/ModPython/Articles/GettingModPythonWorking
                import mod_python
            except ImportError:
                pass
            else:
                yield " v%s" % getattr(mod_python, "version", "<3.2")
                try:
                    import mod_python.psp
                except ImportError, err:
                    yield " (import mod_python.psp error: %s)" % err
                else:
                    yield " (mod_python.psp exists)"
    yield "</stong></p>"

    #_________________________________________________________________________
    yield "<h2>System informations:</h2>"
    yield "<table>"
    yield '<tr><th>Python version</th><td>%s</td></tr>' % sys.version
    yield '<tr><th>sys.prefix</th><td>%s</td></tr>' % sys.prefix
    yield '<tr><th>__name__</th><td>%s</td></tr>' % __name__
    yield '<tr><th>os.uname</th><td>%s</td></tr>' % " ".join(os.uname())
    yield '<tr><th>script file</th><td>%s</td></tr>' % SCRIPT_FILENAME

    yield '<tr><th>PID</th><td>%s</td></tr>' % os.getpid()
    yield '<tr><th>UID / pwd_info</th><td>%s / %s</td></tr>' % get_userinfo()
    yield '<tr><th>GID</th><td>%s</td></tr>' % os.getgid()

    ips, domain = get_ip_info()
    yield '<tr><th>IPs</th><td>%s</td></tr>' % ips
    yield '<tr><th>domain</th><td>%s</td></tr>' % domain
    yield '<tr><th>Server time (UTC)</th><td>%s</td></tr>' % datetime.datetime.utcnow().isoformat(' ')
    yield "</table>"

    #_________________________________________________________________________
    yield "<h2>Apache modules:</h2>"
    try:
        path = "/etc/apache2/mods-enabled"
        yield "<p><small>(*.load files from %r)</small><br />" % path
        modules = get_apache_load_files(path)
        yield ", ".join(sorted(modules))
        yield "</p>"
    except:
        yield "Error: %s" % traceback.format_exc()

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

    #_________________________________________________________________________
    yield "<h2>Existing Python modules:</h2>"
    m = ModuleInfo()
    yield "<p>%s</p>" % ", ".join(m.modulelist)

    yield "<h2>Last lines in %s</h2>" % LOGFILE
    yield "<pre>%s</pre>" % tail_log()

    yield "<hr />"

    yield "<p>Render time: request: %s total: %s</p>" % (
        human_duration(time.time() - request_start),
        human_duration(time.time() - START_TIME),
    )

    yield "<p>-- END --</p>"
    yield "</body></html>"
    log.info("info_app() - END")


def info_app(environ, start_response):
    try:
        for snippet in _info_app(environ, start_response):
            yield snippet
    except:
        log.error(traceback.format_exc())
        raise


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
        if "CGI" in os.environ.get("GATEWAY_INTERFACE", ""): # normal CGI
            RunningType.set_cgi()
            from wsgiref.handlers import CGIHandler
            CGIHandler().run(info_app)
        else:
            # fast_CGI ?
            RunningType.set_fastcgi()
            from flup.server.fcgi import WSGIServer
            WSGIServer(info_app).run()
    else:
        log.error("Unknown __name__ value!")
except:
    log.error(traceback.format_exc())
    raise





