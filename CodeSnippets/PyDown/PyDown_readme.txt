
h5. Download von PyDown:

* Sourcen Online einsehen:
** http://pylucid.python-hosting.com/browser/CodeSnippets/PyDown/
* Download via "SVN":http://de.wikipedia.org/wiki/Subversion_%28Software%29 mit:
** svn export http://svn.pylucid.python-hosting.com/CodeSnippets/PyDown

Es werden folgende Module benötigt, diese sind bei einem SVN checkout/export
automatisch mit dabei!

* "Colubrid":http://wsgiarea.pocoo.org/colubrid/ WSGI Toolkit
* "Jinja":http://wsgiarea.pocoo.org/jinja/ Template Engine
* WSGI Server (fastCGI) from "flup":http://www.saddi.com/software/flup/

Zusätzlich zu installierende Module:

* "PySQLite":http://www.initd.org/tracker/pysqlite/


h5. Installation:

* PyDown config
** Datei "./PyDown_config_Example.py" nach "PyDown_config.py" umbenennen
** Config anpassen
* Template
** Datei "./Browser_template_Example.html" umbennennen nach "Browser_template.html"
** Evtl. anpassen



h5. Webserver Handler:

Der Webserver (z.B. Apache) kann folgende Handler benutzten, die die
Web-Applikation "starten" bzw. mit der PyDown "aufgerufen" wird:

* als pure CGI: ./PyDown.cgi
* mit fastCGI: ./PyDown.fcg