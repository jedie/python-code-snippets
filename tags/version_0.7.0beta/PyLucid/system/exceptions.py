#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid own Exception's
"""


#~ class ConnectionError(Exception):
    #~ def __repr__(self):
        #~ return 'Connect Error!'
    #~ pass

class IntegrityError(Exception):
    """
    Fehler bei einer DB-Transaktion
    """
    pass

class WrongTemplateEngine(Exception):
    """
    Die Template-Engine ist falsch
    """
    pass

class WrongInstallLockCode(Exception):
    """
    Falscher "install Lock Code" in der URL
    """
    pass