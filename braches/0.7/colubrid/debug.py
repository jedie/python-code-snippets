# -*- coding: utf-8 -*-
"""
    Colubrid Debug Handler
    ----------------------
    to wsgi what cgitb is to cgi.
"""

from __future__ import generators
import sys
import re
import traceback
import keyword
import token
import tokenize
import string
import pprint
from cStringIO import StringIO
from xml.sax import saxutils


STYLESHEET = '''
#wsgi-traceback * { font-size: 0.99em;
    font-family: 'Trebuchet MS', sans-serif; margin: 0; padding: 0;
    color: black; text-decoration: none; font-weight: normal }
#wsgi-traceback { margin: 1em; padding: 0; border: 1px solid #12597e }
#wsgi-traceback h1 { font-weight: bold; font-size: 2em;
    background-color: #12597e; color: white; padding: 0.1em }
#wsgi-traceback h2 { background-color: #12597e; color: white;
    padding: 0.2em; font-size: 1.4em; font-weight: bold; margin: 0.7em 0 0 0 }
#wsgi-traceback h3 { font-weight: bold; background-color: #ddd;
    padding: 0.2em 0 0.2em 1em; font-size: 1em; cursor: pointer }
#wsgi-traceback h3:hover { color: white }
#wsgi-traceback h3.fn { margin-top: 0.5em; background-color: #bbb }
#wsgi-traceback p.exec { font-family: 'Bitstream Vera Sans Mono',
    Courier New, monospace; font-size: 0.9em; padding: 1.2em 1em 0 2em }
#wsgi-traceback p.info { padding: 0.2em 1em 1em 5em; font-style: italic }
#wsgi-traceback p.help { margin: 1em 2em 1em 2em }
#wsgi-traceback ul.navigation { margin: 0 0 1em 2em; list-style: none }
#wsgi-traceback ul.navigation li { float: left; }
#wsgi-traceback ul.navigation li + li:before { content: " | " }
#wsgi-traceback ul.navigation a { color: #12597e }
#wsgi-traceback ul.navigation a:hover { text-decoration: underline }
#wsgi-traceback table.code { border-collapse: collapse; width: 100% }
#wsgi-traceback table.code td { white-space: pre; font-size: 0.9em;
    font-family: 'Bitstream Vera Sans Mono', 'Courier New', monospace;
    padding: 0.2em 0.2em 0.2em 1em; border: 1px solid #ddd; }
#wsgi-traceback table.code td.lineno { background-color: #f2f2f2; width: 3em;
    font-weight: bold; text-align: right; padding: 0.2em 1em 0.2em 1em;
    color: #555 }
#wsgi-traceback table.code tr.cur td.code { background-color: #eee }
#wsgi-traceback dl dt { padding: 0.2em 0 0.2em 1em; font-weight: bold;
    cursor: pointer; background-color: #ddd }
#wsgi-traceback dl dt:hover { background-color: #bbb; color: white }
#wsgi-traceback dl dd { padding: 0 0 0 2em; background-color: #eee }
#wsgi-traceback table.vars { border-collapse: collapse; width: 100% }
#wsgi-traceback table.vars td { font-family: 'Bitstream Vera Sans Mono',
    'Courier New', monospace; font-size: 0.9em; padding: 0.3em;
    border: 1px solid #ddd; vertical-align: top; background-color: white }
#wsgi-traceback table.vars .name { font-style: italic }
#wsgi-traceback table.vars .value { color: #555 }
#wsgi-traceback table.vars th { font-weight: bold; padding: 0.2em;
    border: 1px solid #ddd; background-color: #f2f2f2; text-align: left }
#wsgi-traceback span.code-item { font-family: inherit; color: inherit;
    font-size: inherit }
#wsgi-traceback span.p-kw { font-weight: bold }
#wsgi-traceback span.p-str { color: #080; }
#wsgi-traceback span.p-num { color: #d00; }
#wsgi-traceback span.p-op { color: #008; }
#wsgi-traceback span.p-cmt { color: #888; }
'''

JAVASCRIPT = '''
function toggleBlock(handler) {
    if (handler.nodeName == 'H3') {
        var table = handler;
        do {
            table = table.nextSibling;
            if (typeof table == 'undefined') {
                return;
            }
        }
        while (table.nodeName != 'TABLE');
    }
    
    else if (handler.nodeName == 'DT') {
        var parent = handler.parentNode;
        var table = parent.getElementsByTagName('TABLE')[0];
    }
    
    var lines = table.getElementsByTagName("TR");
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.className == 'pre' || line.className == 'post') {
            line.style.display = (line.style.display == 'none') ? '' : 'none';
        }
        else if (line.parentNode.parentNode.className == 'vars') {
            line.style.display = (line.style.display == 'none') ? '' : 'none';
        }
    }
}

function initTB() {
    var tb = document.getElementById('wsgi-traceback');
    var handlers = tb.getElementsByTagName('H3');
    for (var i = 0; i < handlers.length; i++) {
        toggleBlock(handlers[i]);
        handlers[i].setAttribute('onclick', 'toggleBlock(this)');
    }
    handlers = tb.getElementsByTagName('DT');
    for (var i = 0; i < handlers.length; i++) {
        toggleBlock(handlers[i]);
        handlers[i].setAttribute('onclick', 'toggleBlock(this)');
    }
}
'''

