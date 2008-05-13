table = 'PyLucid_page'
fields = ['id', 'content', 'parent_id', 'position', 'name', 'shortcut', 'title', 'template_id', 'style_id', 'markup_id', 'keywords', 'description', 'createtime', 'lastupdatetime', 'createby_id', 'lastupdateby_id', 'showlinks', 'permitViewPublic', 'permitViewGroup_id', 'permitEditGroup_id']
#default item format: "fieldname":("type", "value")
default = {}
records = [
[1, u'<h2>Welcome to your PyLucid CMS =;-)</h2> \r\n<p>\r\nNote:\r\n</p>\r\n<ul>\r\n\t<li>After install deactivate the _install section!</li> \r\n</ul>\r\n<h3>list of last page updates</h3>\r\n<p>\r\n<a href="{% lucidTag RSSfeedGenerator count="10" %}" type="application/rss+xml" title="page updates">RSS feed</a><br />\r\n{% lucidTag page_update_list %}\r\n</p>\r\n', None, 0, u'index', u'index', u'index', 1, 1, 1, u'', u'', '2007-06-22 09:48:29', '2007-12-04 02:25:55', 1, 1, True, True, None, None]
[2, u'h2. sub menu\r\n\r\n{% lucidTag sub_menu %}', None, 0, u'example pages', u'ExamplePages', u'example pages', 1, 1, 2, u'', u'', '2007-06-22 09:48:29', '2007-06-22 09:48:33', 1, 1, True, True, None, None]
[3, u'h1. tinyTextile help\r\n\r\nh1. headlines\r\n\r\nheadlines are introduced with \'h1.\':\r\n\r\n<pre>\r\nh1. h-1 headline\r\n\r\nh2. h-2 headline\r\n</pre>\r\n\r\nResult:\r\n\r\nh1. h-1 headline\r\n\r\nh2. h-2 headline\r\n\r\n(Important: one blank line under the headline!)\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Text formatting\r\n\r\n<pre>\r\nI am a --small-- word with &lt;small&gt; tag.\r\nThis is a *fat* word with &lt;strong&gt; tag.\r\n</pre>\r\n\r\nResult:\r\n\r\nI am a --small-- word with ==<small>== tag.\r\nThis is a *fat* word with ==<strong>== tag.\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Links\r\n\r\nLinks according in the following pattern:\r\n\r\n<pre>"LinkText":URL</pre>\r\n\r\nexamples:\r\n<pre>\r\nhttp://exampledomain.dtl\r\nftp://exampledomain.dtl\r\nmailto:name@exampledomain.dtl\r\nhttp://www.python-forum.de\r\nor better: "Das deutsche Python-Forum":http://www.python-forum.de\r\nThis is a link, too: "Link":?#unten\r\nWiki like, internal PyLucid links: [[ExamplePageName]]\r\n</pre>\r\n\r\nResult:\r\nhttp://exampledomain.dtl\r\nftp://exampledomain.dtl\r\nmailto:name@exampledomain.dtl\r\nhttp://www.python-forum.de\r\nor better: "Das deutsche Python-Forum":http://www.python-forum.de\r\nThis is a link, too: "Link":?#unten\r\nWiki like, internal PyLucid links: [[ExamplePageName]]\r\n\r\n<hr class="big_hr">\r\n\r\nh1. List\r\n\r\nYou can make ==<ul>== liste with "*" and ==<ol>== list with "#".\r\nNote: You can\'t mixed this list types ;)\r\n\r\nexamples:\r\n\r\n<pre>\r\nnormal list:\r\n* Lorem ipsum dolor sit amet\r\n** consectetuer adipiscing elit\r\n**** sed diam nonummy nibh\r\n**** euismod tincidunt ut laoreet\r\n** dolore magna aliquam erat volutpat.\r\n\r\nnumbered list:\r\n# Lorem ipsum dolor sit amet\r\n## consectetuer adipiscing elit\r\n#### sed diam nonummy nibh\r\n#### euismod tincidunt ut laoreet\r\n## dolore magna aliquam erat volutpat.\r\n</pre>\r\n\r\nResult:\r\n\r\nnormal list:\r\n* Lorem ipsum dolor sit amet\r\n** consectetuer adipiscing elit\r\n**** sed diam nonummy nibh\r\n**** euismod tincidunt ut laoreet\r\n** dolore magna aliquam erat volutpat.\r\n\r\nnumbered list:\r\n# Lorem ipsum dolor sit amet\r\n## consectetuer adipiscing elit\r\n#### sed diam nonummy nibh\r\n#### euismod tincidunt ut laoreet\r\n## dolore magna aliquam erat volutpat.\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Bilder\r\n\r\nEin HTML-img-Tag wird erzeugt, wenn eine Adresse mit einem "!"-Zeichen\r\numschlossen ist.\r\n\r\n<pre>\r\n!http://images.sourceforge.net/images/project-support.jpg!\r\n!/favicon.ico!\r\n!http://domain.tld/pics/ich werde zu keiner URL weil hier leerzeichen sind.jpg!\r\n</pre>\r\n\r\nResult:\r\n\r\n!http://images.sourceforge.net/images/project-support.jpg!\r\n!/favicon.ico!\r\n!http://domain.tld/pics/ich werde zu keiner URL weil hier leerzeichen sind.jpg!\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Embed Python SourceCode\r\n\r\nPut sourcecode between ==<python>== tag. Note: The start and end tag must be located alone in a line!\r\n\r\nexample:\r\n\r\n==\r\n<python>\r\n#!/usr/bin/python\r\n# -*- coding: UTF-8 -*-\r\n\r\n"""Ein kleines Skript"""\r\n\r\nprint "Hello Word: I love Python!"\r\n</python>\r\n==\r\n\r\nResult:\r\n<python>\r\n#!/usr/bin/python\r\n# -*- coding: UTF-8 -*-\r\n\r\n"""Ein kleines Skript"""\r\n\r\nprint "Hello Word: I love Python!"\r\n</python>\r\n\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Embed source code generally\r\n\r\nWith the ==<code=ext>== Tag you can highlight everything, which offers Pygments.\r\n\'ext\' is the file extension.\r\n\r\nexamples:\r\n\r\n==\r\n<code=php>\r\n<?php\r\n$conn_id = ftp_connect($ftp_server);\r\n?>\r\n</code>\r\n<code=css>\r\nbody {\r\n  color: black;\r\n}\r\n</code>\r\n==\r\n\r\nResult:\r\n\r\n<code=php>\r\n<?php\r\n$conn_id = ftp_connect($ftp_server);\r\n?>\r\n</code>\r\n<code=css>\r\nbody {\r\n  color: black;\r\n}\r\n</code>\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Escaping\r\n\r\nText inner two "="-chars would be escaped.\r\n\r\nexample:\r\n--------\r\n========\r\nTable: <table width="90%" border="0" align="center">\r\nLink: <a href="URL">txt</a>\r\nInput: <input type="submit" value="preview" />\r\n========\r\n\r\nIt goes also within a flow text:\r\nHere ist no Link: ========<a href="URL">txt</a>======== nice?\r\n\r\n<hr class="big_hr">\r\n\r\nh1. pre-Formarted-Text\r\n\r\nYou can use the ==<pre>== tag. tinyTextile ingnore the Markup in the area.\r\n\r\n<pre>\r\nExample:\r\n---------\r\nh2. Not a textile headline\r\n<h3>Manuelly h3 headline with html tags</h3>\r\n* This is not a...\r\n* ...textile list\r\n</pre>\r\n\r\n<hr class="big_hr">\r\n\r\nh1. HTML-Code\r\n\r\nYou can insert any HTML code directy in you page. tinyTextile ingnore it.', 2, 0, u'tinyTextile example', u'TinyTextileExample', u'complete tinyTextile Formating examples', 1, 1, 2, u'', u'', '2007-06-22 09:48:29', '2007-06-22 09:51:45', 1, 1, True, True, None, None]
[4, u'{% lucidTag SiteMap %}', 2, 5, u'SiteMap', u'SiteMap', u'SiteMap', 1, 1, 2, u'', u'', '2007-06-22 09:48:29', '2007-06-22 09:48:33', 1, 1, True, True, None, None]
[6, u'With this lucidTag you can easy integrade a RSS news feed into your CMS page:\r\n\r\n<code>\r\n{% lucidTag RSS url="http url" title="a feed" %}\r\n</code>\r\n\r\nHere a example:\r\n\r\nh2. PyLucid Project-NEWS RSS feed from sourceforge:\r\n\r\n{% lucidTag RSS url="http://sourceforge.net/export/rss2_projnews.php?group_id=146328&rss_fulltext=1" title="new from sf.net" %}', 2, 0, u'RSS', u'RSS', u'RSS feed test', 1, 1, 2, u'', u'', '2007-06-22 09:48:29', '2007-10-29 05:42:29', 1, 1, True, True, None, None]
[7, u'h2. SourceCode Plugin\r\n\r\nWith the SourceCode Plugin you can integrate the source code of a local file into your CMS page.\r\n\r\nExample Tag:\r\n<pre>&#x7B;% lucidTag SourceCode url=&quot;./media/PyLucid/install_views.css&quot; %&#x7D;</pre>\r\n\r\nNote: With the ==<code>==-Tag you can directly put highlight source code into your CMS page, look at [[TinyTextileExample]]\r\n\r\nPyLucid used the Python syntax highlighter "Pygments":http://pygments.pocoo.org/ . It supports an ever-growing range of languages, look at: http://pygments.pocoo.org/docs/lexers/\r\n\r\nh3. some Examples:\r\n\r\nh5. ./media/PyLucid/install_views.css:\r\n\r\n{% lucidTag SourceCode url="./media/PyLucid/install_views.css" %}\r\n\r\n\r\n\r\nh5. ./media/PyLucid/shared_sha_tools.js:\r\n\r\n{% lucidTag SourceCode url="./media/PyLucid/shared_sha_tools.js" %}\r\n\r\n\r\n\r\nh2. ==<code>==-Tag\r\n\r\nUse ==<code=ext>...</code>== and PyLucid used Pygments to highlight it.\r\n\'ext\' is the typical fileextension/alias, please look at:\r\n\r\n * http://pygments.pocoo.org/docs/lexers/\r\n\r\nh3. examples\r\n\r\n==<code=css>\r\n.xs {font-family:verdana,arial,helvetica,sans-serif;font-size: x-small}\r\n.m {font-size: medium}\r\n</code>==\r\n\r\nresult:\r\n\r\n<code=css>\r\n.xs {font-family:verdana,arial,helvetica,sans-serif;font-size: x-small}\r\n.m {font-size: medium}\r\n</code>\r\n\r\nHere a "error" example:\r\n\r\n<code=NotExists>\r\nThis is a code with an unknown format!\r\n\r\nIf there exist no Lexer for the given format, PyLucid used the Pygments TextLexer.\r\nSo you can make <code=.xy>...</code>, where .xy is any externsion. But for all that it is well displayed through Pygments. Is that cool?\r\n\r\n=;-)\r\n</code>', 2, 0, u'SourceCode', u'SourceCode', u'SourceCode', 1, 1, 2, u'', u'', '2007-06-22 09:48:29', '2007-10-29 05:44:26', 1, 1, True, True, None, None]
[8, u'Here a example pages for the other designs.\r\n\r\nPlease look at the page "customise PyLucid":http://www.pylucid.org/customise-PyLucid/\r\n\r\nh2. sub menu\r\n\r\n{% lucidTag sub_menu %}', None, 0, u'Designs', u'Designs', u'Some other designs pages...', 1, 1, 2, u'', u'', '2007-06-22 09:48:29', '2007-10-29 05:48:58', 1, 1, True, True, None, None]
[9, u'h2. the small dark design\r\n\r\nHere a small dark design by Jens Diemer (based on a design by CUATRO)\r\n\r\nNotes:\r\n* The Menu only works for small pages\r\n\r\n----\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 8, 0, u'small dark', u'SmallDark', u'', 3, 4, 2, u'', u'', '2007-06-22 09:48:29', '2007-06-22 09:48:29', 1, 1, True, True, None, None]
[10, u'Note: The old default Style is not the right one to start you own design! The CSS/Template a grow up into chaos ;)\r\n\r\n----\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 8, 5, u'old default', u'old-default', u'the old default ghastly design... ;)', 2, 3, 2, u'', u'', '2007-06-22 09:48:29', '2007-10-29 05:49:43', 1, 1, True, True, None, None]
[11, u'This discoloured, elementary CSS/Template is a good startpoint to make you own Design!\r\n\r\n----\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 8, 0, u'elementary', u'elementary', u'elementary', 4, 5, 2, u'', u'', '2007-06-22 09:48:29', '2007-10-29 05:49:53', 1, 1, True, True, None, None]
[12, u'h2. a small white design\r\n\r\nBy:\r\n* Martin Bergner\r\n* Jens Diemer\r\n\r\nBased on the original design by "Andreas Viklund":http://andreasviklund.com\r\n\r\n----\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', 8, -5, u'small white', u'small-white', u'small white', 5, 6, 2, u'', u'', '2007-06-22 09:48:29', '2007-10-29 05:49:43', 1, 1, True, True, None, None]
[13, u'{% lucidTag sub_menu %}', 2, 0, u'Markups', u'Markups', u'Markup test pages', 1, 1, 2, u'', u'', '2007-06-26 01:31:02', '2007-06-26 01:32:09', 1, 1, True, True, None, None]
[14, u'h1. headlines\r\n\r\nheadlines are introduced with \'h1.\':\r\n\r\n<pre>\r\nh1. h-1 headline\r\n\r\nh2. h-2 headline\r\n</pre>\r\n\r\nResult:\r\n\r\nh1. h-1 headline\r\n\r\nh2. h-2 headline\r\n\r\n(Important: one blank line under the headline!)\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Text formatting\r\n\r\n<pre>\r\nI am a --small-- word with &lt;small&gt; tag.\r\nThis is a *fat* word with &lt;strong&gt; tag.\r\n</pre>\r\n\r\nResult:\r\n\r\nI am a --small-- word with ==<small>== tag.\r\nThis is a *fat* word with ==<strong>== tag.\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Links\r\n\r\nLinks according in the following pattern:\r\n\r\n<pre>"LinkText":URL</pre>\r\n\r\nexamples:\r\n<pre>\r\nhttp://exampledomain.dtl\r\nftp://exampledomain.dtl\r\nmailto:name@exampledomain.dtl\r\nhttp://www.python-forum.de\r\nor better: "Das deutsche Python-Forum":http://www.python-forum.de\r\nThis is a link, too: "Link":?#unten\r\nWiki like, internal PyLucid links: [[ExamplePageName]]\r\n</pre>\r\n\r\nResult:\r\nhttp://exampledomain.dtl\r\nftp://exampledomain.dtl\r\nmailto:name@exampledomain.dtl\r\nhttp://www.python-forum.de\r\nor better: "Das deutsche Python-Forum":http://www.python-forum.de\r\nThis is a link, too: "Link":?#unten\r\nWiki like, internal PyLucid links: [[ExamplePageName]]\r\n\r\n<hr class="big_hr">\r\n\r\nh1. List\r\n\r\nYou can make ==<ul>== liste with "*" and ==<ol>== list with "#".\r\nNote: You can\'t mixed this list types ;)\r\n\r\nexamples:\r\n\r\n<pre>\r\nnormal list:\r\n* Lorem ipsum dolor sit amet\r\n** consectetuer adipiscing elit\r\n**** sed diam nonummy nibh\r\n**** euismod tincidunt ut laoreet\r\n** dolore magna aliquam erat volutpat.\r\n\r\nnumbered list:\r\n# Lorem ipsum dolor sit amet\r\n## consectetuer adipiscing elit\r\n#### sed diam nonummy nibh\r\n#### euismod tincidunt ut laoreet\r\n## dolore magna aliquam erat volutpat.\r\n</pre>\r\n\r\nResult:\r\n\r\nnormal list:\r\n* Lorem ipsum dolor sit amet\r\n** consectetuer adipiscing elit\r\n**** sed diam nonummy nibh\r\n**** euismod tincidunt ut laoreet\r\n** dolore magna aliquam erat volutpat.\r\n\r\nnumbered list:\r\n# Lorem ipsum dolor sit amet\r\n## consectetuer adipiscing elit\r\n#### sed diam nonummy nibh\r\n#### euismod tincidunt ut laoreet\r\n## dolore magna aliquam erat volutpat.\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Bilder\r\n\r\nEin HTML-img-Tag wird erzeugt, wenn eine Adresse mit einem "!"-Zeichen\r\numschlossen ist.\r\n\r\n<pre>\r\n!http://images.sourceforge.net/images/project-support.jpg!\r\n!/favicon.ico!\r\n!http://domain.tld/pics/ich werde zu keiner URL weil hier leerzeichen sind.jpg!\r\n</pre>\r\n\r\nResult:\r\n\r\n!http://images.sourceforge.net/images/project-support.jpg!\r\n!/favicon.ico!\r\n!http://domain.tld/pics/ich werde zu keiner URL weil hier leerzeichen sind.jpg!\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Embed Python SourceCode\r\n\r\nPut sourcecode between ==<python>== tag. Note: The start and end tag must be located alone in a line!\r\n\r\nexample:\r\n\r\n==\r\n<python>\r\n#!/usr/bin/python\r\n# -*- coding: UTF-8 -*-\r\n\r\n"""Ein kleines Skript"""\r\n\r\nprint "Hello Word: I love Python!"\r\n</python>\r\n==\r\n\r\nResult:\r\n<python>\r\n#!/usr/bin/python\r\n# -*- coding: UTF-8 -*-\r\n\r\n"""Ein kleines Skript"""\r\n\r\nprint "Hello Word: I love Python!"\r\n</python>\r\n\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Embed source code generally\r\n\r\nWith the ==<code=ext>== Tag you can highlight everything, which offers Pygments.\r\n\'ext\' is the file extension.\r\n\r\nexamples:\r\n\r\n==\r\n<code=php>\r\n<?php\r\n$conn_id = ftp_connect($ftp_server);\r\n?>\r\n</code>\r\n<code=css>\r\nbody {\r\n  color: black;\r\n}\r\n</code>\r\n==\r\n\r\nResult:\r\n\r\n<code=php>\r\n<?php\r\n$conn_id = ftp_connect($ftp_server);\r\n?>\r\n</code>\r\n<code=css>\r\nbody {\r\n  color: black;\r\n}\r\n</code>\r\n\r\n<hr class="big_hr">\r\n\r\nh1. Escaping\r\n\r\nText inner two "="-chars would be escaped.\r\n\r\nexample:\r\n--------\r\n========\r\nTable: <table width="90%" border="0" align="center">\r\nLink: <a href="URL">txt</a>\r\nInput: <input type="submit" value="preview" />\r\n========\r\n\r\nIt goes also within a flow text:\r\nHere ist no Link: ========<a href="URL">txt</a>======== nice?\r\n\r\n<hr class="big_hr">\r\n\r\nh1. pre-Formarted-Text\r\n\r\nYou can use the ==<pre>== tag. tinyTextile ingnore the Markup in the area.\r\n\r\n<pre>\r\nExample:\r\n---------\r\nh2. Not a textile headline\r\n<h3>Manuelly h3 headline with html tags</h3>\r\n* This is not a...\r\n* ...textile list\r\n</pre>\r\n\r\n<hr class="big_hr">\r\n\r\nh1. HTML-Code\r\n\r\nYou can insert any HTML code directy in you page. tinyTextile ingnore it.', 13, 0, u'tinyTextile', u'TinyTextileExample1', u'tinyTextile Example', 1, 1, 2, u'', u'', '2007-06-26 01:34:19', '2007-06-26 01:34:19', 1, 1, True, True, None, None]
[15, u'h2{color:green}. This is a title\r\n\r\nh3. This is a subhead\r\n\r\np{color:red}. This is some text of dubious character. Isn\'t the use of "quotes" just lazy writing -- and theft of \'intellectual property\' besides? I think the time has come to see a block quote.\r\n\r\nbq[fr]. This is a block quote. I\'ll admit it\'s not the most exciting block quote ever devised.\r\n\r\nSimple list:\r\n\r\n#{color:blue} one\r\n# two\r\n# three\r\n\r\nMulti-level list:\r\n\r\n# one\r\n## aye\r\n## bee\r\n## see\r\n# two\r\n## x\r\n## y\r\n# three\r\n\r\nMixed list:\r\n\r\n* Point one\r\n* Point two\r\n## Step 1\r\n## Step 2\r\n## Step 3\r\n* Point three\r\n** Sub point 1\r\n** Sub point 2\r\n\r\n\r\nWell, that went well. How about we insert an <a href="/" title="watch out">old-fashioned hypertext link</a>? Will the quote marks in the tags get messed up? No!\r\n\r\n"This is a link (optional title)":http://www.textism.com\r\n\r\ntable{border:1px solid black}.\r\n|_. this|_. is|_. a|_. header|\r\n<{background:gray}. |\\2. this is|{background:red;width:200px}. a|^<>{height:200px}. row|\r\n|this|<>{padding:10px}. is|^. another|(bob#bob). row|\r\n\r\nAn image:\r\n\r\n!/common/textist.gif(optional alt text)!\r\n\r\n# Librarians rule\r\n# Yes they do\r\n# But you knew that\r\n\r\nSome more text of dubious character. Here is a noisome string of CAPITAL letters. Here is something we want to _emphasize_. \r\nThat was a linebreak. And something to indicate *strength*. Of course I could use <em>my own HTML tags</em> if I <strong>felt</strong> like it.\r\n\r\nh3. Coding\r\n\r\nThis <code>is some code, "isn\'t it"</code>. Watch those quote marks! Now for some preformatted text:\r\n\r\n<pre>\r\n<code>\r\n\t$text = str_replace("<p>%::%</p>","",$text);\r\n\t$text = str_replace("%::%</p>","",$text);\r\n\t$text = str_replace("%::%","",$text);\r\n\r\n</code>\r\n</pre>\r\n\r\nThis isn\'t code.\r\n\r\n\r\nSo you see, my friends:\r\n\r\n* The time is now\r\n* The time is not later\r\n* The time is not yesterday\r\n* We must act\r\n\r\n', 13, 0, u'Textile (original)', u'TextileOriginal', u'', 1, 1, 3, u'', u'', '2007-06-26 01:35:24', '2007-06-26 01:35:24', 1, 1, True, True, None, None]
[16, u"A First Level Header\r\n====================\r\n\r\nA Second Level Header\r\n---------------------\r\n\r\nNow is the time for all good men to come to\r\nthe aid of their country. This is just a\r\nregular paragraph.\r\n\r\nThe quick brown fox jumped over the lazy\r\ndog's back.\r\n\r\n### Header 3\r\n\r\n> This is a blockquote.\r\n> \r\n> This is the second paragraph in the blockquote.\r\n>\r\n> ## This is an H2 in a blockquote", 13, 0, u'Markdown', u'Markdown', u'', 1, 1, 4, u'', u'', '2007-06-26 01:38:42', '2007-06-26 01:38:42', 1, 1, True, True, None, None]
[17, u'A ReStructuredText Primer\r\n=========================\r\n\r\n:Author: Richard Jones\r\n:Version: $Revision: 4350 $\r\n:Copyright: This document has been placed in the public domain.\r\n\r\n.. contents::\r\n\r\n\r\nThe text below contains links that look like "(quickref__)".  These\r\nare relative links that point to the `Quick reStructuredText`_ user\r\nreference.  If these links don\'t work, please refer to the `master\r\nquick reference`_ document.\r\n\r\n__\r\n.. _Quick reStructuredText: quickref.html\r\n.. _master quick reference:\r\n   http://docutils.sourceforge.net/docs/user/rst/quickref.html\r\n\r\n\r\nStructure\r\n---------\r\n\r\nFrom the outset, let me say that "Structured Text" is probably a bit\r\nof a misnomer.  It\'s more like "Relaxed Text" that uses certain\r\nconsistent patterns.  These patterns are interpreted by a HTML\r\nconverter to produce "Very Structured Text" that can be used by a web\r\nbrowser.\r\n\r\nThe most basic pattern recognised is a **paragraph** (quickref__).\r\nThat\'s a chunk of text that is separated by blank lines (one is\r\nenough).  Paragraphs must have the same indentation -- that is, line\r\nup at their left edge.  Paragraphs that start indented will result in\r\nindented quote paragraphs. For example::\r\n\r\n  This is a paragraph.  It\'s quite\r\n  short.\r\n\r\n     This paragraph will result in an indented block of\r\n     text, typically used for quoting other text.\r\n\r\n  This is another one.\r\n\r\nResults in:\r\n\r\n  This is a paragraph.  It\'s quite\r\n  short.\r\n\r\n     This paragraph will result in an indented block of\r\n     text, typically used for quoting other text.\r\n\r\n  This is another one.\r\n\r\n__ quickref.html#paragraphs\r\n\r\n\r\nText styles\r\n-----------\r\n\r\n(quickref__)\r\n\r\n__ quickref.html#inline-markup\r\n\r\nInside paragraphs and other bodies of text, you may additionally mark\r\ntext for *italics* with "``*italics*``" or **bold** with\r\n"``**bold**``".\r\n\r\nIf you want something to appear as a fixed-space literal, use\r\n"````double back-quotes````".  Note that no further fiddling is done\r\ninside the double back-quotes -- so asterisks "``*``" etc. are left\r\nalone.\r\n\r\nIf you find that you want to use one of the "special" characters in\r\ntext, it will generally be OK -- reStructuredText is pretty smart.\r\nFor example, this * asterisk is handled just fine.  If you actually\r\nwant text \\*surrounded by asterisks* to **not** be italicised, then\r\nyou need to indicate that the asterisk is not special.  You do this by\r\nplacing a backslash just before it, like so "``\\*``" (quickref__), or\r\nby enclosing it in double back-quotes (inline literals), like this::\r\n\r\n    ``\\*``\r\n\r\n__ quickref.html#escaping\r\n\r\n\r\nLists\r\n-----\r\n\r\nLists of items come in three main flavours: **enumerated**,\r\n**bulleted** and **definitions**.  In all list cases, you may have as\r\nmany paragraphs, sublists, etc. as you want, as long as the left-hand\r\nside of the paragraph or whatever aligns with the first line of text\r\nin the list item.\r\n\r\nLists must always start a new paragraph -- that is, they must appear\r\nafter a blank line.\r\n\r\n**enumerated** lists (numbers, letters or roman numerals; quickref__)\r\n  __ quickref.html#enumerated-lists\r\n\r\n  Start a line off with a number or letter followed by a period ".",\r\n  right bracket ")" or surrounded by brackets "( )" -- whatever you\'re\r\n  comfortable with.  All of the following forms are recognised::\r\n\r\n    1. numbers\r\n\r\n    A. upper-case letters\r\n       and it goes over many lines\r\n\r\n       with two paragraphs and all!\r\n\r\n    a. lower-case letters\r\n\r\n       3. with a sub-list starting at a different number\r\n       4. make sure the numbers are in the correct sequence though!\r\n\r\n    I. upper-case roman numerals\r\n\r\n    i. lower-case roman numerals\r\n\r\n    (1) numbers again\r\n\r\n    1) and again\r\n\r\n  Results in (note: the different enumerated list styles are not\r\n  always supported by every web browser, so you may not get the full\r\n  effect here):\r\n\r\n  1. numbers\r\n\r\n  A. upper-case letters\r\n     and it goes over many lines\r\n\r\n     with two paragraphs and all!\r\n\r\n  a. lower-case letters\r\n\r\n     3. with a sub-list starting at a different number\r\n     4. make sure the numbers are in the correct sequence though!\r\n\r\n  I. upper-case roman numerals\r\n\r\n  i. lower-case roman numerals\r\n\r\n  (1) numbers again\r\n\r\n  1) and again\r\n\r\n**bulleted** lists (quickref__)\r\n  __ quickref.html#bullet-lists\r\n\r\n  Just like enumerated lists, start the line off with a bullet point\r\n  character - either "-", "+" or "*"::\r\n\r\n    * a bullet point using "*"\r\n\r\n      - a sub-list using "-"\r\n\r\n        + yet another sub-list\r\n\r\n      - another item\r\n\r\n  Results in:\r\n\r\n  * a bullet point using "*"\r\n\r\n    - a sub-list using "-"\r\n\r\n      + yet another sub-list\r\n\r\n    - another item\r\n\r\n**definition** lists (quickref__)\r\n  __ quickref.html#definition-lists\r\n\r\n  Unlike the other two, the definition lists consist of a term, and\r\n  the definition of that term.  The format of a definition list is::\r\n\r\n    what\r\n      Definition lists associate a term with a definition.\r\n\r\n    *how*\r\n      The term is a one-line phrase, and the definition is one or more\r\n      paragraphs or body elements, indented relative to the term.\r\n      Blank lines are not allowed between term and definition.\r\n\r\n  Results in:\r\n\r\n  what\r\n    Definition lists associate a term with a definition.\r\n\r\n  *how*\r\n    The term is a one-line phrase, and the definition is one or more\r\n    paragraphs or body elements, indented relative to the term.\r\n    Blank lines are not allowed between term and definition.\r\n\r\n\r\nPreformatting (code samples)\r\n----------------------------\r\n(quickref__)\r\n\r\n__ quickref.html#literal-blocks\r\n\r\nTo just include a chunk of preformatted, never-to-be-fiddled-with\r\ntext, finish the prior paragraph with "``::``".  The preformatted\r\nblock is finished when the text falls back to the same indentation\r\nlevel as a paragraph prior to the preformatted block.  For example::\r\n\r\n  An example::\r\n\r\n      Whitespace, newlines, blank lines, and all kinds of markup\r\n        (like *this* or \\this) is preserved by literal blocks.\r\n    Lookie here, I\'ve dropped an indentation level\r\n    (but not far enough)\r\n\r\n  no more example\r\n\r\nResults in:\r\n\r\n  An example::\r\n\r\n      Whitespace, newlines, blank lines, and all kinds of markup\r\n        (like *this* or \\this) is preserved by literal blocks.\r\n    Lookie here, I\'ve dropped an indentation level\r\n    (but not far enough)\r\n\r\n  no more example\r\n\r\nNote that if a paragraph consists only of "``::``", then it\'s removed\r\nfrom the output::\r\n\r\n  ::\r\n\r\n      This is preformatted text, and the\r\n      last "::" paragraph is removed\r\n\r\nResults in:\r\n\r\n::\r\n\r\n    This is preformatted text, and the\r\n    last "::" paragraph is removed\r\n\r\n\r\nSections\r\n--------\r\n\r\n(quickref__)\r\n\r\n__ quickref.html#section-structure\r\n\r\nTo break longer text up into sections, you use **section headers**.\r\nThese are a single line of text (one or more words) with adornment: an\r\nunderline alone, or an underline and an overline together, in dashes\r\n"``-----``", equals "``======``", tildes "``~~~~~~``" or any of the\r\nnon-alphanumeric characters ``= - ` : \' " ~ ^ _ * + # < >`` that you\r\nfeel comfortable with.  An underline-only adornment is distinct from\r\nan overline-and-underline adornment using the same character.  The\r\nunderline/overline must be at least as long as the title text.  Be\r\nconsistent, since all sections marked with the same adornment style\r\nare deemed to be at the same level::\r\n\r\n  Chapter 1 Title\r\n  ===============\r\n\r\n  Section 1.1 Title\r\n  -----------------\r\n\r\n  Subsection 1.1.1 Title\r\n  ~~~~~~~~~~~~~~~~~~~~~~\r\n\r\n  Section 1.2 Title\r\n  -----------------\r\n\r\n  Chapter 2 Title\r\n  ===============\r\n\r\nThis results in the following structure, illustrated by simplified\r\npseudo-XML::\r\n\r\n    <section>\r\n        <title>\r\n            Chapter 1 Title\r\n        <section>\r\n            <title>\r\n                Section 1.1 Title\r\n            <section>\r\n                <title>\r\n                    Subsection 1.1.1 Title\r\n        <section>\r\n            <title>\r\n                Section 1.2 Title\r\n    <section>\r\n        <title>\r\n            Chapter 2 Title\r\n\r\n(Pseudo-XML uses indentation for nesting and has no end-tags.  It\'s\r\nnot possible to show actual processed output, as in the other\r\nexamples, because sections cannot exist inside block quotes.  For a\r\nconcrete example, compare the section structure of this document\'s\r\nsource text and processed output.)\r\n\r\nNote that section headers are available as link targets, just using\r\ntheir name.  To link to the Lists_ heading, I write "``Lists_``".  If\r\nthe heading has a space in it like `text styles`_, we need to quote\r\nthe heading "```text styles`_``".\r\n\r\n\r\nDocument Title / Subtitle\r\n`````````````````````````\r\n\r\nThe title of the whole document is distinct from section titles and\r\nmay be formatted somewhat differently (e.g. the HTML writer by default\r\nshows it as a centered heading).\r\n\r\nTo indicate the document title in reStructuredText, use a unique adornment\r\nstyle at the beginning of the document.  To indicate the document subtitle,\r\nuse another unique adornment style immediately after the document title.  For\r\nexample::\r\n\r\n    ================\r\n     Document Title\r\n    ================\r\n    ----------\r\n     Subtitle\r\n    ----------\r\n\r\n    Section Title\r\n    =============\r\n\r\n    ...\r\n\r\nNote that "Document Title" and "Section Title" above both use equals\r\nsigns, but are distict and unrelated styles.  The text of\r\noverline-and-underlined titles (but not underlined-only) may be inset\r\nfor aesthetics.\r\n\r\n\r\nImages\r\n------\r\n\r\n(quickref__)\r\n\r\n__ quickref.html#directives\r\n\r\nTo include an image in your document, you use the the ``image`` directive__.\r\nFor example::\r\n\r\n  .. image:: images/biohazard.png\r\n\r\nresults in:\r\n\r\n.. image:: images/biohazard.png\r\n\r\nThe ``images/biohazard.png`` part indicates the filename of the image\r\nyou wish to appear in the document. There\'s no restriction placed on\r\nthe image (format, size etc).  If the image is to appear in HTML and\r\nyou wish to supply additional information, you may::\r\n\r\n  .. image:: images/biohazard.png\r\n     :height: 100\r\n     :width: 200\r\n     :scale: 50\r\n     :alt: alternate text\r\n\r\nSee the full `image directive documentation`__ for more info.\r\n\r\n__ ../../ref/rst/directives.html\r\n__ ../../ref/rst/directives.html#images\r\n\r\n\r\nWhat Next?\r\n----------\r\n\r\nThis primer introduces the most common features of reStructuredText,\r\nbut there are a lot more to explore.  The `Quick reStructuredText`_\r\nuser reference is a good place to go next.  For complete details, the\r\n`reStructuredText Markup Specification`_ is the place to go [#]_.\r\n\r\nUsers who have questions or need assistance with Docutils or\r\nreStructuredText should post a message to the Docutils-users_ mailing\r\nlist.\r\n\r\n.. [#] If that relative link doesn\'t work, try the master document:\r\n   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html.\r\n\r\n.. _reStructuredText Markup Specification:\r\n   ../../ref/rst/restructuredtext.html\r\n.. _Docutils-users: ../mailing-lists.html#docutils-users\r\n.. _Docutils project web site: http://docutils.sourceforge.net/\r\n', 13, 0, u'reStructuredText', u'ReStructuredText', u'', 1, 1, 5, u'', u'', '2007-06-26 01:42:59', '2007-06-26 01:42:59', 1, 1, True, True, None, None]
[19, u'= Top-level heading (1)\r\n== This a test for creole 0.1 (2)\r\n=== This is a Subheading (3)\r\n==== Subsub (4)\r\n===== Subsubsub (5)\r\n\r\nThe ending equal signs should not be displayed:\r\n\r\n= Top-level heading (1) =\r\n== This a test for creole 0.1 (2) ==\r\n=== This is a Subheading (3) ===\r\n==== Subsub (4) ====\r\n===== Subsubsub (5) =====\r\n\r\n\r\nYou can make things **bold** or //italic// or **//both//** or //**both**//.\r\n\r\nCharacter formatting extends across line breaks: **bold,\r\nthis is still bold. This line deliberately does not end in star-star.\r\n\r\nNot bold. Character formatting does not cross paragraph boundaries.\r\n\r\nYou can use [[internal links]] or [[http://www.wikicreole.org|external links]],\r\ngive the link a [[internal links|different]] name.\r\n\r\nHere\'s another sentence: This wisdom is taken from [[Ward Cunningham\'s]]\r\n[[http://www.c2.com/doc/wikisym/WikiSym2006.pdf|Presentation at the Wikisym 06]].\r\n\r\nHere\'s a external link without a description: [[http://www.wikicreole.org]]\r\n\r\nBe careful that italic links are rendered properly:  //[[http://my.book.example/|My Book Title]]// \r\n\r\nFree links without braces should be rendered as well, like http://www.wikicreole.org/ and http://www.wikicreole.org/users/~example. \r\n\r\nCreole1.0 specifies that http://bar and ftp://bar should not render italic,\r\nsomething like foo://bar should render as italic.\r\n\r\nYou can use this to draw a line to separate the page:\r\n----\r\n\r\nYou can use lists, start it at the first column for now, please...\r\n\r\nunnumbered lists are like\r\n* item a\r\n* item b\r\n* **bold item c**\r\n\r\nblank space is also permitted before lists like:\r\n  *   item a\r\n * item b\r\n* item c\r\n ** item c.a\r\n\r\nor you can number them\r\n# [[item 1]]\r\n# item 2\r\n# // italic item 3 //\r\n    ## item 3.1\r\n  ## item 3.2\r\n\r\nup to five levels\r\n* 1\r\n** 2\r\n*** 3\r\n**** 4\r\n***** 5\r\n\r\n* You can have\r\nmultiline list items\r\n* this is a second multiline\r\nlist item\r\n\r\nYou can use nowiki syntax if you would like do stuff like this:\r\n\r\n{{{\r\nGuitar Chord C:\r\n\r\n||---|---|---|\r\n||-0-|---|---|\r\n||---|---|---|\r\n||---|-0-|---|\r\n||---|---|-0-|\r\n||---|---|---|\r\n}}}\r\n\r\nNote: if you look at the source code of the above, you see the escape char (tilde, ~ )\r\nbeing used to escape the closing triple curly braces. This is to do nowiki nesting in this\r\nwiki which doesn\'t follow Creole 1.0 yet (closing triple curly braces should be indented\r\nby one space).\r\n\r\nYou can also use it inline nowiki {{{ in a sentence }}} like this.\r\n\r\n!!! Escapes \r\nNormal Link: http://wikicreole.org/ - now same link, but escaped: ~http://wikicreole.org/ \r\n\r\nNormal asterisks: ~**not bold~**\r\n\r\na tilde alone: ~\r\n\r\na tilde escapes itself: ~~xxx\r\n\r\n!! Creole 0.2 \r\n\r\nThis should be a flower with the ALT text "this is a flower" if your wiki supports ALT text on images:\r\n\r\n[{ImagePro src=\'Red-Flower.jpg\' caption=\'here is a red flower\' }]\r\n\r\n!! Creole 0.4 \r\n\r\nTables are done like this:\r\n\r\n||header col1||header col2\r\n|col1|col2\r\n|you         |can         \r\n|also        |align\\\\ it. \r\n\r\nYou can format an address by simply forcing linebreaks:\r\n\r\nMy contact dates:\\\\\r\nPone: xyz\\\\\r\nFax: +45\\\\\r\nMobile: abc\r\n\r\n!! Creole 0.5 \r\n\r\n|| Header title               || Another header title     \r\n| {{{ //not italic text// }}} | {{{ **not bold text** }}} \r\n| \'\'italic text\'\'             | __  bold text __          \r\n\r\n!! Creole 1.0 \r\n\r\nIf interwiki links are setup in your wiki, this links to the WikiCreole page about Creole 1.0 test cases: [WikiCreole:Creole1.0TestCases].\r\n', 13, 0, u'creole', u'creole', u'The buildin creole markup', 1, 1, 6, u'', u'', '2008-05-13 11:21:23', '2008-05-13 11:27:25', 1, 1, True, True, None, None]
]
