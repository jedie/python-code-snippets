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


import sha, random, base64

HASH_TYP = "sha1"

SALT_LEN = 6 # length of the random salt value
HASH_LEN = 40 # length of a SHA-1 hexdigest

# SHA-1 hexdigest + "sha1" + (2x "$") + salt length
SALT_HASH_LEN = HASH_LEN + 4 + 2 + SALT_LEN


class SaltHashError(Exception):
    pass

def get_salt_and_hash(txt, _debug=False):
    """
    Generate a hast value with a random salt
    returned salt and hash as a tuple

    >>> get_salt_and_hash("test")
    ('sha1', '356a19', '23eb48afb36f672541cab5ee5f07255b3e8bda67')
    """
    if not isinstance(txt, str):
        raise SaltHashError("Only string allowed!")

    salt = sha.new(str(random.random())).hexdigest()[:SALT_LEN]
    hash = sha.new(salt + txt).hexdigest()

    return (HASH_TYP, salt, hash)


def make_salt_hash(txt):
    """
    make from the given string a hash with a salt value
    returned one string back

    >>> make_salt_hash("test")
    'sha1$356a19$23eb48afb36f672541cab5ee5f07255b3e8bda67'
    """
    salt_hash = "$".join(get_salt_and_hash(txt))
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


def encrypt(txt, key, use_base64=True):
    """
    XOR ciphering with a SHA salt-hash checksum

    >>> encrypt(u"1234", u"ABCD")
    'sha1$356a19$24352b9033d86754a51117349820c5b84cd2be71cHBwcA=='

    >>> encrypt(u"1234", u"ABCD", use_base64=False)
    u'sha1$356a19$24352b9033d86754a51117349820c5b84cd2be71pppp'
    """
    if not (isinstance(txt, unicode) and isinstance(key, unicode)):
        raise UnicodeError("Only unicode allowed!")

    salt_hash = make_salt_hash(repr(txt))
    crypted = crypt(txt, key)
    if use_base64==True:
        crypted = base64.b64encode(crypted)
    return salt_hash + crypted


def decrypt(crypted, key, use_base64=True):
    """
    1. Decrypt a XOR crypted String.
    2. Compare the inserted sSHA salt-hash checksum.

    >>> crypted = encrypt(u"1234", u"ABCD")
    >>> decrypt(crypted, u"ABCD")
    u'1234'

    >>> crypted = encrypt(u"1234", u"ABCD", use_base64=False)
    >>> decrypt(crypted, u"ABCD", use_base64=False)
    u'1234'
    """
#    if not (isinstance(crypted, unicode) and isinstance(key, unicode)):
#        raise UnicodeError("Only unicode allowed!")

    salt_hash = str(crypted[:SALT_HASH_LEN])
    crypted = crypted[SALT_HASH_LEN:]
    if use_base64==True:
        crypted = base64.b64decode(crypted)
        crypted = unicode(crypted)

    decrypted = crypt(crypted, key)

    # raised a SaltHashError() if the checksum is wrong:
    check_salt_hash(repr(decrypted), salt_hash)

    return decrypted


#______________________________________________________________________________

def plaintext_to_js_sha_checksum(password):
    """
    Create a Checksum for the PyLucid JS-SHA-Login from a plaintext password.

    >>> plaintext_to_js_sha_checksum("test")
    'sha1$356a19$20e35f157a99b6c1dc888da19a1631a6cb289b84UAYABwFeUVFQBgMEBVIKV1BQVVY='
    """
    hash_typ, salt, hash = get_salt_and_hash(password)
    sha_checksum = salt_hash_to_js_sha_checksum(salt, hash)
    return sha_checksum


def salt_hash_to_js_sha_checksum(salt, hash):
    """
    Create a Checksum for the PyLucid JS-SHA-Login from a salt and hash value.

    >>> salt = "356a19"
    >>> hash = "23eb48afb36f672541cab5ee5f07255b3e8bda67"
    >>> salt_hash_to_js_sha_checksum(salt, hash)
    'sha1$356a19$20e35f157a99b6c1dc888da19a1631a6cb289b84UAYABwFeUVFQBgMEBVIKV1BQVVY='
    """
    assert len(hash) == HASH_LEN, "Wrong hash length! (Not a SHA1 hash?)"

    # Split the SHA1-Hash in two pieces
    sha_a = hash[:(HASH_LEN/2)]
    sha_b = hash[(HASH_LEN/2):]

    sha_a = unicode(sha_a)
    sha_b = unicode(sha_b)
    sha_checksum = encrypt(txt=sha_a, key=sha_b)

    return sha_checksum


def _test():
    # Patch random to make it not random ;)
    global random
    random = type('Mock', (object,), {})()
    random.random=lambda:1

    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()