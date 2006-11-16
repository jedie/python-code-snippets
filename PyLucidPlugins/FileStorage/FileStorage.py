#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"



"""
FileStorage
"""



__version__="0.3.1"

__history__= """
v0.3.1
    - Bugfix: Nun klappt es mit base64 auch mit Python 2.3 :)
v0.3
    - nun werden die Daten in base64 gespeichert
    - MD5 Summe kann mit den Daten in der DB verglichen werden
    - Tabelle werden beim löschen direkt optimiert
v0.2
    - MD5 Summe wird angezeigt und gespeichert.
    - Benutzt die neuen page_msg Farben
v0.2Alpha
    - Daten werden nun in einer seperaten Tabelle eingefügt, das geschied
        mittels raw_cursor, um die automatische DB-Encoding-Konvertierung zu
        umgehen.
    - Benötigt neue Version des DB_wrappers!
v0.1.1
    - Keine 64KB beschränkung durch LONGBLOB
    - Anzeige des Speicherverbrauchs
    - Allgemeine Informationen angezeigt
    - encryption Passwort vorbereitet, aber nicht implementiert
v0.1
    - init with "delete spamuser" ;)
"""

__ToDo__ = """
Fix the ModuleManager and put the SQL commands in the config file!
http://pylucid.htfx.eu/index.py/ModuleManager/
"""



import datetime, cgi, md5, base64



SQL_install_commands = [
"""CREATE TABLE $$plugin_filestorage (
    id INT(11) NOT NULL auto_increment,
    filename VARCHAR(255) NOT NULL,
    upload_time datetime NOT NULL,
    info VARCHAR(255) NOT NULL,
    size INT(11) NOT NULL,
    client_info VARCHAR(255) NOT NULL,
    data_id INT(11) NOT NULL,
    data_md5 VARCHAR(32) NOT NULL,
    owner_id INT(11) NOT NULL,
    public TINYINT(1) NOT NULL DEFAULT '0',
    PRIMARY KEY (id)
) COMMENT = "FileStorage - management data";"""
,
"""CREATE TABLE $$plugin_filestorage_data (
    id INT(11) NOT NULL auto_increment,
    data LONGBLOB,
    PRIMARY KEY (id)
) COMMENT = "FileStorage - BLOB Data";"""
]


SQL_deinstall_commands = [
    "DROP TABLE $$plugin_filestorage;",
    "DROP TABLE $$plugin_filestorage_data;"
]





summary = """<h1>file storage v{{ version }}</h1>

<form action="{{ url }}" method="post" enctype="multipart/form-data">
    <fieldset><legend>file upload</legend>
        <strong>Note:</strong>
        <ul>
            <li>The files store insecure: Use only for unimportant files.</li>
            <li>Data store in database, so only for small files suitably. (>1-2MB)!</li>
        </ul>
        <label class="left" for="upload">upload:</label>
        <input class="right" type="file" name="upload" size="50" id="filename" />
        <br />
        <label class="left" for="info">info:</label>
        <input class="right" name="info" value="" size="50" maxlength="255" type="text"><small> (optional)</small>
        <br />
        <label class="left" for="password">password:</label>
        <input class="right" name="password" value="" size="50" maxlength="255" type="text"><small> (encryption not implemented yet!)</small>
        <br />
        <label class="left" for="public">public:</label>
        <input class="right" name="public" value="1" type="checkbox"><small> (check and every PyLucid user can download this file)</small>
        <br />
        <input type="submit" value="upload" />
    </fieldset>
</form>


{% if not filelist %}
    <small>[ no files ]</small>
{% else %}
    <table>
        <tr>
            <th>filename</th>
            <th>public?</th>
            <th>file size</th>
            <th>upload time</th>
            <th>file info</th>
            <th>client info</th>
            <th>md5</th>
            <th>from user</th>
            <th>action</th>
        </tr>
        {% for file in filelist %}
            {% cycle rowclass through "odd", "even" %}
            <tr class="{{ rowclass }}">
                <td>
                    <a href="{{ file.download_url }}" title="Download this file">
                        {{ file.filename|escapexml }}
                    </a>
                </td>
                <td>{{ file.public }}</td>
                <td>{{ file.size|filesizeformat }}</td>
                <td><small>{{ file.upload_time }}</small></td>
                <td><small>{{ file.info|escapexml }}</small></td>
                <td><small>{{ file.client_info|escapexml }}</small></td>
                <td>
                    <a href="{{ file.md5check_url }}">
                        <small>{{ file.data_md5|escapexml }}</small>
                    </a>
                </td>
                <td>
                    {% if file.user_name %}
                        <a href="mailto:{{ file.user_email }}">
                            {{ file.user_name|escapexml }}
                        </a>
                    {% else %}
                        <i title="The User doesn't exist. He's deleted?">unknown</i>
                    {% endif %}
                </td>
                <td>
                    {% if file.delete_url %}
                        <a href="{{ file.delete_url }}" title="Delete '{{ file.filename|escapexml }}'.">
                            delete
                        </a>
                    {% else %}
                        <span title="only owner '{{ file.user_name|escapexml }}' can delete this file">---</span>
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
    </table>
    <p>
        total size: {{ total_size|filesizeformat }} in {{ file_count }} files.
        (Used {{ db_data_length|filesizeformat }} in db, {{ overhead }}% overhead.)
    </p>
{% endif %}
"""



