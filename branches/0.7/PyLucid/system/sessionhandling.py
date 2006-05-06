#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Allgemeiner CGI-Session-handler
auf Cookie + SQL basis

benötigte SQL-Tabelle:
-------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lucid_session_data` (
  `session_id` varchar(32) NOT NULL default '',
  `timestamp` int(15) NOT NULL default '0',
  `ip` varchar(15) NOT NULL default '',
  `domain_name` varchar(50) NOT NULL default '',
  `session_data` text NOT NULL,
  PRIMARY KEY  (`session_id`),
  KEY `session_id` (`session_id`)
) COMMENT='Python-SQL-CGI-Sessionhandling';
-------------------------------------------------------

Information
===========
Session-Handling ermöglicht es, Variablen (ein dict) zwischen verschiedene
Anfragen hinweg pro User zu speichern.
Damit ist es einfacher Web-Applikationen in Python-CGI zu schreiben, ohne Daten
ständig per Formular weiter zu transportieren ;)

Ein Besucher der Webseite wird mit einer eindeutigen Session-ID per Cookie gekennzeichnet.
Variablen werden in ein Dictioary gespeichert. Dieses Dict wird mittelt pickle serialisiert
und zusammen mit der Session-ID in die SQL-Datenbank gespeichert.
Beim nächsten Aufruf stehen die speicherten Daten wieder zu verfügung.

Grober Ablauf:
==============

session = sessionhandling.sessionhandler( mySQLdb.cursor, sql_tablename, file_like_log )
# mySQLdb.cursor => Cursor-Objekt der Datenbank-API
# sql_tablename  => Name der Tabelle, in der die Sessiondaten verwaltet werden soll (s.SQL-Dump oben)
# file_like_log  => Ein LOG-Objekt, welches eine write()-Methode besitzt

# Erst nach der Instanzierung kann der HTML-Header an den Client geschickt werden
print "Content-type: text/html\n"

if self.session.ID == False:
    # Keine Session vorhanden
else:
    # eine Session ist vorhanden
    if aktion == "LogOut":
        # ein LogOut wird durchgeführt
        self.session.delete_session()
    else:
        # Schreibe Informationen in das Dictionary
        self.session[key] = data
        self.session["UserName"] = username

    # Sessiondaten in die Datenbank schreiben
    self.session.update_session()

    # Session-Daten anzeigen:
    print self.session


Hinweis
-------
Da das Sessionhandling auf Cookies basiert, ist folgendes wichtig:
For dem Instanzieren der sessionhandler-Klasse darf noch kein Header (print "Content-type: text/html\n") an
den Client geschickt worden sein! Ansonsten zählt der Cookie-Print nicht mehr zum Header und wird im Browser
einfach nur angezeigt ;)
"""

__version__ = "v0.2"

__history__ = """
v0.2
    - NEU: Klasse erbt von dict
v0.1.1
    - Umstallung auf neue Art Log-Ausgaben zu machen
v0.1.0
    - Großer Umbau: Diese Klasse ist nun nicht mehr allgemein Nutzbar, sondern an PyLucid
        angepasst, da es die PyLucid-Objekte direkt benutzt.
    - Umstellung bei den LOG-Ausgaben.
v0.0.6
    - Optionales base64 encoding der Sessiondaten
    - PyLucid's page_msg wird bei debug() genutzt, wenn vorhanden
v0.0.5
    - Umstellung auf MySQLdb.cursors.DictCursor
v0.0.4
    - NEU: verbose_log: damit nicht die Log-Ausgaben zuviele sind ;)
v0.0.3
    - __delitem__() hinzugefügt, um Session daten auch wieder löschen zu können
v0.0.2
    - Fehlerbereinigt / verschönert
v0.0.1
    - erste Version
"""

import os, sys, md5, time, pickle
from socket import getfqdn
from Cookie import SimpleCookie


# Bestimmt den Log-Typ
log_typ = "sessionhandling"
verbose_log    = True

# Sollen die Daten im base64 Format in die Datenbank geschrieben werden
base64format = False
if base64format == True:
    import base64


class cookieHandler:
    def __init__ (self, request, response, page_msg_debug):
        self.request        = request
        self.response       = response
        self.page_msg_debug = page_msg_debug

        # shorthands
        self.log            = request.log
        self.page_msg       = request.page_msg
        self.preferences    = request.preferences

        self.CookieName     = "PyLucid_id"

    def getClientID(self):
        """
        Liefert ein existierender Client-ID zurück.
        Wenn noch kein cookie existiert, wird dieser erstellt.
        """
        clientID = self._read_cookie()

        if clientID == False:
            # Kein Cookie vorhanden, also machen wir eins
            clientID = self._gen_clientID()
            self.writeCookie(clientID)

        return clientID


    def _read_cookie(self):
        """ Liest die ID von einem evtl. vorhandenen Cookie """

        if self.page_msg_debug == True:
            self.page_msg( "-"*30 )

        cookie_id = self.readCookie()
        if cookie_id == False:
            # Es gibt kein Session-Cookie, also gibt es keine gültige Session
            msg = "no client cookie found."
            if verbose_log == True:
                self.log.write( msg, "sessionhandling", "error" )
            if self.page_msg_debug == True:
                self.page_msg( msg )
                self.page_msg( "-"*30 )
            return False

        if cookie_id == "":
            self.status = "deleted Cookie found / Client not LogIn!"
            if verbose_log==True:
                self.log.write(self.status, "sessionhandling", "error" )
            return False

        if len(cookie_id) != 32:
            # Mit dem Cookie stimmt wohl was nicht ;)
            self.deleteCookie()
            msg = "wrong Cookie len: %s !" % len( cookie_id )
            if verbose_log == True:
                self.log.write( msg, "sessionhandling", "error" )
            if self.page_msg_debug == True:
                self.page_msg( msg )
                self.page_msg( "-"*30 )
            return False

        return cookie_id

    def _gen_clientID(self):
        "Generiert eine Session ID anhand der Zeit und der REMOTE_ADDR"
        clientID = md5.new(
            str(time.time()) + self.request.environ["REMOTE_ADDR"]
        ).hexdigest()

        return clientID

    #____________________________________________________________________________________________
    # Allgemeine Cookie-Funktionen

    def readCookie(self):
        "liest Cookie"
        if not self.CookieName in self.request.cookies:
            return False

        try:
            cookieData = self.request.cookies[self.CookieName].value
        except KeyError:
            return False

        if self.page_msg_debug == True:
            self.page_msg(
                "client cookie '%s' exists: '%s'" % (
                    self.CookieName, cookieData
                )
            )
        return cookieData


    def writeCookie(self, Text, expires=None):
        """
        speichert Cookie
        Es wird kein 'expires' gesetzt, somit ist der Cookie gültig/vorhanden bis der
        Browser beendet wurde.
        """
        #~ if expires==None: expires=self.timeout_sec
        #~ self.Cookie[self.CookieName]["path"] = self.preferences["poormans_url"]
        #~ self.Cookie[self.CookieName]["expires"] = expires


        if self.CookieName in self.request.cookies:
            raise "Existiert schon!"

        if self.page_msg_debug == True:
            self.page_msg( "set_cookie '%s': %s" % (self.CookieName, Text))

        self.response.set_cookie(self.CookieName, Text)

        #~ if self.page_msg_debug == True:
            #~ CookieData = self.request.cookies[self.CookieName].value
            #~ self.page_msg("test Cookie: '%s'" % CookieData)

    def deleteCookie(self):
        if self.page_msg_debug == True:
            self.page_msg( "delete_cookie '%s'" % self.CookieName)

        if self.CookieName in self.request.cookies:
            self.response.delete_cookie(self.CookieName)


#_____________________________________________________________________________



class sessionhandler(dict):
    """
    CGI-Session Handler
    used mySQL and Cookies

    http://www.python-forum.de/viewtopic.php?p=19523#19523
    """

    def __init__ (self, request, response, page_msg_debug):
        dict.__init__(self)

        self.request        = request
        self.response       = response
        self.page_msg_debug = page_msg_debug

        # shorthands
        self.db             = request.db
        self.log            = request.log
        self.page_msg       = request.page_msg
        self.preferences    = request.preferences

        self.sql_tablename  = "session_data"
        self.timeout_sec    = 1800

        self.set_default_values()

        # Client ID ermitteln
        c = cookieHandler(request, response, page_msg_debug)
        self["user_id"] = c.getClientID()

        # Evtl. vorhandene Session-Daten aus DB einlesen
        self.read_session()

        # Daten die erst mit dem sessionhandling verfügbar sind,
        # in das Logging Module übertragen
        self.log.client_sID = self["user_id"]
        self.log.client_user_name = self["user"]
        self.log.client_domain_name = self["client_domain_name"]

    def set_default_values(self):
        """
        Setzt Interne Session-Variable auf voreinstestellte
        'keine-Session-vorhanden-Werte'
        benötigt von:
        self.__init__()
        self.delete_session()
        """
        self["client_IP"] = self.request.environ.get("REMOTE_ADDR","unknown")
        self["client_domain_name"] = "[not detected]"

        self["user_id"] = False
        self["isadmin"] = False
        self["user"] = False

        self.RAW_session_data_len   = -1


    def read_session(self):
        status = self.read_session_data(self["user_id"])
        if status == False:
            # Es gibt keine Daten zur ID / Falsche Daten vorhanden
            msg = "no session data for id '%s'" % self["user_id"]
            if verbose_log == True:
                self.log.write( msg, "sessionhandling", "error" )
            if self.page_msg_debug == True:
                self.page_msg(msg)
                self.page_msg("-"*30)
            return

        if self.page_msg_debug == True:
            self.debug()

        # Session-Daten auf Vollständigkeit prüfen
        for key in ("isadmin","user_id","user"):
            if not self.session_data.has_key(key):
                # Mit den Session-Daten stimmt was nicht :(
                msg = "Error in Session Data: Key %s not exists." % key
                self.log.write( msg, "sessionhandling", "error" )
                if self.page_msg_debug == True:
                    self.page_msg( msg )
                    self.debug_session_data()
                self.delete_session()
                self.page_msg( "Your logged out!" )
                return

        msg = "found Session for ID: %s" % self["user_id"]
        if verbose_log == True:
            self.log.write( msg, "sessionhandling", "OK" )
        if self.page_msg_debug == True:
            self.page_msg( msg )
            self.page_msg( "-"*30 )
            #~ for k,v in self.session_data.iteritems():
                #~ self.page_msg( "%s - %s" % (k,v) )

    def read_session_data(self, cookie_id):
        "Liest Session-Daten zur angegebenen ID aus der DB"
        DB_data = self.read_from_DB(cookie_id)
        if DB_data == False:
            # Keine Daten in DB
            return False

        if DB_data["ip"] != self["client_IP"]:
            self.delete_session()
            raise IndexError(
                "Wrong client IP from DB: %s from Client: %s" % (
                    DB_data["ip"], current_IP
                )
            )

        # Session ist OK
        msg = "Session is OK\nSession-Data %.2fSec old" % (
            time.time()-DB_data["timestamp"]
        )
        if verbose_log == True:
            self.log.write( msg, "sessionhandling", "OK" )
        if self.page_msg_debug == True: self.page_msg( msg )

        self["user_id"]     = cookie_id
        self.session_data   = DB_data["session_data"]


    def makeSession(self):
        """
        Startet eine Session
        """
        # Stellt Client-Domain-Name fest
        try:
            self["client_domain_name"] = getfqdn(self["client_IP"])
        except Exception, e:
            self["client_domain_name"] = "[getfqdn Error: %s]" % e

        # Speichert den User in der SQL-DB
        self.insert_session()


    def delete_session(self):
        "Löscht die aktuelle Session"
        if self["user_id"] == False:
            self.status = "OK;Client is LogOut, can't LogOut a second time :-)!"
            return

        if self.page_msg_debug == True: self.debug_session_data()
        self.db.delete(
            table = self.sql_tablename,
            where = ("session_id",self["user_id"])
        )
        if self.page_msg_debug == True: self.debug_session_data()

        oldID = self["user_id"]

        # Interne-Session-Variablen rücksetzten
        self.set_default_values()

        self.status = "OK;delete Session data / LogOut for '%s'" % oldID


    def commit(self):
        """
        Schreibt die aktuellen Sessiondaten in die DB.
        Sollte also immer als letztes Aufgerufen werden ;)
        """

        session_data = pickle.dumps(dict(self))
        if base64format == True:
            session_data = base64.b64encode( session_data )
        self.RAW_session_data_len = len( session_data )

        self.delete_old_sessions() # Löschen veralteter Sessions in der DB

    #____________________________________________________________________________________________
    # Allgemeine SQL-Funktionen

    def insert_session(self):
        "Eröffnet eine Session"
        self.state



        self.db.insert(
            table = self.sql_tablename,
            data  = {
                "session_id"    : self["user_id"],
                "timestamp"     : time.time(),
                "ip"            : self["client_IP"],
                "domain_name"   : self["client_domain_name"],
                "session_data"  : session_data,
            }
        )
        self.log.write( "created Session.", "sessionhandling", "OK" )
        if self.page_msg_debug == True:
            self.page_msg("insert session data for:", self["user_id"])
            self.debug_session_data()

    def update_session(self):
        "Aktualisiert die Session-Daten"
        self.delete_old_sessions() # Löschen veralteter Sessions in der DB

        session_data = pickle.dumps(self)
        if base64format == True:
            session_data = base64.b64encode( session_data )

        self.RAW_session_data_len = len( session_data )

        self.db.update(
            table   = self.sql_tablename,
            data    = {
                "session_data"  : session_data,
                "timestamp"     : time.time()
            },
            where   = ("session_id", self["user_id"]),
            limit   = 1,
        )
        #~ self.debug_session_data()

        if verbose_log == True:
            self.log.write( "update Session: ID:%s" % self["user_id"], "sessionhandling", "OK" )
        if self.page_msg_debug == True:
            self.page_msg("update Session: ID:%s" % self["user_id"])
            self.debug_session_data()

    def read_from_DB(self, session_id):
        "Liest Sessiondaten des Users mit der >session_id<"
        DB_data = self.db.select(
                select_items    = ["session_id", "timestamp", "ip", "domain_name", "session_data"],
                from_table      = self.sql_tablename,
                where           = ("session_id",session_id)
            )
        if DB_data == []:
            return False

        self.delete_old_sessions() # Löschen veralteter Sessions in der DB

        #~ if self.page_msg_debug == True: self.page_msg( "DB_data:",DB_data )
        #~ if len(DB_data) != 1:
            #~ raise "More than one Session in DB!", len(DB_data)

        DB_data = DB_data[0]

        self.RAW_session_data_len = len(DB_data["session_data"])

        if base64format == True:
            DB_data["session_data"] = base64.b64decode(DB_data["session_data"])
        DB_data["session_data"] = pickle.loads(DB_data["session_data"])

        if self.page_msg_debug == True:
            self.debug_session_data()

        return DB_data


    def delete_old_sessions(self):
        "Löscht veraltete Sessions in der DB"
        SQLcommand  = "DELETE FROM %s%s" % (self.db.tableprefix, self.sql_tablename)
        SQLcommand += " WHERE timestamp < %s"

        current_timeout = time.time() - self.timeout_sec

        try:
            self.db.cursor.execute(
                SQLcommand,
                ( current_timeout, )
            )
        except Exception, e:
            print "Content-type: text/html\n"
            print "Delete Old Session error: %s" % e
            sys.exit()

        if self.page_msg_debug == True: self.debug_session_data()

    #____________________________________________________________________________________________

    def debug_session_data(self):
        if verbose_log != True:
            return

        import inspect
        stack_info = inspect.stack()[2][4][0]

        try:
            RAW_db_data = self.db.select(
                select_items    = ['timestamp', 'session_data','session_id'],
                from_table      = self.sql_tablename,
                where           = [("session_id",self["user_id"])]
            )[0]
            self.page_msg( "Debug from %s: %s<br />" % (stack_info, RAW_db_data) )
        except Exception, e:
            self.page_msg( "Debug-Error from %s: %s" % (stack_info,e) )
            #~ for i in inspect.stack(): self.page_msg( i )

    #____________________________________________________________________________________________
    ## Debug

    def debug(self):
        "Zeigt alle Session Informationen an"

        import inspect
        # PyLucid's page_msg nutzen
        self.page_msg( "-"*30 )
        self.page_msg(
            "Session Debug (from '%s' line %s):" % (inspect.stack()[1][1][-20:], inspect.stack()[1][2])
        )

        self.page_msg("len:", len(self))
        for k,v in self.iteritems():
            self.page_msg( "%s - %s" % (k,v) )
        self.page_msg("ID:", self["user_id"])
        self.page_msg( "-"*30 )

    def debug_last(self):
        """ Zeigt die letzten Einträge an """
        import inspect
        self.page_msg(
            "Session Debug (from '%s' line %s):" % (inspect.stack()[1][1][-20:], inspect.stack()[1][2])
        )
        info = self.db.select( ["timestamp","session_id"], "session_data",
            limit=(0,5),
            order=("timestamp","DESC"),
        )
        for item in info:
            self.page_msg(item)