class PythonParser(object):

    _KEYWORD = token.NT_OFFSET + 1
    _TEXT    = token.NT_OFFSET + 2
    _classes = {
        token.NUMBER:       'num',
        token.OP:           'op',
        token.STRING:       'str',
        tokenize.COMMENT:   'cmt',
        token.NAME:         'id',
        token.ERRORTOKEN:   'error',
        _KEYWORD:           'kw',
        _TEXT:              'txt',
    }

    def __init__(self, raw, out = sys.stdout):
        self.raw = string.strip(string.expandtabs(raw))
        self.out = StringIO()

    def parse(self):
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = string.find(self.raw, '\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))

        self.pos = 0
        text = StringIO(self.raw)
        try:
            tokenize.tokenize(text.readline, self)
        except tokenize.TokenError, ex:
            pass

    def get_html_output(self):
        def html_splitlines(lines):
            # this cool function was taken from trac.
            # http://projects.edgewall.com/trac/
            open_tag_re = re.compile(r'<(\w+)(\s.*)?[^/]?>')
            close_tag_re = re.compile(r'</(\w+)>')
            open_tags = []
            for line in lines:
                for tag in open_tags:
                    line = tag.group(0) + line
                open_tags = []
                for tag in open_tag_re.finditer(line):
                    open_tags.append(tag)
                open_tags.reverse()
                for ctag in close_tag_re.finditer(line):
                    for otag in open_tags:
                        if otag.group(1) == ctag.group(1):
                            open_tags.remove(otag)
                            break
                for tag in open_tags:
                    line += '</%s>' % tag.group(1)
                yield line
                
        return list(html_splitlines(self.out.getvalue().splitlines()))
            

    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        if toktype in [token.NEWLINE, tokenize.NL]:
            self.out.write('\n')
            return

        if newpos > oldpos:
            self.out.write(self.raw[oldpos:newpos])

        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return

        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = self._KEYWORD
        clsname = self._classes.get(toktype, 'txt')

        self.out.write('<span class="code-item p-%s">' % clsname)
        self.out.write(saxutils.escape(toktext))
        self.out.write('</span>')


class DebugRender(object):

    def __init__(self, context):
        for key, value in context.iteritems():
            setattr(self, '_%s' % key, value)
        
    def var_map(self, items):       
        if not items:
            return '<table class="vars"><tr><th>no data given</th></tr></table>'
            
        items.sort()
        result = ['<table class="vars"><tr><th>Name</th><th>Value</th></tr>']
        for key, value in items:
            result.append('<tr><td class="name">%s</td><td class="value">%s</td></tr>' % (
                saxutils.escape(key), saxutils.escape(pprint.pformat(value))))
        result.append('</table>')
        return '\n'.join(result)
        
    def render_code(self, frame):
        def render_line(mode, lineno, code):
            return ''.join([
                '<tr class="%s">' % mode,
                '<td class="lineno">%i</td>' % lineno,
                '<td class="code">%s</td></tr>' % code
            ])

        tmp = ['<table class="code">']    
        lineno = frame['pre_context_lineno'] + 1
        for l in frame['pre_context']:
            tmp.append(render_line('pre', lineno, l))
            lineno += 1
        tmp.append(render_line('cur', lineno, frame['context_line']))
        lineno += 1
        for l in frame['post_context']:
            tmp.append(render_line('post', lineno, l))
            lineno += 1
        tmp.append('</table>')
        
        return '\n'.join(tmp)
        
    def render(self):
        return '\n'.join([
            self.header(),
            self.intro(),
            self.traceback(),
            self.request_informations(),
            self.footer(),
            self.plain()
        ])
        
    def header(self):
        data = [
            '<script type="text/javascript">%s</script>' % JAVASCRIPT,
            '<style type="text/css">%s</style>' % STYLESHEET,
            '<div id="wsgi-traceback">'
        ]
        
        if hasattr(self, '_exception_type'):
            title = saxutils.escape(self._exception_type)
            exc = saxutils.escape(self._exception_value)
            data += [
                '<h1>%s</h1>' % title,
                '<p class="exec">%s</p>' % exc
            ]
        else:
            data += ['<h1>Request Data</h1>']

        return '\n'.join(data)
        
    def intro(self):
        if not hasattr(self, '_last_frame'):
            return ''
            
        return '<p class="info">%s in %s, line %s</p>' % (
            self._last_frame['filename'], self._last_frame['function'],
            self._last_frame['lineno']
        )
        
    def traceback(self):
        if not hasattr(self, '_frames'):
            return ''

        from xml.sax.saxutils import escape
        from pprint import pformat
        
        result = ['<h2>Traceback</h2>']
        result.append('<p class="help">A problem occurred in your Python WSGI'\
        ' application. Here is the sequence of function calls leading up to'\
        ' the error, in the order they occurred.</p>')
        
        for num, frame in enumerate(self._frames):
            line = [
                '<div class="frame" id="frame-%i">' % num,
                '<h3 class="fn">%s in %s</h3>' % (frame['function'], frame['filename']),
                self.render_code(frame),
            ]
                
            if frame['vars']:
                line.append('\n'.join([
                    '<h3>local variables</h3>',
                    self.var_map(frame['vars'])
                ]))
            
            line.append('</div>')
            result.append(''.join(line))
        
        return '\n'.join(result)
        
    def request_informations(self):
        result = [
            '<h2>Request Data</h2>',
            '<p class="help">The following list contains all important',
            'request variables. Click on a header to expand the list.</p>'
        ]

        if not hasattr(self, '_frames'):
            del result[0]
        
        for k, v in self._exposed:
            result.append('<dl><dt>%s</dt><dd>%s</dd></dl>' % (
                saxutils.escape(k), self.var_map(v.items())
            ))
        
        return '\n'.join(result)
        
    def footer(self):
        return '\n'.join([
            '<script type="text/javascript">initTB();</script>',
            '</div>'
        ])
        
    def plain(self):
        if not hasattr(self, '_plaintb'):
            return ''
        return '<!--\n%s-->' % self._plaintb


class DebuggedApplication(object):

    def __init__(self, application):
        if not isinstance(application, basestring):
            self.application = application
        else:
            try:
                self.module, self.handler = application.split(':', 1)
            except ValueError:
                self.module = application
                self.handler = 'app'
        
    def __call__(self, environ, start_response):
        appiter = None
        request = None
        try:
            if hasattr(self, 'application'):
                result = self.application(environ, start_response)
            else:
                module = __import__(self.module, '', '', [''])
                app = getattr(module, self.handler)
                result = app(environ, start_response)
            try:
                request = result.request
            except:
                pass
            appiter = iter(result)
            for line in appiter:
                yield line
        except:
            exc_info = sys.exc_info()
            try:
                headers = [('Content-Type', 'text/html')]
                start_response('500 INTERNAL SERVER ERROR', headers)
            except:
                pass
            yield self.send_debug_output(request, environ, exc_info)
        
        if hasattr(appiter, 'close'):
            appiter.close()

    def send_debug_output(self, request, environ, exc_info):
        context = self.get_debug_information(exc_info)
        if hasattr(request, 'exposed'):
            context['exposed'] = []
            for item in request.exposed:
                context['exposed'].append((item, getattr(request, item)))
        else:
            context['exposed'] = [('environ', environ)]
        return DebugRender(context).render()

    def get_debug_information(self, exc_info):
        exception_type, exception_value, tb = exc_info
        plaintb = ''.join(traceback.format_exception(*exc_info))
        frames = []
        while tb is not None:
            filename = tb.tb_frame.f_code.co_filename
            function = tb.tb_frame.f_code.co_name
            lineno = tb.tb_lineno
            pre_context_lineno, pre_context, context_line, post_context =\
                self.get_lines(filename, lineno - 1)
            variables = tb.tb_frame.f_locals.items()
            variables.sort()
            frames.append({
                'tb':           tb,
                'filename':     filename,
                'function':     function,
                'lineno':       lineno,
                'vars':         variables,
                'id':           id(tb),
                'pre_context':  pre_context,
                'context_line': context_line,
                'post_context': post_context,
                'pre_context_lineno': pre_context_lineno,
            })
            tb = tb.tb_next
        
        return {
            'exception_type':   str(exception_type),
            'exception_value':  str(exception_value),
            'frames':           frames,
            'last_frame':       frames[-1],
            'plaintb':          plaintb
        }

    def get_lines(self, filename, lineno):
        context_lines = 7
        try:
            parser = PythonParser(file(filename).read())
            parser.parse()
            source = parser.get_html_output()
            
            lbound = max(0, lineno - context_lines)
            ubound = lineno + context_lines

            pre_context = [line.strip('\n') for line in source[lbound:lineno]]
            context_line = source[lineno].strip('\n')
            post_context = [line.strip('\n') for line in source[lineno+1:ubound]]

            return lbound, pre_context, context_line, post_context
        except (OSError, IOError):
            return None, [], None, []
