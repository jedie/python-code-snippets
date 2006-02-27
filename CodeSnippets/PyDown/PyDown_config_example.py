#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Diese Konfigurations-Datei ist die eigentliche WSGI-App die vom CGI-Handler
benutzt wird.
------------------------------------------------------------------------------
Info zur Installation/Benutzung: PyDown_readme.txt

Die Datei kann als Grunlage für deine eigene Konfigurations-Datei dienen,
benenn sie einfach nach "PyDown_config.py" um.
"""

# Default-Config und eigentliche Applikation importieren
from PyDown.PyDown import cfg, app



#_____________________________________________________________________________
# Hier drunter mußt du deine Einstellungen vornehmen:


# Datei-Endungsfilter, nur diese Dateien werden beachtet
cfg["ext_whitelist"] = (".mp3",)

# Basis-Pfad, der "Rekursiv-Freigegeben" werden soll.
cfg["base_path"] = "/tmp"
cfg["max_bandwith"] = 40 # in KB/sec !

# Nur HTTPs Verbindungen erlauben?
cfg["only_https"] = True

# Zugriff nur eingeloggte User, durch Apache's .htaccess-Auth erlauben?
cfg["only_auth_users"] = True

# Debugausgaben anzeigen?
cfg["debug"] = False




#_____________________________________________________________________________



if __name__ == '__main__':
    # Colubrid's name-hook
    from colubrid import execute
    execute()

