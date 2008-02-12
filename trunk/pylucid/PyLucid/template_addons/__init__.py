
"""
    PyLucid defaulttags
    ~~~~~~~~~~~~~~~~~~~

    - register the PyLucid tags
    - put the i18n tags into the builtins, so every internal pages/template can use
      i18n without a explicit {% load i18n %}

    start from:
        ./PyLucid/tools/content_processors.py
    with:
        add_to_builtins('PyLucid.defaulttags')

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


from django.template import Library
from django.templatetags.i18n import do_translate, do_block_translate

from PyLucid.template_addons.lucidTag import lucidTag
from PyLucid.template_addons.filters import chmod_symbol, get_oct

register = Library()

register.tag(lucidTag)
register.filter(chmod_symbol)
register.filter(get_oct)

# register only used tags:
#register.tag('get_available_languages', do_get_available_languages)
#register.tag('get_current_language', do_get_current_language)
#register.tag('get_current_language_bidi', do_get_current_language_bidi)
register.tag('trans', do_translate)
register.tag('blocktrans', do_block_translate)

