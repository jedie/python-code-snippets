#!/usr/bin/python
# coding: ISO-8859-1

"""
    shared utilities
    ~~~~~~~~~~~~~~~~

    :copyleft: 2012-2013 by htFX.de - Jens Diemer
    :license: GNU GPL v3 or above
"""

import sys


stdout_encoding = sys.stdout.encoding or sys.getfilesystemencoding()


def out(*txt):
    for i in txt:
        assert isinstance(i, unicode), "%s is not unicode!" % repr(i)
    txt = u" ".join([i for i in txt])
    print txt.encode(stdout_encoding)


def human_filesize(i):
    """
    'human-readable' file size (i.e. 13 KB, 4.1 MB, 102 bytes, etc).
    """
    bytes = float(i)
    if bytes < 1024:
        return u"%d Byte%s" % (bytes, bytes != 1 and u's' or u'')
    if bytes < 1024 * 1024:
        return u"%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return u"%.1f MB" % (bytes / (1024 * 1024))
    return u"%.1f GB" % (bytes / (1024 * 1024 * 1024))


def human_timedelta(delta):
    """
    borrowed from Django:
    https://github.com/django/django/blob/master/django/utils/timesince.py
    """
    chunks = (
      (60 * 60 * 24 * 365, u"Jahre"),
      (60 * 60 * 24 * 30, u"Monate"),
      (60 * 60 * 24 * 7, u"Wochen"),
      (60 * 60 * 24, u"Tage"),
      (60 * 60, u"Stunden"),
      (60, u"Minuten")
    )
    since = delta.days * 24 * 60 * 60 + delta.seconds # ignore microseconds
    if since <= 0:
        since = since * -1

    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    s = "%(number)d %(type)s" % {'number': count, 'type': name}
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            s += u", %(number)d %(type)s" % {'number': count2, 'type': name2}
    return s
