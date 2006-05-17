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

class TemplateEngines(PyLucidBaseModule):

    def write(self, internalPageName, context):
        internal_page_data = self.db.get_internal_page_data(internalPageName)

        engine = internal_page_data["template_engine"]
        if engine == "string formatting":
            self.render_stringFormatting(internalPageName, internal_page_data, context)
        elif engine == "jinja":
            self.render_jinja(internalPageName, internal_page_data, context)
        else:
            raise NotImplemented, "Template Engine \
                        '%s' not implemented!" % engine


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

    def render_jinja(self, internalPageName, internal_page_data, context):

        self.page_msg("jinja context: %s" % context)

        import jinja

        template = internal_page_data["content"]
        #~ if type(template) == unicode:
            #~ template = str(template)

        t = jinja.Template(template, jinja.StringLoader())#, trim=True)
        c = jinja.Context(context)
        content = t.render(c)

        self.response.write(content)



class OBSOLETE:
    def get_rendered_internal_page(self, internal_page_name, context={}):
        """
        Interne Seite aufgeüllt mit Daten ausgeben. Diese Methode sollte immer
        verwendet werden, weil sie eine gescheite Fehlermeldung anzeigt.

        Wird für template-engine = "None" und = "string formatting" verwendet.
        """

        try:
            internal_page_data = self.get_internal_page_data(internal_page_name)
        except Exception, e:
            import inspect
            self.page_msg(
                "[Can't print internal page '%s' (from '...%s' line %s): %s]" % (
                    internal_page_name, inspect.stack()[1][1][-20:], inspect.stack()[1][2], e
                )
            )
            if not self.config.system.ModuleManager_error_handling: raise
            return

        #~ raise str(internal_page_data)

        if internal_page_data["template_engine"] != "string formatting":
            msg = (
                "Internal page '%s' is not marked as a '%s' page! "
                "(Marked as:'%s')"
            ) % (
                internal_page_name, internal_page_data["template_engine"],
                internal_page_data["template_engine"]
            )
            raise WrongTemplateEngine, msg



    def print_internal_TAL_page(self, internal_page_name, context_dict):

        internal_page_data = self.get_internal_page_data(internal_page_name)
        internal_page_content = internal_page_data["content"]
        if internal_page_data["template_engine"] != "TAL":
            self.page_msg(
                "Warning: Internal page '%s' is not marked as a TAL page! "
                "(Marked as:'%s')" % (
                    internal_page_name, internal_page_data["template_engine"]
                )
            )

        if internal_page_data["markup"] != None:
            self.page_msg(
                "Warning: A TAL page should never have markup! "
                "(internal page name: '%s', Markup:'%s')" % (
                    internal_page_name, internal_page_data["markup"]
                )
            )

        from PyLucid_simpleTAL import simpleTAL, simpleTALES

        context = simpleTALES.Context(allowPythonPath=1)
        context.globals.update(context_dict) # context.addGlobal()

        template = simpleTAL.compileHTMLTemplate(internal_page_content, inputEncoding="UTF-8")
        template.expand(context, self.request, outputEncoding="UTF-8")