"""
    PyLucid.tools.shortcuts
    ~~~~~~~~~~~~~~~~~~~~~~~

    Some usefull routines around `PyLucid.models.Page.shortcut`.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import string
ALLOW_CHARS = string.ascii_letters + string.digits + "_"

def makeUnique(item_name, name_list):
    """
    returns a unique shortcut.
    - delete all non-ALLOW_CHARS characters.
    - if the shotcut already exists in name_list -> add a sequential number
    Note:
    Not only used for making page shortcuts unique.
    Also used in PyLucid.defaulttags.lucidTag.lucidTagNode._add_unique_div()
    """
    # delete all non-ALLOW_CHARS characters and separate in parts
    parts = [""]
    for char in item_name:
        if not char in ALLOW_CHARS:
            parts.append("")
        else:
            parts[-1] += char

    # Upcase the first character of every part
    parts = [i[0].upper() + i[1:] for i in parts if i!=""]
    item_name = "".join(parts)

    if item_name == "":
        # No shortcut? That won't work.
        item_name = "1"

    # make double shortcut unique (add a new free sequential number)
    if item_name in name_list:
        for i in xrange(1, 1000):
            testname = "%s%i" % (item_name, i)
            if testname not in name_list:
                item_name = testname
                break

    return item_name

def getUniqueShortcut(shortcut, exclude_shortcut=None):
    from PyLucid.models import Page
    shortcuts = Page.objects.values("shortcut")
#    print "exclude shortcut: '%s'" % exclude_shortcut
    if exclude_shortcut != None:
        shortcuts = shortcuts.exclude(shortcut=exclude_shortcut)
    existing_shortcuts = [i["shortcut"] for i in shortcuts]
#    print "existing_shortcuts:", existing_shortcuts
    return makeUnique(shortcut, existing_shortcuts)

if __name__ == "__main__":
    name_list = ["GibtsSchon", "UndAuchDas", "UndAuchDas1", "UndAuchDas2"]
    print name_list
    print "-"*80
    print makeUnique("Ich bin neu!", name_list)
    print makeUnique("gibts schon", name_list)
    print makeUnique("#und!auch(das)", name_list)
