#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid.tools.crypt
    ~~~~~~~~~~~~~~~~~~~

    -Two usefull salt hash functions. (Used in the _install section for login.)
    -A one-time-pad XOR crypter. (Used for the SHA-JS-Login)

    unittest: ./dev_scripts/unittests/unittest_crypt.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


import sha, random

SALT_LEN = 6
# SHA-1 hexdigest (40) + "sha1" + (2x "$") + salt length
SALT_HASH_LEN = 40 + 4 + 2 + SALT_LEN


class SaltHashError(Exception):
    pass


def make_salt_hash(txt):
    """
    make from the given string a hash with a salt value

    >>> len(make_salt_hash("test")) == SALT_HASH_LEN
    True
    >>> len(make_salt_hash("test").split("$")[1]) == SALT_LEN
    True
    """
    if not isinstance(txt, str):
        raise SaltHashError("Only string allowed!")

    salt = sha.new(str(random.random())).hexdigest()[:SALT_LEN]
    hash = sha.new(salt + txt).hexdigest()
    salt_hash = "sha1$%s$%s" % (salt, hash)
    return salt_hash


def check_salt_hash(txt, salt_hash):
    """
    compare txt with the salt-hash.
    returns a bool.

    TODO: Should we used the django function for this?
        Look at: django.contrib.auth.models.check_password

    >>> salt_hash = make_salt_hash("test")
    >>> check_salt_hash("test", salt_hash)
    """
    if not (isinstance(txt, str) and isinstance(salt_hash, str)):
        raise SaltHashError("Only string allowed!")

    if len(salt_hash) != SALT_HASH_LEN:
        raise SaltHashError("Wrong salt-hash length.")

    try:
        type, salt, hash = salt_hash.split("$")
    except ValueError:
        raise SaltHashError("Wrong salt-hash format.")

    if type != "sha1":
        raise SaltHashError("Unsupported hash method.")

    test_hash = sha.new(salt + txt).hexdigest()

    if hash != test_hash:
        raise SaltHashError("salt-hash compare failed.")


def salt_hash_to_dict(salt_hash):
    """
    >>> salt_hash_to_dict("sha$salt_value$the_SHA_value")
    {'salt': 'salt_value', 'type': 'sha', 'hash': 'the_SHA_value'}
    """
    type, salt, hash = salt_hash.split("$")
    return {
        "type": type,
        "salt": salt,
        "hash": hash
    }


#______________________________________________________________________________


def crypt(txt, key):
    """
    XOR ciphering
    >txt< and >key< should be unicode.

    >>> crypt("1234", "ABCD")
    u'pppp'
    """
    assert len(txt)==len(key), "Error: txt and key must have the same length!"

    crypted = [unichr(ord(t) ^ ord(k)) for t,k in zip(txt, key)]
    return u"".join(crypted)


def encrypt(txt, key):
    """
    XOR ciphering with a SHA salt-hash checksum

    >>> encrypt(u"1234", u"ABCD")[SALT_HASH_LEN:]
    u'pppp'
    """
    if not (isinstance(txt, unicode) and isinstance(key, unicode)):
        raise UnicodeError("Only unicode allowed!")

    salt_hash = make_salt_hash(repr(txt))
    crypted = crypt(txt, key)
    return salt_hash + crypted


def decrypt(crypted, key):
    """
    1. Decrypt a XOR crypted String.
    2. Compare the inserted sSHA salt-hash checksum.

    >>> crypted = encrypt(u"1234", u"ABCD")
    >>> decrypt(crypted, u"ABCD")
    u'1234'
    """
    if not (isinstance(crypted, unicode) and isinstance(key, unicode)):
        raise UnicodeError("Only unicode allowed!")

    salt_hash = str(crypted[:SALT_HASH_LEN])
    crypted = crypted[SALT_HASH_LEN:]
    decrypted = crypt(crypted, key)

    # raised a SaltHashError() if the checksum is wrong:
    check_salt_hash(repr(decrypted), salt_hash)

    return decrypted


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()