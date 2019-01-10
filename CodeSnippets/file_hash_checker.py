#!/usr/bin/env python3

"""
    Simple file hash checker:

        * Compare existing .md5 and .sha256 files
        * Create .md5 and .sha256 files if not exists

    created 10.01.2019 by Jens Diemer
    copyleft 2019 Jens Diemer - GNU GPL v2+

    Sourcecode from:
    https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/file_hash_checker.py
"""

import hashlib
import logging
import sys
from pathlib import Path

logging.basicConfig(
    # level=logging.DEBUG
    level=logging.WARNING
)
log = logging.getLogger(__name__)


SKIP_EXTENSIONS = list(hashlib.algorithms_available)
SKIP_EXTENSIONS += ["%ssum" % name for name in hashlib.algorithms_available]

OWN_FILE_PATH = Path(__file__).resolve()


class HashChecker:
    chunk_size = 5 * 1024
    hash_name = None

    def __init__(self):
        self.hasher = hashlib.new(self.hash_name)

    def check(self, file_path):

        hash_file_path = Path("%s.%s" % (file_path, self.hash_name))

        if hash_file_path.is_file():
            # hash file exists: compare
            return self.compare(file_path, hash_file_path)

        alternative_hash_file_path = Path("%s.%ssum" % (file_path, self.hash_name))
        if alternative_hash_file_path.is_file():
            # hash file exists: compare
            return self.compare(file_path, alternative_hash_file_path)

        return self.create_hash(file_path, hash_file_path)

    def _get_file_hash(self, file_path):
        log.debug("Calculate %s from: %s" % (self.hash_name, file_path))
        with file_path.open("rb") as f:
            while True:
                data = f.read(self.chunk_size)
                if not data:
                    break
                self.hasher.update(data)

        current_hash = self.hasher.hexdigest()
        log.debug("Current hash: %s", current_hash)
        return current_hash

    def compare(self, file_path, hash_file_path):
        log.info("Compare with %s", hash_file_path)

        with hash_file_path.open("r") as f:
            reference_hash = f.readline().split(" ", 1)[0]

        log.debug("Reference hash: %s", reference_hash)

        current_hash = self._get_file_hash(file_path)

        if current_hash == reference_hash:
            print("\t%s: %s -> OK" % (self.hash_name, current_hash))
            return True
        else:
            print(" *** ERROR in file: %s *** " % file_path, file=sys.stderr)
            print("Reference %s from: %s is:" % (self.hash_name, hash_file_path), file=sys.stderr)
            print("\t%s: %s" % (self.hash_name, reference_hash), file=sys.stderr)
            print("Current calculated %s:" % self.hash_name, file=sys.stderr)
            print("\t%s: %s\n" % (self.hash_name, current_hash), file=sys.stderr)
            return False

    def create_hash(self, file_path, hash_file_path):
        print("\tCreate %s" % hash_file_path)

        current_hash = self._get_file_hash(file_path)

        with hash_file_path.open("w") as f:
            f.write("%s  %s" % (current_hash, file_path.name))

        print("\t%s: %s" % (self.hash_name, current_hash))

class Md5Checker(HashChecker):
    hash_name = "md5"


class Sha256Checker(HashChecker):
    hash_name = "sha256"


def check_file_checksum(file_path):
    file_path = file_path.resolve()

    assert file_path.is_file(), "File not found: %s" % file_path

    file_extension = file_path.suffix.lstrip(".")
    if file_extension in SKIP_EXTENSIONS:
        logging.info("Skip: %s", file_path)
        return

    if file_path == OWN_FILE_PATH:
        logging.info("Skip: %s", file_path)
        return

    print("\nCheck: %s" % file_path)

    Md5Checker().check(file_path)
    Sha256Checker().check(file_path)


def check_checksums(path):
    path = Path(path).expanduser().resolve()
    assert path.is_dir(), "Directory not found: %s" % path
    print("\nCheck file hashes in: %s\n" % path)
    for item in path.iterdir():
        if item.is_file():
            check_file_checksum(item)


if __name__ == "__main__":
    check_checksums(path=".")
    # check_checksums(path="/foo/bar")
