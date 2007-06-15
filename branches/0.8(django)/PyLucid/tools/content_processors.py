
from django.template import Template, Context

from PyLucid.system.tinyTextile import TinyTextileParser
from PyLucid.system.response import SimpleStringIO

from django.template import add_to_builtins
# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./PyLucid/defaulttags/__init__.py
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

def render_template(content, global_context, local_context={}):
    template = Template(content)
    context = prepare_context(global_context, local_context)
    html = template.render(context)
    return html

def prepare_context(global_context, local_context):
    """
    -transfer objects from the global context into the local dict
    -returns a django context object
    TODO: Should we made a copy from the global context?
    """

    global_context.update(local_context)

    ctx = Context(global_context)
    return ctx
