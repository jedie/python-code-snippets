#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid own Exception's
"""


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
