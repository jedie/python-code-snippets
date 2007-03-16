table = 'pylucid_page'
fields = ['id', 'content', 'parent', 'position', 'name', 'shortcut', 'title', 'template', 'style', 'markup', 'keywords', 'description', 'createtime', 'lastupdatetime', 'lastupdateby', 'showlinks', 'permitViewPublic', 'permitViewGroupID', 'ownerID', 'permitEditGroupID']
records = [
[1, "h2. Welcome to the first django powered PyLucid Version!\n\nYou can see, it's pre-alpha state ;)\n\nh3. list of last page updates\n\n<lucidTag:page_update_list/>", 0, 0, 'index', 'Index', 'index', 1, 1, '2', '', '', '2007-01-09 14:17:25', '2007-01-09 14:17:25', 14, 1, 1, 9, 9, 9]
[2, 'h2. sub menu\n\n<lucidTag:sub_menu/>', 0, 0, 'example pages', 'ExamplePages', 'example pages', 1, 1, '2', '', '', None, '2006-06-16 15:58:01', 2, 1, 1, 1, 1, 1]
[3, 'h1. \xc3\x83\xc5\x93berschriften\n\n\xc3\x83\xc5\x93berschriften werden mit h1. eingeleitet:\n\n<pre>\nh1. h-1 \xc3\x83\xc5\x93berschrift\n\nh2. h-2 \xc3\x83\xc5\x93berschrift\n</pre>\n\nErgibt:\n\nh1. h-1 \xc3\x83\xc5\x93berschrift\n\nh2. h-2 \xc3\x83\xc5\x93berschrift\n\n(Wichtig ist hierbei, das eine Leerzeile unter der \xc3\x83\xc5\x93berschriftzeile bleibt!)\n\n<hr class="big_hr">\n\nh1. Textformatierung\n\n<pre>\nIch bin ein --kleines-- Wort mit ==<small>==-Tag\nDas wird ein *fettes* Wort mit ==<strong>==-Tag\n</pre>\n\nErgibt:\n\nIch bin ein --kleines-- Wort mit ==<small>==-Tag\nDas wird ein *fettes* Wort mit ==<strong>==-Tag\n\n<hr class="big_hr">\n\nh1. Links\n\nLinks werden nach folgendem Schema notiert:\n\n<pre>\n"LinkText":URL\n\nBeispiele:\n----------\nhttp://keinserver.dtl\nftp://keinserver.dtl\nmailto:name@beispiel.dtl\nhttp://www.python-forum.de\noder besser: "Das deutsche Python-Forum":http://www.python-forum.de\nDas wird auch ein "Link":?#unten\nEin interner PyLucid Link zur Seite [[BeispielSeitenName]]!\nTo make no link use instand of ":" the ==&#x3A;==\n</pre>\nTo make no link you can put the Link into a pre Area:\n<pre>==<pre>==No link with a pre area: http://domain.tld==</pre>==</pre>\n\nAlso you can use a unicode escape sequenz, so thar tinytextile can\'t find a link. example http*==&#x3A;==*//domain.tld\n\nErgibt:\nhttp://keinserver.dtl\nftp://keinserver.dtl\nmailto:name@beispiel.dtl\nhttp://www.python-forum.de\noder besser: "Das deutsche Python-Forum":http://www.python-forum.de\nDas wird auch ein "Link":?#unten\nEin interner PyLucid Link zur Seite [[BeispielSeitenName]]!\n<pre>No link with a pre area: http://domain.tld</pre>\nexample: http&#x3A;//domain.tld\n\n<hr class="big_hr">\n\nh1. Listen\n\nNormale Listen werden mit einem "*" und nummerierte Liste mit einem "#"\neingeleitet. Diese k\xc3\x83\xc2\xb6nnen verschachtelt werden. Allerdings sollte man\nkeine normale und nummerierte Listen zusammen mischen.\n\n<pre>\n* 1. Eintrag in der erste Ebene\n** 1. Unterprunkt in der zweiten Ebene\n**** 1. Subunterpunkt in der vierter Ebene\n**** 2. Subunterpunkt in der vierter Ebene\n** 2. Unterprunkt in der zweiten Ebene\n\nNummerierte Liste:\n\n# Nummer eins\n# Nummer zweite\n## und so...\n## ...weiter...\n</pre>\n\nErgibt:\n\n* 1. Eintrag in der erste Ebene\n** 1. Unterprunkt in der zweiten Ebene\n**** 1. Subunterpunkt in der vierter Ebene\n**** 2. Subunterpunkt in der vierter Ebene\n** 2. Unterprunkt in der zweiten Ebene\n\nNummerierte Liste:\n\n# Nummer eins\n# Nummer zweite\n## und so...\n## ...weiter...\n\n<hr class="big_hr">\n\nh1. Bilder\n\nEin HTML-img-Tag wird erzeugt, wenn eine Adresse mit einem "!"-Zeichen\numschlossen ist.\n\n<pre>\n!http://images.sourceforge.net/images/project-support.jpg!\n!/favicon.ico!\n!http://domain.tld/pics/ich werde zu keiner URL weil hier leerzeichen sind.jpg!\n</pre>\n\nErgibt:\n\n!http://images.sourceforge.net/images/project-support.jpg!\n!/favicon.ico!\n!http://domain.tld/pics/ich werde zu keiner URL weil hier leerzeichen sind.jpg!\n\n<hr class="big_hr">\n\nh1. Python SourceCode\n\nEinblenden von Python Sourcecode.\nInteressant in dem Zusammenhang ist ==<lucidFunction:SourceCode>== ;)\n\nBeispiel:\n---------\n==\n<python>\n#!/usr/bin/python\n# -*- coding: UTF-8 -*-\n\n"""Ein kleines Skript"""\n\nprint "Hello Word: I love Python!"\n</python>\n==\n\nErgibt:\n\n<python>\n#!/usr/bin/python\n# -*- coding: UTF-8 -*-\n\n"""Ein kleines Skript"""\n\nprint "Hello Word: I love Python!"\n</python>\n\n<hr class="big_hr">\n\nh1. Escaping\n\nIn zwei "="-Zeichen eingeschlossener Text wird escaped.\n\nBeispiel:\n---------\n========\nTable: <table width="90%" border="0" align="center">\nLink: <a href="URL">txt</a>\nInput: <input type="submit" value="preview" />\n========\n\nEs geht aber auch innerhalb eines Fliesstextes:\nMit ========<a href="URL">txt</a>======== wird kein Link erzeugt.\n\n<hr class="big_hr">\n\nh1. pre-Formarted-Text\n\nIn ==<pre>==-Tag eingeschlossener Text wird nicht escaped und nicht formatiert. D.h. tinytextile Markups werden nicht aufgel\xc3\x83\xc2\xb6st. HTML-Tags werden aber in pre-Areas vom Browser angezeigt:\n\n<pre>\nBeispiel:\n---------\nh2. Dies wird zu keiner HTML-\xc3\x83\xc5\x93berschrift\n<h3>Das ist eine manuell eingeleitete h3-\xc3\x83\xc5\x93berschrift</h3>\n* Dies bleibt normaler Text...\n* ...und wird keine Liste\n</pre>\n\n<hr class="big_hr">\n\nh1. HTML-Code\n\nHTML-Code wird einfach so belassen wie es ist:\n\nBeispiel:\n==\n<h3>Dies ist eine Tabelle</h3>\n<ul>\n   <li>1. Eintrag in der erste Ebene</li>\n   <ul>\n      <li>1. Unterprunkt in der zweiten Ebene</li>\n      <ul>\n         <li>1. Subunterpunkt in der dritten Ebene</li>\n         <li>2. Subunterpunkt in der dritten Ebene</li>\n      </ul>\n      <li>2. Unterprunkt in der zweiten Ebene</li>\n   </ul>\n   <li>2. Eintrag in der erste Ebene</li>\n   <li>3. Eintrag in der erste Ebene</li>\n</ul>\n\nHier kommt ein manueller Link zum: <a href="http://www.python-forum.de">Das deutsche Python-Forum</a>\n==\n\nErgibt:\n\n<h3>Dies ist eine Tabelle</h3>\n<ul>\n   <li>1. Eintrag in der erste Ebene</li>\n   <ul>\n      <li>1. Unterprunkt in der zweiten Ebene</li>\n      <ul>\n         <li>1. Subunterpunkt in der dritten Ebene</li>\n         <li>2. Subunterpunkt in der dritten Ebene</li>\n      </ul>\n      <li>2. Unterprunkt in der zweiten Ebene</li>\n   </ul>\n   <li>2. Eintrag in der erste Ebene</li>\n   <li>3. Eintrag in der erste Ebene</li>\n</ul>\n\nHier kommt ein manueller Link zum: <a href="http://www.python-forum.de">Das deutsche Python-Forum</a>\n\n<style type="text/css">\n.big_hr {\n  border:5px solid gray;\n  margin-top: 7em;\n}\n</style>', 2, 0, 'tinyTextile example', 'TinyTextileExample', 'complete tinyTextile Formating examples', 1, 1, '2', '', '', None, '2006-12-05 17:23:23', 14, 1, 1, 9, 9, 9]
[4, '<lucidTag:SiteMap/>', 2, 5, 'SiteMap', 'SiteMap', 'SiteMap', 1, 1, '2', '', '', None, '2006-06-16 16:08:09', 2, 1, 1, 1, 2, 1]
[5, 'h4. DE\n\nBitte nutzt das "Forum":http://pylucid.org/index.py/Forum/ , die Mailingliste bzw. Feature Requests/Bugs Seite von sourceforge! Wenn du mir eine pers?nliche eMail schreibst, k?nnen die anderen leider nicht einsehen und evtl. ist es auch f?r andere Interessant!\n\nh4. EN\n\nPlease use the "forum":http://pylucid.org/index.py/Forum/ , the mailinglist and Feature Requests/Bugs page at sourceforge! If you write me personally one mail, the other one cannot see. Perhaps would be also interesting for others.\n\nh3. Mailinglist\n* "pylucid-news":https://lists.sourceforge.net/lists/listinfo/pylucid-news - NEWS about new releases (low Traffic)\n* "pylucid-general":https://lists.sourceforge.net/lists/listinfo/pylucid-general - General discussion about PyLucid.\n\n<table style="border:1px solid #aa0033; font-size:small" align=center>\n  <tr>\n    <td rowspan=3>\n     <img src="http://groups.google.com/groups/img/groups_medium.gif" height=58 width=150 alt="Google Groups">\n    </td>\n    <td colspan=2 align=center><b>Subscribe to PyLucid-general</b></td>\n  </tr>\n  <form action="http://groups.google.com/group/PyLucid-general/boxsubscribe">\n  <tr> \n    <td>Email: <input type=text name=email></td>\n    <td>\n      <table \n       style="background-color:#ffcc33;padding:2px;border:2px outset #ffcc33;">\n      <tr>\n        <td>\n         <input type=submit name="sub" value="Subscribe">\n        </td>\n      </tr>\n      </table>\n    </td>\n  </tr>\n   </form>\n  <tr><td colspan=2 align=center>\n   <a href="http://groups.google.com/group/PyLucid-general">Browse Archives</a> at <a href="http://groups.google.com/">groups.google.com</a>\n  </td></tr>\n</table>\n\nh3. jabber\n\n* Look in the PyLucid Channel:\n** pylucid@conference.jabjab.de\n** pylucid@conference.jabber.org\n\nh3. IRC\n* You can find us in <a href="irc://irc.freenode.net/%23PyLucid.org">#PyLucid.org</a> on freenode.net, too: \n\nh3. support at "sourceforge":http://www.sourceforge.net/projects/pylucid/\n\n* Report "Feature Requests":http://sourceforge.net/tracker/?atid=764840&group_id=146328&func=browse | "Bugs":http://sourceforge.net/tracker/?atid=764837&group_id=146328&func=browse', 2, 3, 'contact', 'Contact', 'contact', 1, 1, '2', '', '', None, '2006-10-10 20:31:01', 1, 1, 1, 1, 1, 1]
[6, "&lt;lucidFunction:RSS&gt;url&lt;/lucidFunction&gt;\n\nIf you can't see the RSS-Feed, you must first install and activate the RSS Plugin to see the RSS-Feed:\n* log in\n* goto sub menu / Module Administration\n* install the RSS Plugin\n* activate it\n\nh2. PyLucid Project-NEWS RSS feed from sourceforge:\n\n<lucidFunction:RSS>http://sourceforge.net/export/rss2_projnews.php?group_id=146328&rss_fulltext=1</lucidFunction>", 2, 0, 'RSS', 'RSS', 'RSS feed test', 1, 1, '2', '', '', None, '2006-07-12 14:34:43', 1, 1, 1, 1, 1, 1]
[7, 'h2. ==<lucidFunction:SourceCode>== Plugin\n\nWith the SourceCode Plugin you can integrate the source code of a local file into your CMS page.\n\nExample Tag:\n<pre>==<lucidFunction:SourceCode>PyLucid/modules/auth/login.css</lucidFunction>==</pre>\n\nNote: With the ==<code>==-Tag you can directly put highlight source code into your CMS page, look at [[TinyTextileExample]]\n\nPyLucid used the Python syntax highlighter "Pygments":http://pygments.pocoo.org/ . It supports an ever-growing range of languages, look at: http://pygments.pocoo.org/docs/lexers/\n\nh3. some Examples:\n\nh5. ./PyLucid/modules/auth/login.css:\n\n<lucidFunction:SourceCode>PyLucid/modules/auth/login.css</lucidFunction>\n\n\n\nh5. ./PyLucid/buildin_plugins/MySQLdump/menu.js:\n\n<lucidFunction:SourceCode>PyLucid/buildin_plugins/MySQLdump/menu.js</lucidFunction>\n\n\n\nh5. ./PyLucid/buildin_plugins/sub_menu/sub_menu_cfg.py:\n\n<lucidFunction:SourceCode>PyLucid/buildin_plugins/sub_menu/sub_menu_cfg.py</lucidFunction>\n\nh2. ==<code>==-Tag\n\nUse ==<code=ext>...</code>== and PyLucid used Pygments to highlight it.\n\'ext\' is the typical fileextension/alias, please look at:\n\n * http://pygments.pocoo.org/docs/lexers/\n\nh3. examples\n\n==<code=css>\n.xs {font-family:verdana,arial,helvetica,sans-serif;font-size: x-small}\n.m {font-size: medium}\n</code>==\n\nresult:\n\n<code=css>\n.xs {font-family:verdana,arial,helvetica,sans-serif;font-size: x-small}\n.m {font-size: medium}\n</code>\n\nHere a "error" example:\n\n<code=NotExists>\nThis is a code with an unknown format!\n\nIf there exist no Lexer for the given format, PyLucid used the Pygments TextLexer.\nSo you can make <code=.xy>...</code>, where .xy is any externsion. But for all that it is well displayed through Pygments. Is that cool?\n\n=;-)\n</code>', 2, 0, 'SourceCode', 'SourceCode', 'SourceCode', 1, 1, '2', '', '', None, '2006-12-05 17:24:11', 14, 1, 1, 9, 9, 9]
[10, 'Here a example pages for the other designs.\n\nPlease look at the page "customise PyLucid":http://pylucid.org/index.py/CustomisePyLucid/\n\nh2. sub menu\n\n<lucidTag:sub_menu/>', 0, 0, 'Designs', 'Designs', 'Some other designs pages...', 1, 1, '2', '', '', None, '2007-01-09 14:54:06', 14, 1, 1, 9, 14, 9]
[11, 'h2. the small dark design\n\nHere a small dark design by Jens Diemer (based on a design by CUATRO)\n\nNotes:\n* The Menu only works for small pages\n\n----\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 10, 0, 'small dark', 'SmallDark', '', 6, 38, '2', '', '', None, '2007-01-09 14:51:56', 14, 1, 1, 14, 14, 14]
[12, 'Note: The old default Style is not the right one to start you own design! The CSS/Template a grow up into chaos ;)\n\n----\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 10, 0, 'old default', 'OldDefault', 'the old default ghastly design... ;)', 9, 41, '2', '', '', None, '2007-02-07 14:31:25', 14, 1, 1, 14, 14, 14]
[13, 'This discoloured, elementary CSS/Template is a good startpoint to make you own Design!\n\n----\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 10, 0, 'elementary', 'Elementary', 'elementary', 7, 39, '2', '', '', None, '2007-01-09 15:43:02', 14, 1, 1, 14, 14, 14]
[14, 'h2. a small white design\n\nBy:\n* Martin Bergner\n* Jens Diemer\n\nBased on the original design by "Andreas Viklund":http://andreasviklund.com\n\n----\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\n\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 10, 0, 'small white', 'SmallWhite', 'small white', 8, 40, '2', '', '', None, '2007-01-15 11:38:58', 14, 1, 1, 14, 14, 14]
]
