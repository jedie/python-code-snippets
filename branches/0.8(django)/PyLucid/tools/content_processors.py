
import cStringIO as StringIO

from django.template import Template, Context

from PyLucid.system.tinyTextile import TinyTextileParser


CONTEXT_TRANSFER_KEYS = ("request", "page_msg", "URLs")


def apply_markup(content, markup_object):
    """
    appy to the content the given markup
    """
    markup = markup_object.name
    if markup == "textile":
        out_obj = StringIO.StringIO()
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
    -transfer some objects from the global context into the local dict
    -returns a django context object
    """
    for key in CONTEXT_TRANSFER_KEYS:
        local_context[key] = global_context[key]

    c = Context(local_context)
    return c