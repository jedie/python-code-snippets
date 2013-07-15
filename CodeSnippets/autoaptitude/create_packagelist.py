#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    autoaptitude
    ~~~~~~~~~~~~

    Creates a list for autoaptitude.sh

    idea from:
        http://ubuntuforums.org/showthread.php?t=442974

    :copyleft: 2008-2013 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


from pprint import pprint
import collections
import datetime
import os
import re
import subprocess
import sys
import time


# VERBOSE = 0
VERBOSE = 1
# VERBOSE = 2
# VERBOSE = 3

APTITUDE = "/usr/bin/aptitude"
ENVIRON = {"LC_LANG":"C"}  # Alles auf englisch ausgeben

# ~ subprocess.Popen(
    # ~ [APTITUDE, "--help"],
    # ~ env=ENVIRON,
# ~ )
# ~ sys.exit()


TEMP_FILENAME = "packagelist.tmp"
PACKAGE_FILE = "packagelist_%s_%s.txt" % (
    os.uname()[1],
    datetime.datetime.now().strftime("%Y%m%d"),
)
SAVE_APTITUDE = "show ~i >%s" % TEMP_FILENAME

PACKAGE_NAME_PREFIX = "Package: "
DEPENDS_PREFIX = "Depends: "

GENERIC_PREFIXES = {
    "Section: ": "section",
    "Description: ": "description",
    "Priority: ": "priority",
}

SKIP_PREFIXES = (
    "lib",
)

DEFAULT_PRIORITIE = "NONE"
DEBIAN_PRIORITIES = (
    "required",
    "important",
    "standard",
    "optional",
    "extra",
    DEFAULT_PRIORITIE,
)




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
        if VERBOSE > 3:
            print "raw section name:", section_name
        return section_name.rsplit("/", 1)[1]
    else:
        return section_name


def clean_depends(raw_depends):
    """
    >>> clean_depends("libc6 (>= 2.4), xorg-video-abi-13, xserver-xorg-core (>= 2:1.12.99.901), ")
    ['libc6', 'xorg-video-abi-13', 'xserver-xorg-core']
    
    >>> clean_depends("openjade | openjade1.3 | jade, docbook (>= 3.1) | docbook-xml,")
    ['openjade | openjade1.3 | jade', 'docbook | docbook-xml']
    """
    raw_depends = re.sub("\s*\(.*?\)", "", raw_depends)
    depends = [depend.strip() for depend in raw_depends.split(",") if depend.strip()]
    return depends



def get_automark_data(f):
    package_data = {}

    def add(temp_pkg_data):
        if VERBOSE > 2:
            print " *** ", temp_pkg_data
        temp_pkg_data["section"] = clean_section_name(temp_pkg_data["section"])
        package_name = temp_pkg_data.pop("package_name")
        package_data[package_name] = temp_pkg_data

    temp_pkg_data = {}

    in_depends = False
    raw_depends = ""

    for line in f:
        line = line.strip()
        if VERBOSE > 3:
            print ">>>", line

        if in_depends:  # multiline depends
            if ": " in line:  # next list item -> depends list end
                in_depends = False
                if VERBOSE > 3:
                    print "raw_depends:", raw_depends
                depends = clean_depends(raw_depends)
                if VERBOSE > 3:
                    print "cleaned depends:", depends
                    print
                temp_pkg_data["depends"] = depends
            else:
                # catch multiline depends
                raw_depends += line
                continue

        if line.startswith(PACKAGE_NAME_PREFIX):

            if temp_pkg_data:
                # new package -> add the last package data
                add(temp_pkg_data)

            package_name = line[len(PACKAGE_NAME_PREFIX):]

            if VERBOSE > 2:
                print " *** Package_name:", package_name
            temp_pkg_data = {
                "package_name": package_name,
                "priority": DEFAULT_PRIORITIE,
                "depends": (),
            }
        elif line.startswith(DEPENDS_PREFIX):
            # start multiline depends
            in_depends = True
            raw_depends = line[len(DEPENDS_PREFIX):]
        else:
            for prefix, key in GENERIC_PREFIXES.items():
                if line.startswith(prefix):
                    value = line[len(prefix):]
                    if VERBOSE > 2:
                        print " *** %s: %s" % (key, value)
                    temp_pkg_data[key] = value
                    break

    add(temp_pkg_data)  # Add last packages
    return package_data


