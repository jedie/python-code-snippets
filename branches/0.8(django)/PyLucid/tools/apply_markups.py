

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from PyLucid.system.tinyTextile import TinyTextileParser

def apply_markup(content, markup_object):

    markup = markup_object.name
    if markup == "textile":
        out_obj = StringIO.StringIO()
        p = TinyTextileParser(out_obj)#, request, response)
        p.parse(content)
        return out_obj.getvalue()
    else:
        return content
