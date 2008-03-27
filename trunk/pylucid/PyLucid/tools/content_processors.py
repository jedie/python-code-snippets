#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid content processors
    ~~~~~~~~~

    - apply a markup to a content
    - render a django template

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

import warnings

from django.conf import settings
from django.template import Template, Context
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str, force_unicode

from PyLucid.system.response import SimpleStringIO
from PyLucid.models import MARKUPS

# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./PyLucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('PyLucid.template_addons')


def apply_markup(content, context, markup_no):
    """
    appy to the content the given markup
    The Markups names are from the _install Dump:
        ./PyLucid/db_dump_datadir/PyLucid_markup.py
    """
    page_msg = context["page_msg"]

    if markup_no == 2: # textile
        from PyLucid.system.tinyTextile import TinyTextileParser
        out_obj = SimpleStringIO()
        markup_parser = TinyTextileParser(out_obj, context)
        markup_parser.parse(content)
        content = out_obj.getvalue()
    elif markup_no == 3: #Textile (original)
        try:
            import textile
        except ImportError:
            page_msg(
                "Markup error: The Python textile library isn't installed."
                " Download: http://cheeseshop.python.org/pypi/textile"
            )
        else:
            content = force_unicode(textile.textile(
                smart_str(content),
                encoding=settings.DEFAULT_CHARSET,
                output=settings.DEFAULT_CHARSET
            ))
    elif markup_no == 4: # Markdown
        try:
            import markdown
        except ImportError:
            page_msg(
                "Markup error: The Python markdown library isn't installed."
                " Download: http://sourceforge.net/projects/python-markdown/"
            )
        else:
            # unicode support only in markdown v1.7 or above.
            # version_info exist only in markdown v1.6.2rc-2 or above.
            if getattr(markdown, "version_info", None) < (1,7):
                content = force_unicode(markdown.markdown(smart_str(content)))
            else:
                content = markdown.markdown(content)
    elif markup_no == 5: # ReStructuredText
        try:
            from docutils.core import publish_parts
        except ImportError:
            page_msg(
                "Markup error: The Python docutils library isn't installed."
                " Download: http://docutils.sourceforge.net/"
            )
        else:
            docutils_settings = getattr(
                settings, "RESTRUCTUREDTEXT_FILTER_SETTINGS", {}
            )
            parts = publish_parts(
                source=content, writer_name="html4css1",
                settings_overrides=docutils_settings
            )
            content = parts["fragment"]

    return mark_safe(content) # turn djngo auto-escaping off


def render_string_template(content, context, autoescape=True):
    """
    Render a template.
    """
    context2 = Context(context, autoescape)
    template = Template(content)
    html = template.render(context2)
    return html






def redirect_warnings(out_obj):
    """
    Redirect every "warning" messages into the out_obj.
    """
#    old_showwarning = warnings.showwarning
    def showwarning(message, category, filename, lineno):
        msg = unicode(message)
        if settings.DEBUG:
            filename = u"..." + filename[-30:]
            msg += u" (%s - line %s)" % (filename, lineno)
        out_obj.write(msg)

    warnings.showwarning = showwarning



