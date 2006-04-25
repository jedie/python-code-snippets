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

# Nur dieser User erhalten zugriff
cfg["allows_user"]     =  ("user1", "user2")

# Dier User erhält Admin Rechte
cfg["admin_username"]   = "user1"

# Datei-Endungsfilter, nur diese Dateien werden beachtet
cfg["ext_whitelist"] = (".mp3",)

# Basis-Pfad, der "Rekursiv-Freigegeben" werden soll.
cfg["base_path"] = "/tmp"

# Nur HTTPs Verbindungen erlauben?
cfg["only_https"] = True

# Zugriff nur eingeloggte User, durch Apache's .htaccess-Auth erlauben?
cfg["only_auth_users"] = True

# Zugriffe nur von bestimmten IP's zulassen, z.B.: ["127.0.0.1","192.168.*.*"]
cfg["IP_range"] = ["*.*.*.*"]

# Debugausgaben anzeigen?
cfg["debug"] = False

# Anzahl der Log-Einträge die angezeigt werden sollen
cfg["last_log_count"] = 50

# Anzahl der Einträge die bei "newest Files" angezeigt werden
cfg["newestfiles_count"] = 30

# Ab welcher Anzahl von Verzeichnissen sollen Buchstaben eingeblendet werden?
cfg["min_letters"] =  3

# Wenn als Temp-Verz. nicht das default-System-Temp-Verz. genommen werden soll
cfg["temp"] = None

# Max. alter einer Temp-Datei in Sec. bevor sie automatisch gelöscht wird
cfg["temp_max_old"] = 60


# Soll nach dem Upload eine eMail verschickt werden?
cfg["upload_email_notify"]  = False
# Die Absender-Adresse
cfg["email_from"]           = "pydown@localhost"
# Die Ziel-Adresse
cfg["upload_to"]            = "administator@localhost"

#_____________________________________________________________________________



if __name__ == '__main__':
    # Colubrid's name-hook
    from colubrid import execute
    execute(app, reload=True)

