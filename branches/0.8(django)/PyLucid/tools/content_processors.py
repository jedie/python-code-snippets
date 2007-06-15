
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

from django.template import Template, Context

from PyLucid.system.tinyTextile import TinyTextileParser
from PyLucid.system.response import SimpleStringIO


# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./PyLucid/defaulttags/__init__.py
from django.template import add_to_builtins
add_to_builtins('PyLucid.defaulttags')


def apply_markup(content, context, markup_object):
    """
    appy to the content the given markup
    """
    markup = markup_object.name
    if markup == "textile":
        out_obj = SimpleStringIO()
        markup_parser = TinyTextileParser(out_obj, context)
        markup_parser.parse(content)
        return out_obj.getvalue()
    else:
        return content


def render_string_template(template, context):
    """
    Render a string-template with the given context
    """
    c = Context(context)
    t = Template(template)
    html = t.render(c)
    return html

def render_template(content, global_context, local_context={}):
    """
    Render a template.
    1. put all local context items in the global context
    2. render with the merged context
    Note:
    - The local_context are content for a internal page.
    - We merged the local- and global-context together, so every internal
    page can display something from the global context, like page name...
    """
    global_context.update(local_context)

    html = render_string_template(content, global_context)

    return html
