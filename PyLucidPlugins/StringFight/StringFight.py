#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    String Fight

    Simple plugin that allows you to compare the number of search results
    returned by the Google search engine for two given strings. ;)

    TODO: use normal internal pages (django templates)
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

__version__="0.4"

__history__="""
v0.4 - A quick update for PyLucid v0.8 changed API
v0.3
    - Anzeige der gesammt Anzahl an Abfragen
    - TXT_MAX_LEN
v0.2
    - Zeigt die letzten 10 Fights an ;)
v0.1
    - erste Version
"""


import socket, urllib, urllib2, re, time, cgi

from django import newforms as forms

from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.models import Preference

class FightForm(forms.Form):
    txt1 = forms.CharField(min_length=2, max_length=150)
    txt2 = forms.CharField(min_length=2, max_length=150)


# Search form
form = """<h1>String Fight v%(version)s</h2>
<form id="txtfight" method="post" action="%(url)s">
  %(fight_form)s
  <input type="submit">
</form>"""


# Results HTML
result = """<h2>Results:</h2>
<ul>
    <li>%(txt1)s: %(count1)s</li>
    <li>%(txt2)s: %(count2)s</li>
</ul>
<small>(request time: %(duration).2fsec)</small>
"""

# Search engine and result filter regex
engine = {
    "url": "http://www.google.com/search?as_q=%s&num=1&hl=en",
    "re": r"about <b>(.*?)</b>"
}


# A fake User-agent for google (otherwise: HTTP Error 403: Forbidden)
headers = [(
    'User-agent',
    (
        'Mozilla/5.0 '
        '(X11; U; Linux i686; en-US; rv:1.8.1.6) '
        'Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)'
    )
)]



class StringFight(PyLucidBasePlugin):

    def lucidTag(self):
        return self.fight()


    def fight(self):
        """
        main
        """
        if self.request.method == 'POST':
            fight_form = FightForm(self.request.POST)
            if fight_form.is_valid():
                txt1 = fight_form.cleaned_data["txt1"]
                txt2 = fight_form.cleaned_data["txt2"]
                self._do_fight(txt1, txt2)
        else:
            fight_form = FightForm()

        url = self.URLs.methodLink("fight")
        html = form % {
            "url": url,
            "version": __version__,
            "fight_form": fight_form.as_p(),
        }
        self.response.write(html)

#        self._display_last_fights()


    def _do_fight(self, txt1, txt2):

        start_time = time.time()

        try:
            count1, count2 = self._get_count(txt1, txt2)
        except (EngineError, REerror), e:
#            self.log("Error: %s" % e, "StringFight", "error")
            self.page_msg(e)
            return

        duration = time.time() - start_time

        fight_no = self._get_fight_no()

        txt1 = cgi.escape(txt1)
        txt2 = cgi.escape(txt2)

#        log_txt = "No. %s: %s %s vs. %s %s (%.3fsec)" % (
#            fight_no+1, txt1, count1, txt2, count2, duration
#        )
#        self.log(log_txt, "StringFight", "OK")

        result_html = result % {
            "txt1": txt1,
            "txt2": txt2,
            "count1": count1,
            "count2": count2,
            "duration": duration,
        }
        self.response.write(result_html)

    def _get_fight_no(self):
#        default_page = Preference.objects.get(name__exact="index page")
        return 0

#    def _display_last_fights(self):
#        """
#        Letzten Fights anzeigen
#        """
#        result = self.db.select(
#            select_items    = ["message","domain"],
#            from_table      = "log",
#            where           = [("typ","StringFight"),("status","OK")],
#            order           = ("timestamp","DESC"),
#            limit           = (0,10)
#        )
#        self.response.write('<h4>last 10 fights</h4>\n')
#        self.response.write('<ul id="last_search_words">\n')
#        for line in result:
#            message = line["message"]
#            self.response.write("\t<li>%s</li>\n" % message)
#        self.response.write("</ul>\n")

    def _get_count(self, txt1, txt2):
        """
        Fragt für beide Begriffe die Treffer ab
        """
        socket.setdefaulttimeout(5)

        count1 = self._count(txt1)
        count2 = self._count(txt2)

        return count1, count2

    def _count(self, txt):
        """
        Startet eine Anfrage und liefert die Trefferanzahlen zurück
        """
        txt = urllib.quote(txt)
        url = engine["url"] % txt

        opener = urllib2.build_opener()
        opener.addheaders = headers

        try:
            handle = opener.open(url)
            content = handle.read()
            handle.close()
        except Exception, e:
            self.page_msg(url)
            raise EngineError("Request error: %s" % cgi.escape(str(e)))

        regex = engine["re"]
        try:
            count = re.findall(regex, content)[0]
        except KeyError, e:
            raise REerror("Regex '%s' wrong: %s" % (regex, e))
        return count


class EngineError(Exception):
    """
    Fehler beim Abrufen der Ergebnisse vom Server
    """
    pass

class REerror(Exception):
    """
    Die regex liefert keine richtigen Ergebnisse
    """
    pass