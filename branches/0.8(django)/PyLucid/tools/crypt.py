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


import os, sys, time, sha, random, base64

if __name__ == "__main__":
    print "Local DocTest..."
    settings = type('Mock', (object,), {})()
    settings.SECRET_KEY = "DocTest"
    smart_str = str
else:
    from django.conf import settings
    from django.utils.encoding import smart_str


# Warning: Debug must always be False in productiv environment!
DEBUG = True
#DEBUG = False
if DEBUG:
    import warnings
    warnings.warn("Debugmode is on", UserWarning)

HASH_TYP = "sha1"

SALT_LEN = 6 # length of the random salt value
HASH_LEN = 40 # length of a SHA-1 hexdigest

# SHA-1 hexdigest + "sha1" + (2x "$") + salt length
SALT_HASH_LEN = HASH_LEN + 4 + 2 + SALT_LEN


class SaltHashError(Exception):
    pass


def get_new_seed(can_debug = True):
    """
    Generate a new, random seed value.

    >>> get_new_seed() # DEBUG is True in DocTest!
    'DEBUG!_1234567890'
    >>> seed = get_new_seed(can_debug=False)
    >>> assert seed != 'DEBUG!', "seed is: %s" % seed
    >>> assert len(seed) == HASH_LEN, "Wrong length: %s" % len(seed)
    """
    if can_debug and DEBUG:
        seed = "DEBUG!_1234567890"
    else:
        raw_seed = "%s%s%s%s" % (
            random.randint(0, sys.maxint - 1), os.getpid(), time.time(),
            settings.SECRET_KEY
        )
        seed = sha.new(raw_seed).hexdigest()

    return seed


def get_new_salt(can_debug = True):
    """
    Generate a new, random salt value.

    >>> get_new_salt() # DEBUG is True in DocTest!
    'DEBUG!'
    >>> salt = get_new_salt(can_debug=False)
    >>> assert salt != 'DEBUG!_1234567890', "salt is: %s" % salt
    >>> assert len(salt) == SALT_LEN, "Wrong length: %s" % len(salt)
    """
    seed = get_new_seed(can_debug)
    return seed[:SALT_LEN]


def make_hash(txt, salt):
    """
    make a SHA1 hexdigest from the given >txt< and >salt<.
    IMPORTANT:
        This routine must work like
        django.contrib.auth.models.User.set_password()!

    >>> make_hash(txt="test", salt='DEBUG!')
    '0398bf140231dbfa1e0fb13421e176a1bb27bc72'
    """
    hash = sha.new(salt + smart_str(txt)).hexdigest()
    return hash

def get_salt_and_hash(txt):
    """
    Generate a hast value with a random salt
    returned salt and hash as a tuple

    >>> get_salt_and_hash("test")
    ('sha1', 'DEBUG!', '0398bf140231dbfa1e0fb13421e176a1bb27bc72')
    """
    if not isinstance(txt, str):
        raise SaltHashError("Only string allowed!")

    salt = get_new_salt()
    hash = make_hash(txt, salt)

    return (HASH_TYP, salt, hash)


def make_salt_hash(txt):
    """
    make from the given string a hash with a salt value
    returned one string back

    >>> make_salt_hash("test")
    'sha1$DEBUG!$0398bf140231dbfa1e0fb13421e176a1bb27bc72'
    """
    salt_hash = "$".join(get_salt_and_hash(txt))
    return salt_hash


def check_salt_hash(txt, salt_hash):
    """
    compare txt with the salt-hash.

    TODO: Should we used the django function for this?
        Look at: django.contrib.auth.models.check_password

    >>> salt_hash = make_salt_hash("test")
    >>> salt_hash
    'sha1$DEBUG!$0398bf140231dbfa1e0fb13421e176a1bb27bc72'
    >>> check_salt_hash("test", salt_hash)
    True
    """
#    if not (isinstance(txt, str) and isinstance(salt_hash, str)):
#        raise SaltHashError("Only string allowed!")

    if len(salt_hash) != SALT_HASH_LEN:
        raise SaltHashError("Wrong salt-hash length.")

    try:
        type, salt, hash = salt_hash.split("$")
    except ValueError:
        raise SaltHashError("Wrong salt-hash format.")

    if type != "sha1":
        raise SaltHashError("Unsupported hash method.")

    test_hash = make_hash(txt, salt)
#    raise
    if hash != test_hash:
        msg = "salt-hash compare failed."
        if DEBUG:
            msg += " (txt: '%s', salt: '%s', hash: '%s', test_hash: '%s')" % (
                txt, salt, hash, test_hash
            )
        raise SaltHashError(msg)

    return True


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


