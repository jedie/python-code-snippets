#!/usr/bin/python
# -*- coding: UTF-8 -*-

from colubrid.exceptions import *

class PermissionDenied(AccessDenied):
    """
    Zugriff verweigert
    """
    code = 403
    title = 'permission denied'
    msg = 'Access was denied to this resource.'
    def __init__(self, msg):
        self.msg = msg

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