def render_jinja(template, context):
    """
    Ist als normale Funktion ausgelagert, damit sie auch w�hrend der _install
    Phase benutzt werden kann...
    """
    import jinja

    # FIXME: jinja.loader.load() wandelt immer selber in unicode um und
    # mag deswegen kein unicode, also wandeln wir es in einen normale
    # String :(
    template = str(template)

    t = jinja.Template(template, jinja.StringLoader())#, trim=True)
    c = jinja.Context(context)
    content = t.render(c)

    return content





from PyLucid.system.BaseModule import PyLucidBaseModule



class FileStorage(PyLucidBaseModule):

    def __init__(self, *args, **kwargs):
        super(FileStorage, self).__init__(*args, **kwargs)

        self.meta_tablename = "%splugin_filestorage" % self.db.tableprefix
        self.data_tablename = "%splugin_filestorage_data" % self.db.tableprefix

    def lucidTag(self):
        #~ self.response.debug()

        if self.request.files:
            # Ein Upload wurde gemacht
            try:
                self.handle_upload()
            except UploadTooBig, e:
                self.page_msg.red(e)

        self._create_page()

    def _create_page(self):
        """
        Baut die HTML Seite mit dem Upload-Form und der Dateiliste auf
        """

        try:
            filelist = self.get_filedata()
        except Exception, e:
            if not "doesn't exist" in str(e):
                raise Exception(e)
                self.page_msg.red("Error: %s" % e)
            else:
                self.create_table()
            filelist = []

        total_size, file_count, db_data_length, overhead = self.get_size_info()
        overhead = round(overhead, 1)

        context = {
            "url"               : self.URLs.actionLink("lucidTag"),
            "total_size"        : total_size,
            "file_count"        : file_count,
            "db_data_length"    : db_data_length,
            "overhead"          : overhead,
            "filelist"          : filelist,
            "version"           : __version__,
        }
        #~ self.page_msg.debug(context)

        #~ self.templates.write("summary", context)
        self.response.write(
            render_jinja(summary, context)
        )

        self.response.write(
            '<p><small><a href="%s">DROP TABLE</a></small></p>' % \
                                        self.URLs.actionLink("drop_table")
        )

    #_________________________________________________________________________

    def handle_upload(self):
        """
        Eine neue Datei soll gespeichert werden
        """
        #~ self.response.debug()
        info = self.request.form.get("info","")

        FieldStorage = self.request.files['upload']
        filename = FieldStorage.filename
        data = FieldStorage.read()

        totalBytes = self.request.environ["CONTENT_LENGTH"]
        #~ if totalBytes>5000:
            #~ self.page_msg("Upload too big!")
            #~ return

        #~ self.page_msg.debug(self.request.files)
        #~ self.page_msg.debug(filename, totalBytes)

        self.insert(filename, info, data)

    def db_rollback(self):
        try:
            self.db.rollback() # transaktion aufheben
        except Exception, e:
            self.page_msg.red("Error, db rollback failed: %s" % e)
        else:
            self.page_msg.black("Info: db rollback successful.")

    def _make_md5(self, data):
        return md5.new(data).hexdigest()

    def insert(self, filename, info, data):
        """
        Trägt eine neue Datei in die DB ein
        """
        client_info = "%s - %s" % (
            self.session['client_IP'], self.session['client_domain_name']
        )

        raw_cursor = self.db.conn.raw_cursor()

        # Nur die Daten als BLOB einfügen
        sql = "".join(
            ["INSERT INTO ", self.data_tablename," (data) VALUES (%s);"]
        )
        try:
            raw_cursor.execute(sql, (base64.encodestring(data),))
        except Exception, e:
            self.db_rollback()
            txt = "%s..." % str(e)[:200]
            if "MySQL server has gone away" in txt:
                raise UploadTooBig()
            else:
                raise Exception(txt)

        data_id = raw_cursor.lastrowid
        data_md5 = self._make_md5(data)
        size = len(data)
        del(data)

        try:
            # Meta Daten zum Upload eintragen
            self.db.insert(
                table = "plugin_filestorage",
                data  = {
                    "filename"      : filename,
                    "info"          : info,
                    "size"          : size,
                    "data_id"       : data_id,
                    "data_md5"      : data_md5,
                    "upload_time"   : datetime.datetime.now(),
                    "client_info"   : client_info,
                    "owner_id"      : self.session['user_id'],
                    "public"        : self.request.form.get("public",0),
                },
                #~ debug = True
            )
        except Exception, e:
            self.page_msg.red("Error, can't insert Metadata: %s" % e)
            self.db_rollback()
        else:
            self.db.commit() # transaktion ende
            self.page_msg.green(
                "Upload successful. saved %s Bytes. MD5: %s" % (size, data_md5)
            )

    #_________________________________________________________________________

    def get_filedata(self):
        """
        Liefert die Daten zu allen hochgeladenen Dateien zurück.
        """
        result = self._filedata()

        user_list = self.db.userList(select_items=["name","email"])
        #~ self.page_msg.debug(user_list)

        # Daten auffüllen
        for line in result:
            # URLs
            line["download_url"] = self.URLs.actionLink(
                "download", str(line["id"])
            )
            if self.session['user_id'] == line['owner_id']:
                line["delete_url"] = self.URLs.actionLink(
                    "delete", str(line["id"])
                )

            # User Info:
            user_id = line["owner_id"]
            if user_id in user_list:
                user_data = user_list[user_id]
                line["user_name"] = user_data["name"]
                line["user_email"] = user_data["email"]
            else:
                # Vielleicht ist der User mittlerweile gelöscht worden
                pass

            # URLs
            line["md5check_url"] = self.URLs.actionLink(
                "md5check", str(line["id"])
            )

        return result

    def _filedata(self, id=None):
        """
        Liefert Info's zu allen (id=None) oder einer bestimmten Datei zurück
        """
        if id==None:
            # Alle Dateien
            where = (
                "(owner_id=%s) OR (public=1)",
                (self.session['user_id'],)
            )
        else:
            # Info's einer bestimmten Datei
            where = ("(id=%s)", (id,))

        result = self.db.process_statement(
            SQLcommand = (
                "SELECT id, filename, size, data_md5, info, data_id,"
                " upload_time, client_info, owner_id, public"
                " FROM $$plugin_filestorage"
                " WHERE %s" % where[0]
            ),
            SQL_values = where[1]
        )
        return result

    def get_size_info(self):
        """
        Liefert die gesammt Größe und Anzahl aller gespeicherten Dateien
        zurück.
        """
        result = self.db.select(
            select_items    = "id",
            from_table = "plugin_filestorage",
        )
        file_count = len(result)

        result = self.db.process_statement(
            SQLcommand = (
                "SELECT SUM(size)"
                " FROM $$plugin_filestorage;"
            )
        )
        total_size = result[0]["SUM(size)"]
        if total_size == None: total_size=0

        SQLresult = self.db.process_statement("SHOW TABLE STATUS")

        for line in SQLresult:
            if line["Name"] == self.data_tablename:
                db_data_length = line["Data_length"]
                break

        try:
            overhead = float(db_data_length)/float(total_size) * 100.0-100.0
        except ZeroDivisionError:
            overhead = 0.0

        return total_size, file_count, db_data_length, overhead

    #_________________________________________________________________________

    def download(self, function_info=None):
        try:
            filedata = self._get_filedata(function_info)
        except PermissionDeny:
            self.page_msg.red("Permission Deny!")
            return

        self.page_msg.debug(filedata)

        data = self._get_data_by_file_id(filedata["id"])

        file_len = len(data)
        filename = str(filedata['filename']) # kein unicode!

        #~ self.page_msg.debug(len(data), data)

        # Datei zum Browser senden
        self.response.startFileResponse(filename, file_len)
        self.response.write(data)
        return self.response



    def _get_filedata(self, function_info):
        """
        -Liefert Informationen zu Datei zurück, wenn in function_info auch
        eine gültige Datei-ID steckt!
        -Wirft PermissionDeny-Exception, wenn der User auf die Datei nicht
        zugreifen kann.
        """
        try:
            file_id = int(function_info[0])
        except (ValueError, TypeError):
            raise WrongFileID()

        #~ try:
        filedata = self._filedata(file_id)
        if filedata == []:
            raise WrongFileID()

        filedata = filedata[0]

        if self.session['user_id'] != filedata['owner_id'] and \
                                                    filedata['public']!=1:
            raise PermissionDeny()

        return filedata

    def _get_data_by_file_id(self, file_id):
        """
        Liefert die eigentlichen Dateidaten zurück
        """
        # ID des BLOB Eintrags feststellen
        data_id1 = self.db.select(
            select_items    = "data_id",
            from_table = "plugin_filestorage",
            where = ("id",file_id),
        )
        data_id = data_id1[0]["data_id"]

        return self._get_data_by_data_id(data_id)

    def _get_data_by_data_id(self, data_id):
        raw_cursor = self.db.conn.raw_cursor()

        # Eigentlichen Daten aus DB holen
        sql = "".join(
            ["SELECT data FROM ", self.data_tablename, " WHERE (id=%s)"]
        )
        raw_cursor.execute(sql, (data_id,))
        data1 = raw_cursor.fetchone()

        data = data1[0]
        data = data.tostring() # Aus der DB kommt ein array Objekt!

        data = base64.decodestring(data)

        return data

    #_________________________________________________________________________

    def md5check(self, function_info=None):
        """
        Prüft die gespeicherte MD5 Summe: Erstellt eine neue MD5 von den
        gespeicherten DB Daten und vergleicht diese.
        """
        try:
            filedata = self._get_filedata(function_info)
        except (PermissionDeny, WrongFileID), e:
            self.page_msg.red(e)
            return

        #~ self.page_msg.debug(filedata)

        data_md5 = filedata["data_md5"]
        data_id = filedata["data_id"]

        data = self._get_data_by_data_id(data_id)
        db_md5 = self._make_md5(data)
        del(data)

        if data_md5 != db_md5:
            self.page_msg.red("Wrong MD5: %s != %s" % (data_md5, db_md5))
            self.page_msg.red("The saved data in database are corrupt!")
        else:
            self.page_msg.green("MD5 ok, data consistent.")

        self._create_page()

    #_________________________________________________________________________

    def delete(self, function_info=None):
        try:
            filedata = self._get_filedata(function_info)
        except (PermissionDeny, WrongFileID), e:
            self.page_msg.red(e)
            return
        #~ self.page_msg.debug(filedata)
        #~ return

        data_id = filedata["data_id"]
        id = filedata["id"]

        try:
            # Eigentliche Daten löschen
            self.db.delete(
                table = "plugin_filestorage_data",
                where = ("id",data_id),
            )
            # Metadaten löschen
            self.db.delete(
                table = "plugin_filestorage",
                where = ("id",id),
            )
        except Exception, e:
            self.page_msg.red("Can't delete: %s" % e)
        else:
            self.page_msg.green(
                "File '%s' deleted in DB!" % cgi.escape(filedata["filename"])
            )

        try:
            status = self.db.process_statement(
                "OPTIMIZE TABLE %s" % self.data_tablename
            )[0]
        except Exception, e:
            self.page_msg.red("Optimize data table error: %s" % e)
        else:
            self.page_msg.green(
                "Optimize data table: %s" % status["Msg_text"]
            )

        self._create_page()

    #_________________________________________________________________________

    def create_table(self):
        """
        FIXME put this into the ModuleManager!
        """
        for sql in SQL_install_commands:
            try:
                self.db.process_statement(sql)
            except Exception, e:
                self.page_msg.red("Error: %s" % e)
            else:
                self.page_msg.green("One Table created, OK!")

    def drop_table(self):
        """
        FIXME put this into the ModuleManager!
        """
        for sql in SQL_deinstall_commands:
            try:
                self.db.process_statement(sql)
            except Exception, e:
                if "Unknown table" in str(e):
                    self.page_msg.black(
                        "Skip drop table, because it doesn't exists."
                    )
                else:
                    self.page_msg.red("Error: %s" % e)
            else:
                self.page_msg.green("Drop one table OK")




class PermissionDeny(Exception):
    """
    User darf nicht die Datei downloaden/löschen/ändern
    """
    def __str__(self):
        return "Permission Deny!"

class WrongFileID(Exception):
    """
    In der DB existiert keine Datei mit der ID.
    """
    def __str__(self):
        return "wrong file id!"

class UploadTooBig(Exception):
    """
    Der Upload ist einfach zu groß.
    """
    def __str__(self):
        return "ERROR: Upload is too Big!"