def encrypt(txt, key, use_base64=True, can_debug = True):
    """
    XOR ciphering with a SHA salt-hash checksum

    >>> encrypt(u"1234", u"ABCD") # DEBUG is True in DocTest!
    u'crypt 1234 with ABCD'

    >>> encrypt(u"1234", u"ABCD", can_debug=False)
    u'sha1$DEBUG!$1c3f99b739c59c6569800f0b9e6bd426f3dcd063cHBwcA=='

    >>> encrypt(u"1234", u"ABCD", use_base64=False, can_debug=False)
    u'sha1$DEBUG!$1c3f99b739c59c6569800f0b9e6bd426f3dcd063pppp'
    """
    if not (isinstance(txt, unicode) and isinstance(key, unicode)):
        raise UnicodeError("Only unicode allowed!")

    if can_debug and DEBUG:
        return "crypt %s with %s" % (txt, key)

    salt_hash = make_salt_hash(repr(txt))
    salt_hash = unicode(salt_hash)

    crypted = crypt(txt, key)
    if use_base64==True:
        crypted = base64.b64encode(crypted)
    return salt_hash + crypted


def decrypt(crypted, key, use_base64=True, can_debug = True):
    """
    1. Decrypt a XOR crypted String.
    2. Compare the inserted sSHA salt-hash checksum.

    >>> decrypt(u'crypt 1234 with ABCD', u"ABCD") # DEBUG is True in DocTest!
    u'1234'

    >>> crypted = encrypt(u"1234", u"ABCD", can_debug=False)
    >>> crypted
    u'sha1$DEBUG!$1c3f99b739c59c6569800f0b9e6bd426f3dcd063cHBwcA=='
    >>> decrypt(crypted, u"ABCD", can_debug=False)
    u'1234'

    >>> crypted = encrypt(u"1234", u"ABCD", use_base64=False, can_debug=False)
    >>> decrypt(crypted, u"ABCD", use_base64=False, can_debug=False)
    u'1234'
    """
    if not (isinstance(crypted, unicode) and isinstance(key, unicode)):
        raise UnicodeError("Only unicode allowed!")

    if can_debug and DEBUG:
        txt, _, key2 = crypted.split(" ", 3)[1:]
        assert key == key2, "key: %s != key2: %s" % (key, key2)
        return txt

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

def django_to_sha_checksum(django_salt_hash):
    """
    Create a JS-SHA-Checksum from the django user password.

    The >django_salt_hash< is:
        user = User.objects.get(...)
        django_salt_hash = user.password

    >>> django_to_sha_checksum("sha1$DEBUG!$50b412a7ef09f4035f2daca882a1f8bfbe263b62")
    (u'crypt 50b412a7ef09f4035f2d with aca882a1f8bfbe263b62', 'DEBUG!')
    """
    hash_typ, salt, hash = django_salt_hash.split("$")
    assert hash_typ == "sha1", "hash typ not supported!"
    assert len(hash) == HASH_LEN, "Wrong hash length! (Not a SHA1 hash?)"

    # Split the SHA1-Hash in two pieces
    sha_a = hash[:(HASH_LEN/2)]
    sha_b = hash[(HASH_LEN/2):]

    sha_a = unicode(sha_a)
    sha_b = unicode(sha_b)
    sha_checksum = encrypt(txt=sha_a, key=sha_b)

    return sha_checksum, salt


def check_js_sha_checksum(challenge, sha_a2, sha_b, sha_checksum):
    """
    Check a PyLucid JS-SHA-Login

    >>> salt1 = "a salt value"
    >>> challenge = "debug"
    >>> password = "test"
    >>>
    >>> hash = make_hash(password, salt1)
    >>> hash
    'f893fc3ebdfd886836822161b6bc2ccac955e014'
    >>> django_salt_hash = "$".join(["sha1", salt1, hash])
    >>> sha_checksum, salt2 = django_to_sha_checksum(django_salt_hash)
    >>> sha_checksum
    u'crypt f893fc3ebdfd88683682 with 2161b6bc2ccac955e014'
    >>> assert salt1 == salt2
    >>>
    >>> sha_a = hash[:(HASH_LEN/2)]
    >>> sha_a
    'f893fc3ebdfd88683682'
    >>> sha_b = hash[(HASH_LEN/2):]
    >>> sha_b
    '2161b6bc2ccac955e014'
    >>> sha_a2 = make_hash(sha_a, challenge)
    >>> sha_a2
    '0d96f2fdda9c6f633ba0f5c2619aa7706abc492d'
    >>>
    >>> check_js_sha_checksum(challenge, sha_a2, sha_b, sha_checksum)
    True
    """
    sha_checksum = unicode(sha_checksum)
    sha_b = unicode(sha_b)

    encrypted_checksum = decrypt(sha_checksum, sha_b)
    client_checksum = make_hash(encrypted_checksum, challenge)

    if client_checksum == sha_a2:
        return True

    return False




def _doc_test(verbose):
    global DEBUG
    DEBUG = True

    import doctest
    doctest.testmod(verbose=verbose)

if __name__ == "__main__":
    _doc_test(verbose=False)
#    _doc_test(verbose=True)
    print "DocTest end."