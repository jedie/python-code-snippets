
"""
Documentation about the JS-MD5-Login
"""


from md5 import new as md5_new

##____________________________________________________________________________

password = "321654987"
salt = "20711"
challenge = "12345"

##____________________________________________________________________________


def md5(txt):
    return md5_new(txt).hexdigest()

def encrypt(txt, key): # Pseudo encrypt
    return "encrypted %s with %s" % (txt, key)

def decrypt(txt, key): # Pseudo decrypt
    txt, _, key2 = txt.split(" ", 3)[1:]
    if key!=key2:
        raise AssertionError("key '%s' != key2 '%s'" % (key, key2))
    return txt

# Die echten crypt Module von PyLucid nutzten:
import sys
sys.path.insert(0,"..")
from PyLucid.system.crypt import encrypt, decrypt

##____________________________________________________________________________

def create_new_user():
    print "\n\n------------ 1. Ein neuer User in der DB anlegen------------"
    print "\n 1.1. Server sendet salt zum Client:",
    print "'%s'" % salt

    print "\n 1.2. Eingabe des Passwortes auf dem Client:",
    print "'%s'" % password

    print "\n 1.3. md5sum = md5(salt + password)"
    md5sum = md5(salt + password)

    print "\n 1.4. �bermittlung der MD5 Summe zum Server:\n"
    print "        md5sum....:", md5sum



    print "\n\n------------ 2. speichern des Users auf dem Server------------"

    print "\n 2.1. Server trennt die MD5 in:",
    md5_a = md5sum[:16]
    md5_b = md5sum[16:]
    print "md5_a: '%s' md5_b: '%s'" % (md5_a, md5_b)

    print "\n 2.2. md5checksum = encrypt(md5_a, key=md5_b)"
    md5checksum = encrypt(md5_a, md5_b)

    print "\n 2.3. Speichern nur der verschl�sselten md5checksum + salt:\n"
    print "        md5checksum:", md5checksum
    print "        salt.......:", salt

    return md5checksum

##____________________________________________________________________________

def user_login(md5checksum):
    print "\n\n------------ 3. Login eines Users------------"

    print "\n 3.1. Server sendet salt '%s' + challenge zum client:" % salt,
    print "'%s'" % challenge

    print "\n 3.2. Eingabe des Passwortes auf dem Client:",
    print "'%s'" % password

    print "\n 3.3. md5(salt + password):",
    md5sum = md5(salt + password)
    print "'%s'" % md5sum

    print "\n 3.4. trennen der MD5 in:",
    md5_a = md5sum[:16]
    md5_b = md5sum[16:]
    print "md5_a: '%s' md5_b: '%s'" % (md5_a, md5_b)

    print "\n 3.5. md5_a2 = md5(challenge + md5_a)\n",
    md5_a2 = md5(challenge + md5_a)

    print "\n 3.6. �bermittlung von md5_a2 und md5_b:"
    print "        md5_a2......:", md5_a2
    print "        md5_b.......:", md5_b



    print "\n\n------------ 4. check auf dem Server------------"

    print "\n 4.1. aus der DB md5checksum: '%s'" % md5checksum

    print "\n 4.2. decrypt(md5checksum, key=md5_b):",
    md5checksum = decrypt(md5checksum, md5_b)
    print "'%s'" % md5checksum

    print "\n 4.3. md5(md5checksum + challenge):",
    md5check = md5(md5checksum + challenge)
    print "'%s'" % md5check

    print "\n 4.4. Vergleich: %s == %s" % (md5check, md5_a2)

##____________________________________________________________________________

if __name__ == "__main__":
    #~ checksum_from_db = create_new_user() # Neuer User in der DB anlegen

    checksum_from_db = "mi4lvvfGMCR/1eLG2ncq4hG2OQI8K0QWIgQqESUISicIOiFk"

    user_login(checksum_from_db) # User will einloggen
