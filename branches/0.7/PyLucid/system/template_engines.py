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

    def write(self, internalPageName, context):
        internal_page_data = self.db.get_internal_page_data(internalPageName)

        engine = internal_page_data["template_engine"]
        if engine == "string formatting":
            self.render_stringFormatting(internalPageName, internal_page_data, context)
        elif engine == "jinja":
            content = internal_page_data["content"]
            content = render_jinja(content, context)
            self.response.write(content)
        else:
            msg = "Template Engine '%s' not implemented!" % engine
            raise NotImplemented, msg

        addCode = self.db.get_internal_page_addition_Data(internalPageName)
        self.response.addCode += addCode


    def render_stringFormatting(self, internalPageName, internal_page_data, context):
        content = internal_page_data["content"]

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
                    sys.exc_info()[0], e, internalPageName,
                )
            )

        content = self.render.apply_markup(content, internal_page_data["markup"])

        self.response.write(content)




