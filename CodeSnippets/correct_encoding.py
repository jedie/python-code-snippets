# encoding:utf-8

"""
    try to correct some mixed encoding problems in a text file (SQL dump)

    HACK!
    
    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
"""

import sys
import codecs
import pprint
import time


print "sys.getdefaultencoding():", sys.getdefaultencoding()
print "sys.stdout.encoding:", sys.stdout.encoding
print "-"*79

SQL_DUMP = "test.sql"

CONVERT_DATA = {
    u'\xc3\xa4': u"ä",
    u'\xc3\u201e': u"Ä",

    u'\xc3\xb6': u"ö",
    u'\xc3\u2013': u"Ö",

    u'\xc3\xbc': u"ü",
    u'\xc3\u0153': u"Ü",

    u'\xc3\u0178': u"ß",

    u'\xc3\xa4\xc3\u0178': u"äß",
    u'\xc3\xb6\xc3\u0178': u"öß",
    u'\xc3\xbc\xc3\u0178': u"üß",

}

SKIP_INFO = {
    "utf-8":(
        u"ä", u"Ä",
        u"ö", u"Ö",
        u"ü", u"Ü",
        u"ß",
        u"üß",
    )
}
#SKIP_INFO = {}


POSSIBLE_CODECS = ("latin-1", "utf-8")



def get_nonascii_chars(content):
    """
    >>> get_nonascii_chars(u'zur\\xc3\\xbcckf\\xc3\\xbchren.')
    [u'\\xc3\\xbc', u'\\xc3\\xbc']
    """
    chars = [u""]
    in_nonascii = False
    for char in content:
        if ord(char) > 127:
            chars[-1] += char
            in_nonascii = True
            continue
        if in_nonascii:
            in_nonascii = False
            chars.append(u"")
    if chars[-1] == u"":
        chars = chars[:-1]
    return chars


def correct_encoding(content):
    content = content.split(u" ")
    total_count = len(content)
    print total_count
    for index, part in enumerate(content):
        try:
            part.encode("ascii")
        except UnicodeEncodeError, err:
#            print "Unicode error: %s" % err
#            print repr(part[err.start:err.end]), repr(part)
            pass
        else:
            continue

        chars = get_nonascii_chars(part)
#        print chars

        for char in chars:
            if char not in CONVERT_DATA:
                continue
            new_char = CONVERT_DATA[char]
            print repr(char), "->", new_char
            print repr(part), "->",
            part = part.replace(char, new_char)
            print part

        content[index] = part

    print "%i/%i -> done." % (index, total_count)
    content = " ".join(content)
    return content


def extract_unicode_errors(content, skip_info):

    def is_correct(char, skip_info):
        for codec, chars in skip_info.items():
            try:
                test = char.encode(codec)
            except UnicodeEncodeError:
                continue
            else:
                if test in chars:
                    return True
        return False

    content = content.split(u" ")
    total_count = len(content)
    print total_count
    non_ascii = {}
    for part in content:
        try:
            part.encode("ascii")
        except UnicodeEncodeError, err:
#            print "Unicode error: %s" % err
#            print repr(part[err.start:err.end]), repr(part)
            pass
        else:
            continue

        chars = get_nonascii_chars(part)
#        print chars

        for char in chars:
            if is_correct(char, skip_info):
                continue

            if char not in non_ascii:
                non_ascii[char] = [part]
            else:
                if part not in non_ascii[char]:
                    non_ascii[char].append(part)

    return non_ascii


def display_unicode_errors(non_ascii_data):
    for char, parts in non_ascii_data.items():
        print repr(char),

        if char in CONVERT_DATA:
            print u"*** %s ***" % CONVERT_DATA[char]
            for part in parts[:3]:
                part = part.replace(char, CONVERT_DATA[char])
                print "\t", part
        else:
            for part in parts[:3]:
                print "\t", part


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
#    sys.exit()

    with open(SQL_DUMP, "rb") as f:
        content = f.read()

    non_ascii_data = extract_unicode_errors(content, SKIP_INFO)
    display_unicode_errors(non_ascii_data)
#    sys.exit()

    content = correct_encoding(content)

    print "write...",
    with open(SQL_DUMP + "2", "wb") as f:
        f.write(content)

    print "done"

