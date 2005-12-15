
PyAdmin by www.jensdiemer.de
(GNU General Public License)



History
=======
v0.1.1
 - neues Modul "SystemInfo"
 - FileBrowser: schnellerer Aufbau im Browser, weil Informationen zu Dateien erst im
    zweiten Durchlauf eingelesen werden und nachträglich per JavaScript in
    die Tabelle eingefügt werden.
v0.1.0
 - Erste Version




Installation
============

Zum installieren als inetd-Service:

"/etc/services"
PyAdmin     9000/tcp

"/etc/inetd.conf"
PyAdmin 	stream	tcp	nowait	root	/.../PyAdminInetdServer.py PyAdminInetdServer

inetd neu starten:
/etc/init.d/inetd stop
/etc/init.d/inetd start


PyAdminInetdServer.py benötigt Ausführungsrechte.





Credits
=======
Danke an alle die mir geholfen haben!
insbesondere den Users aus dem python-forum.de!!!