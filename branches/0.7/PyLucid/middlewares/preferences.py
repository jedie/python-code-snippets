#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Middelware


"""


import config # PyLucid Grundconfiguration

class Preferences(dict):
    def __init__(self):
        dict.__init__(self)
        self.update(config.config) # Grundconfig in Dict aufnehmen

    def update_from_sql(self, db):
        """ Preferences aus der DB lesen und in self speichern """

        #~ try:
        RAWdata = db.get_all_preferences()
        #~ except Exception, e:
            #~ msg = "<h1>Error: Can't read preferences:</h1>"
            #~ msg += str(e)
            #~ msg += "<p>(Did you install PyLucid correctly?)</p>"
            #~ msg += "<hr><address>PyLucid</address>"
            #~ raise Exception, msg # FIXME <- eigene Exception definieren und abfragen

        for line in RAWdata:
            # Die Values sind in der SQL-Datenbank als Type varchar() angelegt.
            # Doch auch Zahlenwerte sind gespeichert, die PyLucid doch lieber
            # auch als Zahlen sehen möchte ;)
            try:
                line["value"] = int(line["value"])
            except ValueError:
                pass

            if not self.has_key(line["section"]):
                # Neue Sektion
                self[line["section"]] = {}

            self[line["section"]][line["varName"]] = line["value"]



class preferencesMiddleware(object):
    """
    preferences Tabelle aus Datenbank lesen und als Dict zur verfügung stellen
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['PyLucid.preferences'] = Preferences()
        return self.app(environ, start_response)


