#!/usr/bin/python3

"""
    convert "tox -l" to a formatted list for '.travis.yml'

    usage, e.g.:

        ~/python-code-snippets/CodeSnippets$ ./tox2travis.py ~/your/repo/

    Output looks like, e.g.:

        - env: TOXENV=flake8
          python: flake8

        - env: TOXENV=py35-django111
          python: 3.5
        - env: TOXENV=py35-django18
          python: 3.5

        - env: TOXENV=py36-django111
          python: 3.6

        - env: TOXENV=pypy3-django111
          python: pypy3
        - env: TOXENV=pypy3-django18
          python: pypy3
"""


import argparse
import os
import subprocess
import sys
from collections import defaultdict


__author__  = "Jens Diemer"
__license__ = "GNU General Public License v3 or above - https://opensource.org/licenses/gpl-license.php"
__url__     = "http://www.jensdiemer.de"


def verbose_check_output(*args, **kwargs):
    """ 'verbose' version of subprocess.check_output() """
    print("subprocess: %r with %s\n" % (" ".join(args), kwargs))
    try:
        return subprocess.check_output(args, universal_newlines=True, stderr=subprocess.STDOUT, **kwargs)
    except subprocess.CalledProcessError as err:
        print("\n***ERROR:")
        print(err.output)
        raise


def tox2travis(txt):
    """
    >>> txt = 'flake8\\npy35-django18\\npy35-django111\\npypy3-django18\\npypy3-django111\\npy36-django111\\n'
    >>> lines = tox2travis(txt)
    >>> print("\\n".join(lines))
    - env: TOXENV=flake8
    <BLANKLINE>
    - env: TOXENV=py35-django111
      python: 3.5
    - env: TOXENV=py35-django18
      python: 3.5
    <BLANKLINE>
    - env: TOXENV=py36-django111
      python: 3.6
    <BLANKLINE>
    - env: TOXENV=pypy3-django111
      python: pypy3
    - env: TOXENV=pypy3-django18
      python: pypy3
    <BLANKLINE>
    """
    data = defaultdict(set)
    for env_txt in txt.splitlines():
        env_txt = env_txt.strip()
        if not env_txt:
            continue

        py = env_txt.split("-",1)[0]
        # print(py, env_txt)
        data[py].add(env_txt)

    lines = []
    for py, envs in sorted(data.items()):
        if not py.startswith("py"):
            py = None
        elif not py.startswith("pypy"):
            py = py.lstrip("py")
            assert len(py) == 2, "ERROR with: %r" % py
            py = ".".join([*py])

        for env in sorted(envs):
            lines.append("- env: TOXENV=%s" % env)
            if py is not None:
                lines.append("  python: %s" % py)
        lines.append("")
    return lines


if __name__=="__main__":
    import doctest
    print("Doctest:", doctest.testmod(
        # verbose=True
        verbose=False
    ))
    print("source")

    parser = argparse.ArgumentParser(description="Convert 'tox -l' output for .travis.py")
    parser.add_argument('path', action='store', default=".", help='path to tox.ini')
    args = parser.parse_args()
    path = args.path

    if os.path.isfile(path):
        path = os.path.split(path)[0]

    tox_file_path = os.path.join(path, "tox.ini")
    if not os.path.isfile(tox_file_path):
        print("\nERROR: tox.ini not found here: %r\n" % path)
        sys.exit(-1)

    try:
        output = verbose_check_output("tox", "-l", cwd=path)
    except FileNotFoundError as err:
        print("ERROR: calling 'tox': %s" % err)
        print("(Maybe tox not installed or virtualenv not activates?!?)\n")
        sys.exit(-1)

    lines = tox2travis(output)

    print(" #")
    print(" # Generated from 'tox -l' with tox2travis.py")
    print(" # https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/tox2travis.py")
    print(" #")
    print("\n".join(lines))
