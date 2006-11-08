#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"



"""
PyLucid Plugin - 'phpBBAdmin'

    -löschen von Spamusern

Die Angabe des SQLprefix muß evtl. in der seperaten
Datei 'phpBBtableprefix.py' angepasst werden!
"""



__version__="0.1.1"

__history__= """
v0.1.1
    - user_lastvisit=0 raus genommen (Machen Bots mittlerweile auch!)
v0.1
    - init with "delete spamuser" ;)
"""


from PyLucid.plugins.phpBBadmin.phpBBtableprefix import SQLprefix



from PyLucid.system.BaseModule import PyLucidBaseModule


class phpBBadmin(PyLucidBaseModule):

    def lucidTag(self):
        #~ self.response.debug()
        self.response.write("<h1>phpBBAdmin</h1>\n")

        if self.request.form.has_key("make"):
            # Ausgewählte User sollen gelöscht werden
            #~ self.page_msg(self.request.form)
            self.deleteUsers()

        self.makeTable()


    def makeTable(self):
        """
        Tabelle zur Auswahl der User aufbauen.

        SELECT * FROM `phpbb_users` WHERE user_posts=0 AND user_lastvisit=0
        """

        SQLcommand = (
            'SELECT user_id, user_active, username, user_website, user_email'
            ' FROM %susers'
            ' WHERE user_posts=0 AND user_website!=""'
        ) % SQLprefix
        self.response.write("<pre>%s</pre>\n" % SQLcommand)
        try:
            spam_user = self.db.process_statement(SQLcommand)
        except Exception, e:
            self.response.write("<h3>Error:</h3><p>%s</p>\n" % e)
            self.response.write(
                "<p>Is the SQLprefix '%s' correct?</p>\n" % SQLprefix
            )
            return

        if spam_user==[]:
            self.response.write("No Spamuser found in DB ;)\n")
            return


        for line in spam_user:
            # HTML-checkbox einfügen
            line["delete User?"] = (
                '<input type="checkbox" name="delete_id"'
                ' value="%s" />'
            ) % line["user_id"]

            # URL anklickbar machen ;)
            line["user_website"] = (
                '<a href="%(url)s">%(url)s</a>'
            ) % {"url": line["user_website"]}


        self.response.write('<p>Here a list of every spam user.</p>\n')

        self.response.write(
            '<form method="post" action="%s">\n' % self.URLs.currentAction()
        )
        # Tabelle erzeugen
        self.tools.writeDictListTable(
            spam_user, self.response, primaryKey="username"
        )
        self.response.write(
            '<p>Disallow username: '
            '<input type="checkbox" name="disallow" value="disallow"'
            ' checked="checked" /></p>\n'
            '<input type="submit" value="make" name="make" />\n'
            '</form>\n'
        )

    def deleteUsers(self):
        if not self.request.form.has_key("delete_id"):
            self.page_msg("No User selected!")
            return

        IDs = self.request.form.getlist("delete_id")
        for id in IDs:
            self.deleteUser(id)

    def deleteUser(self, id):
        """
        phpBB Userprofil löschen
        """
        user_name = self.db.select(
            select_items    = ["username"],
            from_table      = "%susers" % SQLprefix,
            where           = ("user_id", id),
            autoprefix      = False
        )
        user_name = user_name[0]["username"]
        if self.request.form.has_key("disallow"):
            self.disallowUser(user_name)

        self.page_msg(
            "Delete user '%s' (id %s)." % (user_name, id)
        )

        self.db.delete(
            table       = "%susers" % SQLprefix,
            where       = ("user_id", id),
            limit       = 1,
            autoprefix  = False
        )

    def disallowUser(self, user_name):
        """
        Den Usernamen verbieten
        """

        self.page_msg(
            "Insert '%s' in disallowed usernames." % (user_name)
        )

        self.db.insert(
            table = "%sdisallow" % SQLprefix,
            data  = { "disallow_username" : user_name },
            autoprefix  = False
        )




