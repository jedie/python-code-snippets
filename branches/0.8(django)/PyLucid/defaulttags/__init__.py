
"""
register the PyLucid tags

start from:
    ./PyLucid/tools/content_processors.py
with:
    add_to_builtins('PyLucid.defaulttags')
"""

from django import template
from PyLucid.defaulttags.lucidTag import lucidTag

register = template.Library()
register.tag(lucidTag)