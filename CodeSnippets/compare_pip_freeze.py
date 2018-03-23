#!/usr/bin/env python3

"""
    copyleft 2018 Jens Diemer - GNU GPL v2+
"""

from difflib import Differ
from pathlib import Path

import pip.req
import piptools.sync
import piptools.utils


def parse_requirements(req_files):
    print("parse %s..." % req_files)
    assert isinstance(req_files, (tuple, list))
    for r in req_files:
        assert r.is_file(), "not found: %s" % r

    req_files = [str(r) for r in req_files]

    requirements = piptools.utils.flat_map(
        lambda src: pip.req.parse_requirements(src, session=True),
        req_files
    )
    requirements = piptools.sync.merge(requirements, ignore_conflicts=False) # InstallRequirement instances

    req_names = [r.name.lower() for r in requirements]
    req_names.sort()
    return req_names


def requirements_diff(req1, req2, normalize_editables=False):
    req1 = parse_requirements(req1)
    req2 = parse_requirements(req2)

    d = Differ()
    result = list(d.compare(req1, req2))
    for line in result:
        # print(line)
        if line.startswith("+ "): # only missing
            print(line)


if __name__ == "__main__":
    requirements_diff(
        req1=[Path("requirements/requirements.txt")],
        req2=[Path("20180323-084911_pip_freeze_.txt")],
        normalize_editables=False
    )