def merge_package_data(package_data):
    """
    1774 packages before merge
    removed 1034 packages.
    740 packages after merge
    """



    for package_name, data in package_data.items():
        if VERBOSE > 3:
            print package_name, data
        depends = data["depends"]
        for depend_package_name in depends:
            try:
                if "hits" not in package_data[depend_package_name]:
                    package_data[depend_package_name]["hits"] = 1
                else:
                    package_data[depend_package_name]["hits"] += 1
            except KeyError, err:
                if VERBOSE > 2:
                    print " *** missing package:", err

#     pprint(package_data)

    hitlist = {}
    for package_name, data in package_data.items():
        if not "hits" in data:
            continue
        hits = data["hits"]
        if hits not in hitlist:
            hitlist[hits] = [package_name]
        else:
            hitlist[hits].append(package_name)

    if VERBOSE > 1:
        pprint(hitlist)

    removed = 0
    for hits in sorted(hitlist, reverse=True):
        for package_name in hitlist[hits]:
            if VERBOSE > 2:
                print hits, package_name
            if package_name in package_data:
                for package_name2, data in package_data.items():
                    depends = data["depends"]
                    if package_name in depends:
                        if VERBOSE > 1:
                            print "remove '%s', because is a depend for '%s'" % (
                                package_name, package_name2
                            )
                        del(package_data[package_name])
                        removed += 1
                        break
    if VERBOSE:
        print "removed %i packages." % removed

    return package_data



def write_package_list(package_data, f):
    f.writelines([
        "#" * 79, "\n",
        "# automatic generated with %s" % __file__, "\n",
        "# (%s)" % datetime.datetime.now(), "\n",
        "# %i packages\n" % len(package_data),
        "#" * 79, "\n",
        "\n\n",
    ])

    data = collections.defaultdict(dict)
    for pkg_name, pkg_data in package_data.items():
        priority = pkg_data["priority"]
        section = pkg_data["section"]

        data[priority].setdefault(section, []).append(pkg_name)

#     pprint(data)

    for priority in DEBIAN_PRIORITIES:
        f.writelines([
            "=" * 80, "\n",
            "# %s" % priority, "\n\n\n",
        ])

        priority_data = data[priority]
#         pprint(priority_data)

        for section, packages in sorted(priority_data.items()):
            f.writelines([
                "#" * 20, "\n",
                "# %s" % section, "\n",
                "#" * 20, "\n",
            ])
            for pkg_name in sorted(packages):
                pkg_data = package_data[pkg_name]
                description = pkg_data["description"]
                f.write("%-35s # %s\n" % (pkg_name, description))

            f.write("\n\n")


def _dev_clean(package_data, key_part):
    """
    For development only:
     * Cleans all data if not 'key' in name
     * Deletes all data except 'depends' list
    """
    for pkg_name, pkg_data in package_data.items():
        if not key_part in pkg_name:
            del(package_data[pkg_name])

    for key in package_data.keys(): del(package_data[key]["priority"])
    for key in package_data.keys(): del(package_data[key]["description"])
    for key in package_data.keys(): del(package_data[key]["section"])

    for key in package_data.keys():
        depends = [depend for depend in package_data[key]["depends"] if key_part in depend]
        package_data[key]["depends"] = depends

    return package_data


if __name__ == "__main__":
    import doctest
    print doctest.testmod()
#     sys.exit()

#     os.remove(TEMP_FILENAME)
    if os.path.isfile(TEMP_FILENAME):
        print "Skip aptitude show, use file %s" % TEMP_FILENAME
    else:
        create_temp_file()

    # ~ sys.exit()
    print "-"*79

    f = file(TEMP_FILENAME, "r")
    package_data = get_automark_data(f)
    f.close()
#     sys.exit()

    # XXX: For develomplemt only!
#     pprint(package_data)
#     package_data = _dev_clean(package_data, "python3")
#     pprint(package_data)
#     sys.exit()

    print "%i packages before merge" % len(package_data)

#     VERBOSE = 2
    package_data = merge_package_data(package_data)

    print "%i packages after merge" % len(package_data)
    for key in package_data.keys():
        if "hits" in package_data[key]:
            del(package_data[key]["hits"])
#     pprint(package_data)
#     sys.exit()

    f = file(PACKAGE_FILE, "w")
#     f = sys.stdout
    write_package_list(package_data, f)
    f.close()

    print "\nList file '%s' created." % PACKAGE_FILE
