# Create your views here.

from django.http import HttpResponse
from django.db import connection

#~ from PyLucid.db import DBwrapper
import os, cgi

HTML_head = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>PyLucid Setup</title>
<meta http-equiv="expires"      content="0" />
<meta name="robots"             content="noindex,nofollow" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
html, body {
    padding: 30px;
    background-color: #FFFFEE;
}
body {
    font-family: tahoma, arial, sans-serif;
    color: #000000;
    font-size: 0.9em;
    background-color: #FFFFDB;
    margin: 30px;
    border: 3px solid #C9C573;
}
form * {
  vertical-align:middle;
}
input {
    border: 1px solid #C9C573;
    margin: 0.4em;
}
pre {
    background-color: #FFFFFF;
    padding: 1em;
}
#menu li, #menu li a {
    list-style-type: none;
    padding: 0.3em;
}
#menu h4 {
    margin: 0px;
}
a {
    color:#0BE;
    padding: 0.1em;
}
a:hover {
    color:#000000;
    background-color: #F4F4D2;
}
</style>
%(addCodeTag)s
</head>
<body>
<h3>%(info)s - Setup @ <a href="%(base_url)s">%(base_url)s</a></h3>
<lucidTag:page_msg/>
"""
HTML_bottom = """
<hr />
<small>
<p>Rendertime: <lucidTag:script_duration/></p>
</small>
</body></html>"""

from PyLucid.db.models import Pages
import sys, cgi, inspect

class Install:
    def inspectdb(request):
        """
        django.core.management.instectdb
        """
        response = HttpResponse()
        response.write(HTML_head)
        response.write("<h1>inspectdb</h1>")
        response.write("<pre>")

        from django.core.management import inspectdb

        for line in inspectdb():
            response.write("%s\n" % line)

        response.write("</pre>")
        response.write(HTML_bottom)
        return response

    def table_info

def index(request, url_info):
    response = HttpResponse()
    response.write(HTML_head)
    response.write("<h1>menu</h1>")
    response.write("<p>url: [%s]</p>" % url_info)
    response.write("<pre>")

    method_list = inspect.getmembers(Install, inspect.ismethod)
    for method_name in method_list:
        method_name = method_name[0]
        response.write(repr(
            method_name
        ))

    response.write("</pre>")
    response.write(HTML_bottom)
    return response



    response.write(cgi.escape(repr(dir(Pages))))
    response.write("\n")
    response.write(cgi.escape(repr(Pages.objects)))
    response.write("\n")
    response.write(cgi.escape(repr(Pages)))
    response.write("\n")

    for entry in Pages.objects.all():
        response.write(cgi.escape(repr(dir(entry))))
        response.write("\n")
        response.write(cgi.escape(repr(entry)))
        response.write(cgi.escape(entry.title))
        response.write("\n")

    page = Pages.objects.get(id__exact=1)
    response.write("title id=1: %s" % cgi.escape(page.title))

    old = sys.stdout
    sys.stdout = response
    help(Pages)
    sys.stdout = old



