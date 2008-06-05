#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    Small Python SVN tool
    ~~~~~~~~~~~~~~~~~~~~~

    sync svn:keywords with the keywords found in the sourcecode.

    Last commit info:
    ----------------------------------
    $LastChangedDate$
    $Rev$
    $Author$
    $HeadURL$

    Created by Jens Diemer

    :copyleft: 2007-2008 by Jens Diemer.
    :license: GNU GPL v3 or above.
"""

import os, sys, re, fnmatch

try:
    import pysvn
except ImportError, e:
    print "Import Error: ", e
    print "You must install pysvn from:"
    print "http://pysvn.tigris.org"
    print "or use: 'sudo aptitude install python-svn' ;)"
    sys.exit()


#_____________________________________________________________________________
# settings:

class Config(object):
    # Path to the SVN repo:
    repository = "."

#    simulation = False
    simulation = True

    # Dateien die keine svn:keywords haben dürfen, ist in den svn:keywords dennoch
    # welche drin, werden die gelöscht:
    no_keyword_file_ext = (".zip",)

    # Dateien mit der Endung, werden komplett ausgelassen:
    skip_file_ext = (".pyc",)

    # Verzeichnisse die ausgelassen werden sollen. (Relativ zum aktuellen Verz.)
    # wird mit .startwith() verglichen!
    skip_dirs = ()

    # Nur diese keywords werden als svn:keywords eingetragen:
    allowed_keywords = set([
        "LastChangedDate", "LastChangedRevision", "LastChangedBy", "HeadURL",
        "Id", "Rev", "Author"
    ])

    # Properties die in jeder Datei gesetzt werden sollen:
    basic_properties = (
        {
            "fnmatches": ("*.py",),
            "properties": (["svn:eol-style", "LF"],),
        },
    )

#_____________________________________________________________________________


client = pysvn.Client()

# Hier ist $ durch \x24 maskiert, damit das Skript nicht die re findet!
re_keywords = re.compile(r"\x24(.*?):(.*?)\x24")

# Ein kleiner Test für die re:
assert re_keywords.findall(u"jau\u0024Test:OK\u0024jup") == [(u'Test', u'OK')]


#_____________________________________________________________________________

def cleanup(config):
    print "SVN cleanup...",
    client.cleanup(config.repository)
    print "OK"

#_____________________________________________________________________________


def print_status(config):
    """
    shows the SVN status
    """
    def print_list(changes, status):
        print "%s files:" % status
        wc_status = getattr(pysvn.wc_status_kind, status)
        count = 0
        for f in changes:
            if f.text_status != wc_status:
                continue
            count +=1
            print "    ", f.path
        print "  %s file(s)" % count

    print "SVN status:"
    print "- "*39
    changes = client.status(config.repository)

    for status in ("added","deleted","modified","conflicted","unversioned"):
        print_list(changes, status)

    print "- "*39

#_____________________________________________________________________________

def walk(repo_path, skip_file_ext, skip_dirs):
    """
    os.walk durch das repro-Verz.
    Liefert den absoluten Pfad als generator zurí¤«
    """
    def test_skip_dirs(dir, skip_dirs):
        for skip_dir in skip_dirs:
            if dir.startswith(skip_dir):
                return False
        return True

    for dir,_,files in os.walk(repo_path):
        if ("/.svn" in dir) or ("\\.svn" in dir):
            # Versteckte .svn Verzeichnisse auslassen
            continue

        if test_skip_dirs(dir, skip_dirs) != True:
            continue

        for fn in files:
            ext = os.path.splitext(fn)[1]
            if ext in skip_file_ext:
                continue
            abs_path = os.path.join(dir, fn)
            yield abs_path

#_____________________________________________________________________________

def get_file_keywords(fn):
    """
    Fischt aus dem DateiInhalt vorhandene keywords per re raus
    """
    f = file(fn, "r")
    content = f.read()
    f.close()

    keywords = re_keywords.findall(content)
    if keywords == []:
        return set()

    return set([i[0] for i in keywords])

def get_svn_keywords(proplist):
    """
    Liefert eine set() der vorhanden svn:keywords zurück.
    proplist = pysvn.Client().proplist(filename)
    """
    try:
        props = proplist[0][1]["svn:keywords"]
    except (IndexError, KeyError):
        # Hat keine keywords
        return set()
    else:
        return set(props.split(" "))

#_____________________________________________________________________________

def delete_svn_keywords(filename, proplist):
    """
    Löscht aus den svn-properties den Eintrag "svn:keywords", wenn vorhanden.
    """
    svn_keywords = get_svn_keywords(proplist)
    if len(svn_keywords) == 0:
        # Hat keine Keywords die man löschen könnte
        print "File has no svn:keywords, OK"
        return

    print ">>>", svn_keywords
    print "Delete svn_keywords"

    client.propdel("svn:keywords", filename)

def set_svn_keywords(filename, keywords, simulation=True):
    """
    Setzt svn:keywords
    """
    keywords = " ".join(keywords)
    print ">>> set svn_keywords to:", keywords
    if simulation:
        print "config.simulation on, no change made."
        return

    client.propset("svn:keywords", keywords, filename)

def convert_newlines(filename):
    """
    Konvertiert Zeilenenden zu "\n"
    """
    print "Converting newlines...",
    f = file(filename, "rU")
    content = f.read()
    f.close()

    old_filename = filename + ".old"
    try:
        os.rename(filename, old_filename)
    except Exception, e:
        print "\n>>>Error backup file:", e
        return

    try:
        f = file(filename, "wb")
        f.write(content)
        f.close()
    except Exception, e:
        print "\n>>>Error writing:", e
        try:
            os.remove(filename)
        except:
            pass
        try:
            os.rename(old_filename, filename)
        except:
            pass
        return
    else:
        os.remove(old_filename)

    print "OK"

def set_basic_properties(filename, proplist, basic_properties):
    """
    Setzten der properties, die immer vorhanden sein sollen.
    """
    def filenamematch(filename, fnmatches):
        for match in fnmatches:
            if fnmatch.fnmatch(filename, match) == True:
                return True
        return False

    for prop in basic_properties:
        if not filenamematch(filename, prop["fnmatches"]):
            continue

        for prop in prop["properties"]:
            prop_name, prop_value = prop

            try:
                props = proplist[0][1]#["svn:keywords"]
            except (IndexError, KeyError):
                pass
            else:
                if prop_name in props and props[prop_name] == prop_value:
                    # Der aktuelle basic_property Eintrag existiert schon
                    continue

            print "set basic svn property:", prop,
            try:
                client.propset(prop_name, prop_value, filename)
            except pysvn._pysvn.ClientError, e:
                print "\n> Error setting svn property '%s' to '%s':" % (
                    prop_name, prop_value
                )
                print ">", e

                if "has inconsistent newlines" in str(e):
                    # In der Datei gibt es andere Zeilenenden -> konvertieren
                    convert_newlines(filename)
                    try:
                        client.propset(prop_name, prop_value, filename)
                    except Exception, e:
                        print ">>> Error:", e

                continue
            else:
                print "OK"

#_____________________________________________________________________________

def sync_keywords(config):
    """
    syncronisiert keywords aus allen Dateien.
    """
    for fn in walk(config.repository, config.skip_file_ext, config.skip_dirs):
        try:
            svn_entry = client.info(fn)
        except pysvn._pysvn.ClientError, e:
            if "is not a working copy" in str(e):
                # ist nicht in config.repository
                pass
            else:
                print ">>> Error:", e
            continue
        else:
            if svn_entry == None:
                # Die Datei ist nicht im config.repository
                continue

        print "-"*40
        print fn

        proplist = client.proplist(fn)

        ext = os.path.splitext(fn)[1]
        if ext in config.no_keyword_file_ext:
            # Diese Datei sollte keine Keywords haben!
            delete_svn_keywords(fn, proplist)
            continue

        set_basic_properties(fn, proplist, config.basic_properties)

        # svn:keywords aus in der Datei mit re suchen:
        file_keywords = get_file_keywords(fn)

        if not file_keywords.issubset(config.allowed_keywords):
            print ">>>Error!"
            not_allowed = file_keywords.difference(config.allowed_keywords)
            print ">Found not allowed keyword in file:", ", ".join(not_allowed)
            file_keywords = file_keywords.intersection(config.allowed_keywords)
            print ">I used only this keywords:", ", ".join(file_keywords)

        # Die aktuell gesetzten svn:keywords ermitteln:
        svn_keywords = get_svn_keywords(proplist)

        print "keywords in file..: >%s<" % " ".join(sorted(file_keywords))
        print "svn:keywords......: >%s<" % " ".join(sorted(svn_keywords))

        if file_keywords != svn_keywords:
            print "keywords are different -> change it:"
            if len(file_keywords) == 0:
                delete_svn_keywords(fn, proplist)
            else:
                set_svn_keywords(fn, list(file_keywords), config.simulation)
        else:
            print "keywords are the same, ok"


#_____________________________________________________________________________


if __name__ == "__main__":
    #~ cleanup(Config)
    sync_keywords(Config)
    #~ print_status(Config)