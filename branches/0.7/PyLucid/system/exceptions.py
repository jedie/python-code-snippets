#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid own Exception's
"""


class ProbablyNotInstalled(Exception):
    """
    Fehler die auftauchen, wenn PyLucid noch nicht installiert ist.
    Tritt auf, wenn versucht wird auf SQL-Daten zurück zu greifen, wenn
    die Tabellen überhaupt noch nicht eingerichtet wurden.
    """
    pass

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