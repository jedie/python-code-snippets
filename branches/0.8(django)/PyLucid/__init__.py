
"""
use the undocumented django function to add the "lucidTag" to the tag library.

see ./PyLucid/defaulttags/__init__.py
"""

from django.template import add_to_builtins

add_to_builtins('PyLucid.defaulttags')