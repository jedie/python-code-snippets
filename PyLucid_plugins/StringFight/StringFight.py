#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
String Fight

DE
Zeigt die Anzahl der Treffer von zwei Begriffen bei google an ;)

EN
Simple plugin that allows you to compare the number of search results
returned by the Google search engine for two given strings. ;)
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"

__version__="0.3"

__history__="""
v0.3
    - Anzeige der gesammt Anzahl an Abfragen
    - txt_max_len
v0.2
    - Zeigt die letzten 10 Fights an ;)
v0.1
    - erste Version
"""


import socket, urllib, urllib2, re, time, cgi


from PyLucid.system.BaseModule import PyLucidBaseModule



# Such Formular
form = """<h1>String Fight v%(version)s</h2>
<form id="txtfight" method="post" action="%(url)s">
  <p>
    <input name="txt1" type="text" value="" size="20" maxlength="50" />
    <input name="txt2" type="text" value="" size="20" maxlength="50" />
    <input type="submit" name="search" value="fight!" />
  </p>
</form>"""


# Ergebniss HTML
result = """<h2>Results:</h2>
<ul>
    <li>%(txt1)s: %(count1)s</li>
    <li>%(txt2)s: %(count2)s</li>
</ul>
<small>(request time: %(duration).2fsec)</small>
"""


# Min./Max. länge der Strings
txt_min_len = 2
txt_max_len = 20


# Suchmaschine + regex zum filtern
engine = {
    "url": "http://www.google.com/search?as_q=%s&num=1&hl=en",
    "re": r"about <b>(.*?)</b>"
}


# Zusätzliche Header für google, ansonsten: HTTP Error 403: Forbidden
headers = [(
    'User-agent',
    (
        'Mozilla/5.0 '
        '(Windows; U; Windows NT 5.1; de; rv:1.8.1) '
        'Gecko/20061010 Firefox/2.0'
    )
)]



class StringFight(PyLucidBaseModule):

    def lucidTag(self):
        """
        Zeigt das Formular zum eintragen der Suchbegriffe
        """
        url = self.URLs.actionLink("fight")
        html = form % {
            "url": url,
            "version": __version__
        }
        self.response.write(html)

        self.display_last_fights()

    def fight(self):
        """
        Zeigt die Ergebnisse an
        """
        try:
            txt1 = self.request.form["txt1"]
            txt2 = self.request.form["txt2"]
        except KeyError:
            self.page_msg("Form error!")
            self.lucidTag() # Formular wieder anzeigen lassen
            return

        if len(txt1)<txt_min_len or len(txt2)<txt_min_len:
            self.page_msg("Given Strings are to short!")
            self.lucidTag() # Formular wieder anzeigen lassen
            return

        if len(txt1)>txt_max_len or len(txt2)>txt_max_len:
            self.page_msg("Given Strings are to long!")
            self.lucidTag() # Formular wieder anzeigen lassen
            return

        start_time = time.time()

        try:
            count1, count2 = self.get_count(txt1, txt2)
        except (EngineError, REerror), e:
            self.log("Error: %s" % e, "StringFight", "error")
            self.page_msg(e)
            self.lucidTag() # Formular wieder anzeigen lassen
            return

        duration = time.time() - start_time

        fight_no = self.get_fight_no()

        txt1 = cgi.escape(txt1)
        txt2 = cgi.escape(txt2)

        log_txt = "No. %s: %s %s vs. %s %s (%.3fsec)" % (
            fight_no+1, txt1, count1, txt2, count2, duration
        )
        self.log(log_txt, "StringFight", "OK")

        result_html = result % {
            "txt1": txt1,
            "txt2": txt2,
            "count1": count1,
            "count2": count2,
            "duration": duration,
        }
        self.response.write(result_html)
        self.lucidTag() # Formular wieder anzeigen lassen

    def get_fight_no(self):
        result = self.db.select(
            select_items    = ["message"],
            from_table      = "log",
            where           = [("typ","StringFight"),("status","OK")],
            order           = ("timestamp","DESC"),
            limit           = (0,1)
        )
        try:
            last_fight = result[0]['message']
            no = int(re.findall("(\d*?):", last_fight)[0])
        except:
            return 0
        else:
            return no

    def display_last_fights(self):
        """
        Letzten Fights anzeigen
        """
        result = self.db.select(
            select_items    = ["message","domain"],
            from_table      = "log",
            where           = [("typ","StringFight"),("status","OK")],
            order           = ("timestamp","DESC"),
            limit           = (0,10)
        )
        self.response.write('<h4>last 10 fights</h4>\n')
        self.response.write('<ul id="last_search_words">\n')
        for line in result:
            message = line["message"]
            self.response.write("\t<li>%s</li>\n" % message)
        self.response.write("</ul>\n")

    def get_count(self, txt1, txt2):
        """
        Fragt für beide Begriffe die Treffer ab
        """
        try:
            socket.setdefaulttimeout(5)
        except AttributeError:
            # erst ab Python 2.3 verfügbar :(
            pass

        count1 = self.count(txt1)
        count2 = self.count(txt2)

        return count1, count2

    def count(self, txt):
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