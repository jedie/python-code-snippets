#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Einheitliche Schnittstelle zu den Templates Engines
"""

__version__="0.1"

__history__="""
v0.1
    - erste Version
"""

import sys


from PyLucid.system.exceptions import *
from PyLucid.system.BaseModule import PyLucidBaseModule


def render_jinja(template, context):
    """
    Ist als normale Funktion ausgelagert, damit sie auch während der _install
    Phase benutzt werden kann...
    """
    import jinja

    # FIXME: jinja.loader.load() wandelt immer selber in unicode um und
    # mag deswegen kein unicode, also wandeln wir es in einen normale
    # String :(
    template = str(template)

    t = jinja.Template(template, jinja.StringLoader())#, trim=True)
    c = jinja.Context(context)
    content = t.render(c)

    return content



class TemplateEngines(PyLucidBaseModule):

    def write(self, internal_page_name, context):
        try:
            internal_page_data = self.db.get_internal_page_data(
                internal_page_name
            )
        except IndexError, e:
            import inspect
            stack = inspect.stack()[1]
            raise KeyError(
                "Internal page '%s' not found (from '...%s' line %s): %s" % (
                    internal_page_name, stack[1][-30:], stack[2], e
                )
            )

        engine = internal_page_data["template_engine"]
        if engine == "string formatting":
            self.render_stringFormatting(
                internal_page_name, internal_page_data, context
            )
        elif engine == "jinja":
            content = internal_page_data["content_html"]
            content = render_jinja(content, context)
            self.response.write(content)
        else:
            msg = "Template Engine '%s' not implemented!" % engine
            raise NotImplemented, msg

        # CSS/JS behandeln:
        self.addCSS(internal_page_data["content_css"])
        self.addJS(internal_page_data["content_js"])

    def addCSS(self, content_css):
        """
        Zusätzlicher Stylesheet Code für interne Seite behandeln
        """
        if content_css=="":
            return

        #~ tag = '<style type="text/css">\n%s\n</style>\n'
        tag = (
            '<style type="text/css">\n/* <![CDATA[ */\n'
            '%s\n'
            '/* ]]> */\n</style>'
        )
        content_type = "Stylesheet"
        self.addCode(content_css, tag, content_type, internal_page_name)

    def addJS(self, content_js):
        """
        Zusätzlicher JavaScript Code für interne Seite behandeln
        """
        if content_js=="":
            return

        #~ tag = '<script type="text/javascript">\n%s\n</script>\n'
        tag = (
            '<script type="text/javascript">\n/* <![CDATA[ */\n'
            '%s\n'
            '/* ]]> */\n</script>'
        )
        content_type = "JavaScript"
        self.addCode(content_js, tag, content_type, internal_page_name)

    def addCode(self, code, tag, content_type, internal_page_name):
        """
        Fügt den Code an response.addCode an
        """
        try:
            code = code.encode("utf8")
        except UnicodeError, e:
            msg = (
                "UnicodeError in %s add data for internal page '%s'"
                " (Error: %s)"
            ) % (content_type, internal_page_name, e)
            self.page_msg(msg)
            code = code.encode("utf8", "replace")

        # Tag anwenden
        code = tag % code
        self.response.addCode.add(code)


    def render_stringFormatting(self, internal_page_name, internal_page_data, context):
        content = internal_page_data["content_html"]

        content = content % context

        try:
            a=1#content = content % context
        except UnicodeError, e:
            self.page_msg("UnicodeError: Can't render internal page: %s" % e)
            self.page_msg("(Try to go around.)")
            try:
                for k,v in context.iteritems():
                    try:
                        context[k] = v.encode("utf_8", 'replace')
                    except Exception: # z.B. bei Zahlen
                        pass

                content = content.encode("utf_8", 'replace')
                content = content % context
                self.response.write(content)
            except:
                self.response.write(
                    "<h4>Can't go around the UnicodeError!</h4>"
                )
                if self.preferences["ModuleManager_error_handling"] != True:
                    raise
        except Exception, e:
            self.page_msg("Error information:")

            s = self.tools.Find_StringOperators(content)
            if s.incorrect_hit_pos != []:
                self.page_msg(" -"*40)
                self.page_msg("There are incorrect %-chars in the internal_page:")
                self.page_msg("Text summary:")
                for line in s.get_incorrect_text_summeries():
                    self.page_msg(line)
                self.page_msg(" -"*40)

            l = s.correct_tags
            # doppelte Einträge löschen (auch mit Python >2.3)
            content_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            content_placeholder.sort()
            self.page_msg("*** %s content placeholder:" % len(content_placeholder))
            self.page_msg(content_placeholder)

            l = context.keys()
            given_placeholder = [l[i] for i in xrange(len(l)) if l[i] not in l[:i]]
            given_placeholder.sort()
            self.page_msg("*** %s given placeholder:" % len(given_placeholder))
            self.page_msg(given_placeholder)

            diff_placeholders = []
            for i in content_placeholder:
                if (not i in given_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)
            for i in given_placeholder:
                if (not i in content_placeholder) and (not i in diff_placeholders):
                    diff_placeholders.append(i)

            diff_placeholders.sort()
            self.page_msg("*** placeholder diffs:", diff_placeholders)

            raise Exception(
                "%s: '%s': Can't fill internal page '%s'. \
                *** More information above in page message ***" % (
                    sys.exc_info()[0], e, internal_page_name,
                )
            )

        content = self.render.apply_markup(content, internal_page_data["markup"])

        self.response.write(content)




