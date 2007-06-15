"""
    PyLucid.tools.crypt
    ~~~~~~~~~~~~~~~~~~~

    Two usefull hash functions.
    Used in the _install section for login.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer.
    :license: GNU GPL, see LICENSE for more details
"""


import sha, random

SALT_LEN = 6


def make_salt_hash(txt):
    """
    make from the given string a hash with a salt value
    """
    salt = sha.new(str(random.random())).hexdigest()[:SALT_LEN]
    sha_hash = sha.new(salt + txt).hexdigest()
    return salt + sha_hash

def check_salt_hash(txt, hash_string):
    """
    compare txt with the salt-hash.
    returns a bool.
    """
    salt = hash_string[:SALT_LEN]
    sha_hash = hash_string[SALT_LEN:]
    test_hash = sha.new(salt + txt).hexdigest()
    return sha_hash == test_hash

if __name__ == "__main__":
    test_txt = "12345678test"
    salt_hash = make_salt_hash(test_txt)
    print "salt_hash....................:", salt_hash
    check = check_salt_hash(test_txt, salt_hash)
    print "check........................:", check
    assert check == True
    check2 = check_salt_hash("wrong!", salt_hash)
    assert check2 == False
