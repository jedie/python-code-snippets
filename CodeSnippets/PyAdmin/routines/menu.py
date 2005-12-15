#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-


__version__ = "0.0.2"



## Revisions-History
# v0.0.2
#   - Zeitanzeige am Ende der Seite
# v0.0.1
#   - Erste Version



import os, locale, time

starttime = time.time()


path = os.path.split( __file__ )[0]
#~ css_path = os.path.join( os.environ["docroot"], "css" )
css_path = "/css"

print "Content-Type: text/html\n\n"

head = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset="%(charset)s" />
<title>%(title)s</title>
<link href="/css/base.css" rel="stylesheet" type="text/css" />
%(css)s
%(headings)s</head>
%(body)s
%(menu)s
<div id="content">'''

html_menu = '''<div id="menu">
    <h1>PyAdmin</h1>
    <ul>
        <li><a href="SystemInfo%(SystemInfo_args)s">SystemInfo</a></li>
        <li><a href="console%(console_args)s">Console</a></li>
        <li><a href="FileBrowser%(FileBrowser_args)s">FileBrowser</a></li>
        <li><a href="editor%(Editor_args)s">Editor</a></li>
    </ul>
</div>'''


class cfg:
    "Klasse um Daten der Module optional veränderbar zu machen"
    css                 = ""
    title               = "PyAdmin"
    headings            = ""
    body                = "<body>"
    SystemInfo_args     = ""
    console_args        = ""
    FileBrowser_args    = ""
    Editor_args         = ""


footer = '''</div>%(info)s</body></html>'''

cssLink = '<link href="%s" rel="stylesheet" type="text/css" />\n'


class Menu:
    def __init__( self ):
        #~ self.ModulInfo = ModuleInfo
        #~ self.set_compression()
        self.print_head()

    def set_compression( self ):
        "Komprimierte übertragung einschalten"
        MyOut = CompressedOut.AutoCompressedOut()
        print "<!-- Out-Compression:'%s' -->" % MyOut.get_mode()

    def print_head( self ):

        cssTags = ""
        if cfg.css != "":
            # Optionale CSS-Datei für das aktuelle Modul
            cssTags += cssLink % os.path.join( css_path, cfg.css )

        print head % {
            "charset"       : locale.getdefaultlocale()[1],
            "title"         : cfg.title + "@" + " ".join( os.uname() ),
            "css"           : cssTags,
            "headings"      : cfg.headings,
            "body"          : cfg.body,
            "menu"          : self.get_menu()
            }

    def get_menu( self ):
        return html_menu % {
            "SystemInfo_args"   : cfg.SystemInfo_args,
            "console_args"      : cfg.console_args,
            "FileBrowser_args"  : cfg.FileBrowser_args,
            "Editor_args"       : cfg.Editor_args
            }


def print_footer():
    #~ print
    print footer % {
        "info": '<div id="FooterInfo">executed in %.2f sec.</div>' % ( time.time() - starttime )
        }


if __name__ == "__main__":
    Menu()

