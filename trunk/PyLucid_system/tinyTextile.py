#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Eine kleine Version vom textile Parser
(stehen unter der GPL-License)
by jensdiemer.de

http://pylucid.org/index.py?p=/Doku/details/Markup

Links
-----
http://dealmeida.net/en/Projects/PyTextile/
http://www.solarorange.com/projects/textile/mtmanual_textile2.html
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.2.3"

__history__="""
v0.2.3
    - Bug 1328496: Fehler im inline-Python-Highlighter. Nun wird Python-Source als kompletter
        Block durch den Highlighter gejagt.
v0.2.2
    - *Fettschrift* nun auch bei *Teilen mit Leerzeichen* erlaubt, aber nicht über mehrere Zeilen
    - Durch bessere Erkennung des Ende einer URL sind kombination möglich mit <small> möglich
        Bsp.: --"text":http://wow.de-- oder --http://www.heise.de--
v0.2.1
    - Codeerzeugung bei Listen etwas verbessert (newline eingefügt)
v0.2.0
    - NEU: area_rules, die jetzt das direkte einbinden von Python-Code mit PyLucid_system.sourcecode_parser
        ermöglichen
    - Verbesserung bei dem <small>-Tag erkennung.
    - Detailverbesserungen einiger Regeln
v0.1.7
    - Bug Erkennung ob der Block schon HTML ist, war nicht ganz richtig. Hab es nun vereinfacht
v0.1.6
    - neu: auch nummerierte Listen: <ol>...</ol>
v0.1.5
    - neu: interner PyLucid Link mit [[SeitenName]]
    - neu: small Text: --klein-- -> <small>klein</small>
v0.1.4
    - neu: img-Tag wird durch !/MeinBild.jpg! erzeugt
    - dank Joe, neue RE Regeln für das trennen einer Liste vom Text
v0.1.3
    - Im Pre-Process wird eine Liste direkt nach einem Text getrennt
v0.1.2
    - Fehler in generierung von Listen behoben
v0.1.1
    - Links werden nun richtig umgesetz: Dank an BlackJack
v0.1.0
    - erste Version
"""

__todo__ = """
    ToDo
    ----
mit [sc Datei] PyLucid/system/SourceCode.py benutzen
"""

import sys, re, cgi

SourceCodeParser = "/cgi-bin/PyLucid/system/SourceCode.py"



