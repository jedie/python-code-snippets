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
    hash = sha.new(salt + txt).hexdigest()
    salt_hash = "sha$%s$%s" % (salt, hash)
    return salt_hash

def check_salt_hash(txt, salt_hash):
    """
    compare txt with the salt-hash.
    returns a bool.
    """
    type, salt, hash = salt_hash.split("$")
    assert type == "sha"
    test_hash = sha.new(salt + txt).hexdigest()
    return hash == test_hash

def salt_hash_to_dict(salt_hash):
    type, salt, hash = salt_hash.split("$")
    return {
        "type": type,
        "salt": salt,
        "hash": hash
    }


if __name__ == "__main__":
    test_txt = "12345678test"
    salt_hash = make_salt_hash(test_txt)
    print "salt_hash....................:", salt_hash
    check = check_salt_hash(test_txt, salt_hash)
    print "check........................:", check
    assert check == True
    check2 = check_salt_hash("wrong!", salt_hash)
    assert check2 == False

    print

    salt_hash = "sha$3863$d894911422c320e2f656f08fe32c13219537221d"
    print salt_hash
    check = salt_hash_to_dict(salt_hash)
    print check
    assert check == {
        'type': 'sha',
        'salt': '3863',
        'hash': 'd894911422c320e2f656f08fe32c13219537221d'
    }
