#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Der Parser füllt eine CMS Seite mit leben ;)
Parsed die lucid-Tags/Funktionen, führt diese aus und fügt das Ergebnis in die Seite ein.
"""

__version__="0.1.4"

__history__="""
v0.1.4
    - apply_markup kommt mit markup id oder richtigen namen klar
v0.1.3
    - textile Parser erhält nun auch die PyLucid-Objekt. page_msg ist hilfreich zum debuggen des Parsers ;)
v0.1.2
    - Bug 1297263: "Can't use textile-Markup (maximum recursion limit exceeded)":
        Nun wird zuerst das Markup angewendet und dann erst die lucidTag's aufgelöst
v0.1.1
    - parser.handle_function(): toleranter wenn kein String vom Modul zurück kommt
    - Versionsnummer geändert
v0.1.0
    - Erste Version: Komplett neugeschrieben. Nachfolge vom pagerender.py
"""

__todo__ = """
in apply_markup sollte nur noch mit markup IDs erwartet werden. Solange aber die Seiten keine IDs,
sondern die richtigen Namen verwenden geht das leider noch nicht :(
"""

import sys, cgi, re, time


#~ lucidTagRE      = re.compile("<lucidTag:(.*?)/?>")
#~ lucidFunctionRE = re.compile("<lucidFunction:(.*?)>(.*?)</lucidFunction>")


#~ class tag_parser(object):
    #~ """
    #~ Alle Tags in der Seite ersetzten...
    #~ """
    #~ def __init__(self, request, response):
        #~ self.request = request
        #~ self.response = response

        #~ # Shorthands
        #~ self.page_msg       = request.page_msg
        #~ self.module_manager = request.module_manager
        #~ self.staticTags     = request.staticTags

        #~ self.tag_data = {} # "Statische" Tags-Daten
        #~ self.ignore_tag = ("page_msg", "script_duration")

    #~ def rewrite_responseObject(self):
        #~ # Tags ersetzten:
        #~ self.response.response = [self.rewrite(line) for line in self.response.response]

    #~ def rewrite_String(self, content):
        #~ content = content.split("\n")
        #~ content = [self.rewrite(line) for line in content]
        #~ content = "\n".join(content)
        #~ return content

    #~ def rewrite(self, line):
        #~ if "<lucid" in line:
            #~ line = lucidTagRE.sub(self.handle_tag, line)
            #~ line = lucidFunctionRE.sub(self.handle_function, line)

        #~ line = line.replace(self.pageMsgTag, page_msg.get())
        #~ return line

    #~ def handle_tag(self, matchobj):
        #~ """
        #~ Abarbeiten eines <lucidTag:... />
        #~ """
        #~ tag = matchobj.group(1)

        #~ self.page_msg("tag: %s" % tag)

        #~ if tag in self.ignore_tag:
            #~ # Soll ignoriert werden. Bsp.: script_duration, welches wirklich am ende
            #~ # erst "ausgefüllt" wird ;)
            #~ return matchobj.group(0)

        #~ if self.staticTags.has_key(tag):
            #~ # Als "Statische" Information vorhanden
            #~ return self.check_result(tag, self.staticTags[tag])

        #~ content = self.module_manager.run_tag(tag)
        #~ return ""

        #~ return self.check_result(tag, content)

    #~ def run_tag(self, tag):
        #~ self.module_manager.run_tag(tag)


    #~ def handle_function(self, matchobj):
        #~ function_name = matchobj.group(1)
        #~ function_info = matchobj.group(2)

        #~ print function_name, function_info

        #~ content = self.module_manager.run_function(function_name, function_info)
        #~ return ""

        #~ return self.check_result(
            #~ "%s.%s" % (function_name, function_info),
            #~ content
        #~ )


    #~ def check_result(self, tag, content):
        #~ # FIXME - besserer Umgang mit unicode content!

        #~ if not isinstance(content, basestring):
        #~ if type(content) == unicode:
            #~ return str(content)

        #~ if type(content) != str:
            #~ self.page_msg(
                #~ "result of tag '%s' is not type string! Is type: %s" % (
                    #~ tag, cgi.escape(str(type(content))),
                #~ )
            #~ )
            #~ self.page_msg("---- result is: ----")
            #~ self.page_msg(cgi.escape(str(content)))
            #~ self.page_msg("--------------------")
            #~ return str(content)

        #~ return content








class render:
    """
    Parsed die Seite und wendes das Markup an.
    """
    def __init__(self, request, response):
        self.request        = request
        self.response       = response

        # shorthands
        self.page_msg       = request.page_msg
        self.db             = request.db
        self.session        = request.session
        self.preferences    = request.preferences
        self.environ        = request.environ
        self.URLs           = request.URLs
        self.tools          = request.tools
        self.staticTags     = request.staticTags

    def write_page_template(self):
        """ Baut die Seite zusammen """

        page_id = self.session["page_id"]
        page_data = self.db.get_side_data(page_id)
        self.staticTags.fill_with_page_data(page_data)

        template_data = self.db.side_template_by_id(self.session["page_id"])
        self.response.write(template_data)

    def write_command_template(self):
        # FIXME - Quick v0.7 Patch !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        template_data = self.db.side_template_by_id(self.session["page_id"])
        self.response.write(template_data)

    def get_rendered_page(self, page_id):
        page = self.db.get_content_and_markup(page_id)
        #~ self.page_msg(page)
        content = self.apply_markup(
            content = page["content"],
            markup = page["markup"]
        )
        return content

    def apply_markup(self, content, markup):
        """
        Wendet das Markup auf den Seiteninhalt an
        """
        #~ self.page_msg("markup: '%s' content: '%s'" % (markup, content))

        # Die Markup-ID Auflösen zum richtigen Namen
        markup = self.db.get_markup_name( markup )

        if markup == "textile":
            # textile Markup anwenden
            if self.preferences["ModuleManager_error_handling"] == True:
                try:
                    from PyLucid_system import tinyTextile
                    out = self.tools.out_buffer()
                    tinyTextile.parser( out, self.PyLucid ).parse( content )
                    return out.get()
                except Exception, e:
                    msg = "Can't use textile-Markup (%s)" % e
                    self.page_msg(msg)
                    return msg
            else:
                from PyLucid.system import tinyTextile
                out = self.tools.out_buffer()
                tinyTextile.parser(out, self.request).parse(content)
                return out.get()
        elif markup in ("none", "None", None, "string formatting"):
            return content
        else:
            self.page_msg("Markup '%s' not supported yet :(" % markup)
            return content

