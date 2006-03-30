#!/usr/bin/python
# -*- coding: UTF-8 -*-


class AccessDenied(Exception):
    """
    Zugriff verweigert, u.a. bei path.check_absolute_path()
    """
    pass

class CanNotSaveFile(Exception):
    """
    Datei k?te nicht auf Platte geschrieben werden
    """
    pass


class NoUpload(Exception):
    """
    Es wird keine Datei hochgeladen
    """
    pass