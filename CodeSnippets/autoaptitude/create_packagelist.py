#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    autoaptitude
    ~~~~~~~~~~~~

    Creates a list for autoaptitude.sh

    idea from:
        http://ubuntuforums.org/showthread.php?t=442974

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import os, sys, time, subprocess, datetime
from pprint import pprint


APTITUDE = "/usr/bin/aptitude"
ENVIRON = {"LC_LANG":"C"} # Alles auf englisch ausgeben

#~ subprocess.Popen(
    #~ [APTITUDE, "--help"],
    #~ env=ENVIRON,
#~ )
#~ sys.exit()

TEMP_FILENAME = "packagelist.tmp"
PACKAGE_FILE = "packagelist.txt"
SAVE_APTITUDE = "show ~i >%s" % TEMP_FILENAME

START_packet_NAME = "Package: "
START_SECTION = "Section: "
START_AUTOMARK = "Automatically installed: "
AUTOMARK_MAP = {"yes": True, "no": False}



def create_temp_file():
    # TODO: Can we use the piped output directly?
    cmd = " ".join([APTITUDE, SAVE_APTITUDE])
    print "run:", cmd
    p = subprocess.Popen(cmd, shell=True, env=ENVIRON)
    while p.poll() == None:
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()
    print "\nOK"


def clean_section_name(section_name):
    if "/" in section_name:
        #~ print section_name
        return section_name.rsplit("/", 1)[1]
    else:
        return section_name


def get_automark_data(f):
    automark_data = {}

    packet_name = None
    section = None
    automark = None

    count = 0
    for line in f:
        line = line.strip()
        #~ print ">>>", line

        if line.startswith(START_packet_NAME):
            packet_name = line[len(START_packet_NAME):]
            #~ print "1", packet_name

        elif line.startswith(START_SECTION):
            section = line[len(START_SECTION):]
            #~ print "2", section

        elif line.startswith(START_AUTOMARK):
            automark = line[len(START_AUTOMARK):]
            automark = AUTOMARK_MAP[automark]
            #~ print "3", automark

        if packet_name and section and automark:
            #~ print "4"
            #~ count += 1
            #~ if count>2: break

            section = clean_section_name(section)
            #~ print "packet:", packet_name
            #~ print "Section:", section
            #~ print " -"*40

            if not section in automark_data:
                automark_data[section] = []

            automark_data[section].append(packet_name)

            packet_name = None
            section = None
            automark = None

        elif line == "":
            #~ print "-" * 79
            packet_name = None
            section = None
            automark = None

    return automark_data


def write_package_list(automark_data, filename):
    f = file(filename, "w")
    f.writelines([
        "#" * 79, "\n",
        "# automatic generated with %s" % __file__, "\n",
        "# (%s)" % datetime.datetime.now(), "\n",
        "#" * 79, "\n",
    ])
    for section, packages in sorted(automark_data.iteritems()):
        f.writelines([
            "#" * 20, "\n",
            "# %s" % section, "\n",
            "#" * 20, "\n",
        ])
        packages.sort()
        f.write("\n".join(packages))
        f.write("\n\n")

    f.close()


if __name__ == "__main__":
    #~ os.remove(TEMP_FILENAME)
    if os.path.isfile(TEMP_FILENAME):
        print "Skip aptitude show, use file %s" % TEMP_FILENAME
    else:
        create_temp_file()

    #~ sys.exit()
    print "-"*79

    f = file(TEMP_FILENAME, "r")
    automark_data = get_automark_data(f)
    f.close()

    pprint(automark_data)

    write_package_list(automark_data, PACKAGE_FILE)