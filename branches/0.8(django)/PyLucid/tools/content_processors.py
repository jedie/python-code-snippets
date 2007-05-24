
from django.template import Template, Context

from PyLucid.system.tinyTextile import TinyTextileParser
from PyLucid.system.response import SimpleStringIO

from django.template import add_to_builtins
# use the undocumented django function to add the "lucidTag" to the tag library.
# see ./PyLucid/defaulttags/__init__.py
add_to_builtins('PyLucid.defaulttags')

def apply_markup(content, markup_object):
    """
    appy to the content the given markup
    """
    markup = markup_object.name
    if markup == "textile":
        out_obj = SimpleStringIO()
        p = TinyTextileParser(out_obj)#, request, response)
        p.parse(content)
        return out_obj.getvalue()
    else:
        return content

def render_template(content, global_context, local_context={}):
#        try:
        t = Template(content)
        c = prepare_context(global_context, local_context)
        html = t.render(c)
#        except Exception, e:
#            html = "[Error, render the django Template '%s': %s]" % (
#                internal_page_name, e
#            )
        return html

def prepare_context(global_context, local_context):
    """
    -transfer objects from the global context into the local dict
    -returns a django context object
    TODO: Should we made a copy from the global context?
    """

    global_context.update(local_context)

    c = Context(global_context)
    return c