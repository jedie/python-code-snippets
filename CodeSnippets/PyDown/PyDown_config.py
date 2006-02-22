#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Diese Konfigurations-Datei ist die eigentliche WSGI-App die vom CGI-Handler
benutzt wird.
"""

from PyDown.PyDown import cfg, app

# Überschreiben der Basis-Einstellungen
cfg["ext_whitelist"] = (".mp3",)
cfg["base_path"] = "/tmp"
cfg["only_https"] = True
cfg["only_auth_users"] = True

if __name__ == '__main__':
    from colubrid import execute
    execute()

