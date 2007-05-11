
import os
os.chdir("..") # go into PyLucid App root folder

from django.core import management

from PyLucid import settings

settings.DATABASE_ENGINE = "sqlite3"
settings.DATABASE_NAME = ":memory:"

print "init django, create tables...",
management.setup_environ(settings) # init django
management.syncdb(verbosity=0, interactive=False) # Create Tables
print "OK\n"

#______________________________________________________________________________
# Test:

from PyLucid.models import Plugin, Markup, PagesInternal

plugin = Plugin.objects.create()
print "plugin ID:", plugin.id

markup2 = Markup.objects.create(name="Test Markup")
print markup2, type(markup2)
print "markup2 ID:", markup2.id

markup = Markup.objects.get(name="Test Markup")
print markup, type(markup)
print "markup2 ID:", markup.id

internal_page = PagesInternal.objects.create(
    name = "Test",
    plugin = plugin, # The associated plugin
    markup = markup,

    content_html = "TEST content_html",
    content_js = "TEST content_html",
    content_css = "TEST content_html",
    description = "Test description",
)
print internal_page