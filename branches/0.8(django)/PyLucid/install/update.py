
"""
2. update

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

import sys

import os

from PyLucid.utils import check_pass
from PyLucid.settings import TABLE_PREFIX
from PyLucid.system.response import PyLucidResponse

from django.http import HttpResponse



#______________________________________________________________________________

def update(request, install_pass):
    """
    1. update DB tables from v0.7.2 to django PyLucid v0.8
    """
    check_pass(install_pass)
    
    response = HttpResponse(mimetype="text/plain")
    response.write("\nupdate PyLucid database:\n")

    from django.db import connection
    cursor = connection.cursor()
    
    def display_info(txt):
        response.write("\n\n")
        response.write("%s:\n" % txt)
        response.write("-"*79)
        response.write("\n")
        
    
    def verbose_execute(SQLcommand):
        response.write("%s..." % SQLcommand)
        try:
            cursor.execute(SQLcommand)
        except Exception, e:
            response.write("Error: %s\n" % e)
        else:
            response.write("OK\n")

    display_info("Drop obsolete tables")

    for tablename in ("l10n", "user_group", "log", "session_data"):
        tablename = TABLE_PREFIX + tablename
        SQLcommand = "DROP TABLE %s;" % tablename
        verbose_execute(SQLcommand)
        
    display_info("rename tables")

    tablenames = (
        ("pages",  "page"),
        ("styles", "style"),
        ("templates", "template"),
        ("groups", "group"),
        ("markups", "markup"),
        ("md5users", "md5user"),
        ("plugins", "plugin"),
        ("preferences", "preference"),
        ("styles", "style"),
        ("template_engines", "template_engine"),
        ("templates", "template"),
    )
    for source, destination in tablenames:
        source = TABLE_PREFIX + source
        destination = TABLE_PREFIX + destination

        SQLcommand = "RENAME TABLE %s TO %s;" % (source, destination)
        verbose_execute(SQLcommand)

    response.write("\n\nupdate done. (Please go back)")

    return response

#______________________________________________________________________________

REPLACE_DATA = (
    ("|escapexml ", "|escape "),
)
def _convert_template(content):
    """
    simple replace some tags
    """
    changed = False
    for source, destination in REPLACE_DATA:
        if source in content:
            old_content = content
            content = content.replace(source, destination)
            if old_content != content:
                changed = True

    if changed:
        return content

UNSUPPORTED_TAGS = ("{% recurse ",)
def _display_warnings(response, content):
    """
    Waring if there is some unsupportet tags in the template
    """
    for tag in UNSUPPORTED_TAGS:
        if tag in content:
            response.write("\t - WARNING: unsupportet tag '%s' in Template!\n" % tag)
    
def update_templates(request, install_pass):
    """
    2. convert jinja to django templates
    """
    check_pass(install_pass)

    response = HttpResponse(mimetype="text/plain")
    response.write("convert jinja to django templates:\n")
    
    from PyLucid.tools.Diff import display_plaintext_diff
    from PyLucid.models import PagesInternal
    
    for internal_page in PagesInternal.objects.all():
        name = internal_page.name
        old_content = internal_page.content_html
        
        response.write("\n==================[ %s ]==================\n\n" % name)
        _display_warnings(response, old_content)
        content = _convert_template(old_content)
        if not content:
            response.write("\t - Nothing to change.\n")
            continue
        
        response.write("\t - changed!\n\nthe diff:\n")
        display_plaintext_diff(old_content, content, response)
        
        internal_page.content_html = content
        internal_page.save()
        response.write("\t - updated and saved.\n")
        
        response.write("\n\n")
        
        
    return response
        