class parser:
    def __init__(self, out_obj, PyLucid, newline="\n"):
        self.out        = out_obj
        self.PyLucid    = PyLucid
        self.page_msg   = PyLucid["page_msg"]
        self.tools      = PyLucid["tools"]
        self.newline    = newline

        # Regeln für Blockelemente
        self.block_rules = self._compile_rules([
            [ # <h1>-Überschriften
                r"\Ah(\d)\. +(.*)(?us)",
                r"<h\1>\2</h\1>"
            ],
        ])

        # Regeln für Inlineelemente
        self.inline_rules = self._compile_rules([
            [ # Kleiner Text - Bsp.: Ich bin ein --kleines-- Wort.
                r"-{2,2}([^-]+?)-{2,2}",
                r"<small>\1</small>"
            ],
            [ # Fettschrift - Bsp.: Das Wort ist in *fett* geschrieben.
                r"\*([^*\n]+?)\*(?uism)",
                r"<strong>\1</strong>"
            ],
            [ # img-Tag - Bsp.: !/Bilder/MeinBild.jpg!
                r'\!([^!\n]+?)\!(?uis)',
                r'<img src="\1">'
            ],
            [ # Link + LinkText - Bsp.: "LinkText":http://www.beispiel.de
                r'"([^"]+?)":([^\s\<]+)',
                r'<a href="\2">\1</a>'
            ],
            [ # interne PyLucid Links - Bsp.: Das ist ein [[InternerLink]] zur Seite InternerLink ;)
                r'\[\[(.+?)\]\]',
                r'<a href="?\1">\1</a>'
            ],
            [ # Link alleine im Text - Bsp.: Das wird ein Link: http://www.beispiel.de weil es eine URL ist
                r'''
                    (?<!=") # Ist noch kein HTML-Link
                    (?P<url>(http|ftp)://([^\s\<]+))
                    (?uimx)
                ''',
                r'<a href="\g<url>">\g<url></a>'
            ],
            [ # EMails
                r'mailto:([^\s\<]+)',
                r'<a href="mailto:\1">\1</a>'
            ],
        ])

        # Pre-Process Regeln
        self.pre_process_rules = self._compile_rules([
            [ # NewLines von Windows "\r\n", MacOS "\r" nach "\n" vereinheitlichen
                r"\r\n{0,1}",
                r"\n"
            ],
            [ # HTML-Escaping
                r"={2,2}(.+?)={2,2}(?usm)",
                self.escaping
            ],
            [ # Text vor einer Liste mit noch einem \n trennen
                r"""
                    (^[^*\n].+?$) # Text-Zeile vor einer Liste
                    (\n^\*) # Absatz + erstes List-Zeichen
                    (?uimx)
                """,
                r"\1\n\2",
            ],
        ])

        self.area_rules = (
            ["<pre>", "</pre>",         self.pre_area,          self.pre_area,      self.pre_area],
            ["<python>", "</python>",   self.python_area_start, self.python_area,   self.python_area_end],
        )

    def _compile_rules(self, rules):
        "Kompliliert die RE-Ausdrücke"
        for rule in rules:
            rule[0] = re.compile(rule[0])
        return rules

    def parse(self, txt):
        "Parsed den Text in's out_obj"

        #~ import cgi
        #~ self.page_msg(cgi.escape(txt))

        txt = self.pre_process(txt)
        self.make_paragraphs(txt)

    def escaping(self, matchobj):
        return cgi.escape(matchobj.group(1))

    def pre_process(self, txt):
        "Vorab Verarbeitung des Textes"
        # Leerzeilen vorn und hinten abschneiden
        txt = txt.strip()

        # Preprocess rules anwenden
        for rule in self.pre_process_rules:
            txt = rule[0].sub(rule[1], txt)
        return txt

    def make_paragraphs(self, txt):
        """
        Verarbeitung des Textes.
        Wendet Blockelement-Regeln und Inlineelement-Regeln an.
        """
        blocks = re.split("\n{2,}", txt)
        #~ self.page_msg(cgi.escape(str(blocks)))
        text = ""
        current_area = None
        for block in blocks:
            block = block.strip()
            if len(block) == 0:
                continue

            current_area = self.handle_areas(block, current_area)
            if current_area != None:
                # Wir sind in einer Area und der Block wurde schon abgehandelt
                continue

            #~ if self.is_html.findall(block) != []:
            if block[0] == "<":
                # Der Block scheint schon HTML-Code zu sein
                self.out.write(block + self.newline)
                #~ self.page_msg("Is HTML:", cgi.escape(block))
                continue

            # inline-rules Anwenden
            for inlinerule in self.inline_rules:
                #~ print ">>>",block,"<<<"
                block = inlinerule[0].sub(inlinerule[1], block)

            # Block-rules Anwenden
            self.blockelements(block)

    #___________________________________________________________________________
    # Areas

    def handle_areas(self, block, current_area):
        """
        Areas anhandeln
        """
        def handle_end(current_area, block):
            if block.endswith(current_area[1]):
                # Die aktuelle Area ist zuende
                inner_block = block[:-len(current_area[1])].rstrip()
                # Erstmal die restlichen Daten verabeiten
                current_area[3](inner_block)

                current_area[4](current_area[1]) # Endmethode aufrufen
                return False

        if (current_area != None) and (current_area != False):
            # Wir sind gerade in einer area

            if handle_end(current_area, block) == False:
                # Ende erreicht
                return False

            # Methode die für die area zuständig ist aufrufen
            current_area[3]("\n"+block+"\n")

            # In der area bleiben
            return current_area

        for current_area in self.area_rules:
            if block.startswith(current_area[0]): # Start einer neuen area
                area_tag = current_area[0]

                # Area-Start-Methode aufrufen
                current_area[2](area_tag)

                rest_block = block[len(area_tag):]
                try:
                    if rest_block[0]=="\n": # Evtl. vorhandene Leerzeile ignorieren
                        rest_block = rest_block[1:]
                except IndexError:
                    # Es ist ein Leerzeichen zwischem Tag und Inhalt (kommt selten vor)
                    pass

                if handle_end(current_area, rest_block) == False:
                    # Das Ende schon erreicht
                    return False

                # Das Ende ist noch nicht erreicht, also
                # den Restlichen Block durch die normale Methode jagen
                current_area[3](rest_block)

                # In-der-Area-Methode "merken"
                return current_area

        # Wir sind nicht in einer Area
        return None

    def pre_area(self, block):
        """
        Daten innerhalb von <pre>...</pre> werden direkt "ausgegeben"
        """
        self.out.write(block + self.newline)

    #___________________________________________________________________________

    def python_area_start(self, block):
        """
        Python-Source-Code area
        """
        self.python_source_data = ""

    def python_area(self, block):
        self.python_source_data += block

    def python_area_end(self, dummy):
        from PyLucid_system import sourcecode_parser

        p = sourcecode_parser.python_source_parser(self.PyLucid)
        self.out.write(p.get_CSS())
        self.out.write('<div class="SourceCode">')

        self.redirector = self.tools.redirector()
        p.parse(self.python_source_data)
        self.out.write(self.redirector.get())

        self.out.write("</div>")

    #___________________________________________________________________________

    def blockelements(self, block):
        "Anwenden der Block-rules. Formatieren des Absatzes"

        #~ self.page_msg(block[0], block)

        if block[0] in ("*","#"):
            # Aktueller Block ist eine Liste
            self.build_list(block)
            return

        for rule in self.block_rules:
            txt,count = rule[0].subn(rule[1], block)

            if count != 0:
                # Ein Blockelement wurde gefunden
                self.out.write(txt + self.newline)
                return

        # Kein Blockelement gefunden -> Formatierung des Absatzes
        block = block.strip().replace("\n", "<br />" + self.newline)
        self.out.write("<p>%s</p>" % block + self.newline)

    def build_list(self, listitems):
        "Erzeugt eine Liste aus einem Absatz"

        def spacer(deep): return " "* (deep * 3)

        def write(number, Tag, spacer):
            for i in range(number):
                self.out.write(spacer + Tag)

        deep = 0
        for item in re.findall("([\*#]+) (.*)", listitems):
            currentlen = len(item[0])
            if item[0][0] == "*":
                # normale Aufzählungsliste
                pre_tag  = "<ul>" + self.newline
                post_tag = "</ul>" + self.newline
            else:
                # Nummerierte Liste
                pre_tag  = "<ol>" + self.newline
                post_tag = "</ol>" + self.newline

            if currentlen > deep:
                write(currentlen - deep, pre_tag, spacer(deep))
                deep = currentlen
            elif currentlen < deep:
                write(deep - currentlen, post_tag, spacer(deep))
                deep = currentlen

            self.out.write("%s<li>%s</li>%s" % (spacer(deep), item[1], self.newline))

        for i in range(deep):
            self.out.write(post_tag)


