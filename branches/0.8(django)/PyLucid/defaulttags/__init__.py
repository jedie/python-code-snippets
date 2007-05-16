
"""
register the PyLucid tag

e.g.: {% lucidTag module_name.method_name key1="value1" key2="value2" %}

registered by
    ./PyLucid/__init__.py
with
    add_to_builtins('PyLucid.defaulttags')
"""

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from PyLucid.system.module_manager import run

from django import template

register = template.Library()


class lucidTagNode(template.Node):
    def __init__(self, module_name, method_name, method_kwargs):
        self.module_name = module_name
        self.method_name = method_name
        self.method_kwargs = method_kwargs

    def __repr__(self):
        return "<lucidTag node>"

    def render(self, context):
        local_response = StringIO.StringIO()
        output = run(
            context, local_response,
            self.module_name, self.method_name, self.method_kwargs
        )
        if isinstance(output, basestring):
            content = output
        else:
            try:
                # StringIO Object
                content = local_response.getvalue()
            except Exception, e:
                msg = (
                    "Error: Wrong output from inline Plugin!"
                    " - It should be write into the response object"
                    " or return a String!"
                    " - But %s.%s has returned: %s (%s)"
                    " - Original Error: %s"
                ) % (
                    self.module_name, self.method_name,
                    repr(output), type(output), e
                )
                raise AssertionError(msg)

        print self.module_name, self.method_name
        print content
        print "---"

        return content


def lucidTag(parser, token):
    """
    {% lucidTag NurEinTag %}
    {% lucidTag EinParameter par1="value1" %}
    {% lucidTag ZweiParameter par1="value1" par2="value2" %}
    """
#    print token.contents

    # split content:
    # e.g.: {% lucidTag ZweiParameter par1="value1" par2="value2" %}
    # module_name = "ZweiParameter"
    # contents = ['par1="value1"', 'par2="value2"']
    contents = token.contents.split()[1:]
    module_name = contents.pop(0)

    if "." in module_name:
        module_name, method_name = module_name.split(".")
    else:
        method_name = "lucidTag"

    # split the args into dicts
    # in..: ['par1="value1"', 'par2="value2"']
    # out.: {'par1': 'value1', 'par2': 'value2'}
    method_kwargs = {}
    for no, arg in enumerate(contents):
        key, value = arg.split("=", 1)
        value = value.strip('"')
        method_kwargs[key] = value

    return lucidTagNode(module_name, method_name, method_kwargs)

lucidTag = register.tag(lucidTag)