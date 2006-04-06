#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Diese Konfigurations-Datei ist die eigentliche WSGI-App die vom CGI-Handler
benutzt wird.
"""

from PyDown.PyDown import cfg, app

# Überschreiben der Basis-Einstellungen
#~ cfg["allows_user"]      = ("jedie", "snacker", "nero1976", "idontno")
cfg["admin_username"]   = "anonymous"

cfg["ext_whitelist"]    = (".mp3",)
cfg["base_path"]        = "M:/"

cfg["only_https"]       = False
#~ cfg["only_https"]       = True

cfg["only_auth_users"]  = False

# Zugriffe nur von bestimmten IP's zulassen
cfg["IP_range"] = ["127.0.0.1"]

#~ cfg["debug"]            = True


if __name__ == '__main__':
    from colubrid import execute
    execute(app, reload=True)

