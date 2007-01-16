#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Administration Sub-Menü : "show internals"

Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

__version__= "$Rev$"

# Python-Basis Module einbinden
import cgi, sys, imp, time

from PyLucid.tools.formatter import filesizeformat

from PyLucid.system.BaseModule import PyLucidBaseModule

class show_internals(PyLucidBaseModule):
    def link( self ):
        return '<a href="%smenu">show_internals</a>' % self.URLs["action"]

    #_______________________________________________________________________

    def lucidTag(self):
        url = self.URLs.actionLink("menu")
        self.response.write('<a href="%s">show internals</a>' % url)

    def menu( self ):
        self.response.write(
            "<h4>show internals v%s</h4>" % __version__
        )
        self.response.write(self.module_manager.build_menu())

    #_______________________________________________________________________

    def python_modules(self):

        back_link = (
            '<a href="%s">back</a>'
        ) % self.URLs.actionLink("menu")
        self.response.write(back_link)

        self.response.write("<h3>Python Module Info</h3>")
        from PyLucid.buildin_plugins.show_internals.module_info \
                                                        import PythonModuleInfo

        start_time = time.time()
        modulelist = PythonModuleInfo().modulelist
        duration_time = time.time() - start_time

        self.response.write(
            "%s Modules found in %.2fsec.:" % (len(modulelist), duration_time)
        )
        self.response.write('<table>')
        Link = '<a href="%s' % self.URLs["action"]
        Link += '%s">more Info</a>'

        modulelist.sort()
        for modulename in modulelist:
            #~ if modei
            self.response.write("<tr>")
            self.response.write("<td>%s</td>" % modulename)
            self.response.write(
                '<td><a href="%s">more info</a></td>' % (
                    self.URLs.actionLink("module_info", modulename)
                )
            )
            self.response.write("</tr>")
        self.response.write("</table>")

    def module_info(self, function_info):
        module_name = function_info[0]

        back_link = (
            '<a href="%s">back</a>'
        ) % self.URLs.actionLink("python_modules")
        self.response.write(back_link)

        self.response.write("<h3>Modul info: '%s'</h3>" % module_name)

        try:
            t = imp.find_module(module_name)
        except Exception,e:
            self.response.write("Can't import '%s':" % module_name)
            self.response.write(str(e))
            return

        try:
            process = self.tools.subprocess2(
                "file %s" % t[1],
                "/",
                1
            )
        except Exception,e:
            fileinfo = "Can't get file-info: '%s'" % e
        else:
            try:
                fileinfo = process.out_data.split(":",1)[1]
            except:
                fileinfo = process.out_data

        self.response.write(back_link)
        self.response.write("<ul>")
        self.response.write("<li>pathname: %s</li>" % t[1])
        self.response.write("<li>description: %s</li>" % str(t[2]))
        self.response.write("<li>fileinfo: %s</li>" % fileinfo)
        self.response.write("</ul>")

        try:
            module = __import__( module_name )
        except Exception,e:
            self.response.write("<p>Can't import module ;(</p>")
            return
        else:
            self.response.write("<h4>help:</h4>")
            self.response.write("<pre>")

            old_stdout = sys.stdout
            try:
                sys.stdout = self.response
                help(module)
            finally:
                sys.stdout = old_stdout

            self.response.write("</pre>")

        if t[2][1] == "rb":
            self.response.write(
                "<p>(SourceCode not available. It's a binary module.)</p>"
            )
            return

        try:
            sourcecode = []
            filehandle = t[0]
            for i in filehandle:
                sourcecode.append(i)
            sourcecode = "".join(sourcecode)
        except Exception, e:
            self.response.write("Can't read Source:", e)
        else:
            self.response.write("<h4>SourceCode:</h4>")

            ext = t[2][0][1:] # Endung "extrahieren"
            self.render.highlight(ext, sourcecode)


    #_______________________________________________________________________
    # Informations-Methoden

    def session_data( self ):
        """ Session Informationen anzeigen """
        self.menu()
        self.response.write("<hr>")

        self.response.write("<h3>session data</h3>")
        self.response.write(
            '<fieldset id="system_info"><legend>your session data:</legend>'
        )
        self.response.write(
            '<table id="internals_session_data" class="internals_table">'
        )
        for k,v in self.session.iteritems():
            self.response.write("<tr>")
            self.response.write("<td>%s</td>" % k)
            self.response.write("<td>: %s</td>" % v)
            #~ self.response.write("%s:%s\n" % (k,v))
            self.response.write("</tr>")

        #~ result = self.db.select(
                #~ select_items    = ["session_data"],
                #~ from_table      = "session_data",
                #~ where           = [("session_id",self.session["session_id"])]
                #~ limit           = 10
            #~ )
        #~ for line in result:
            #~ self.response.write(str( line ).replace("\\n","<br/>"))

        self.response.write("</table>")
        self.response.write("</fieldset>")

    #_______________________________________________________________________

    def system_info( self ):
        """ Allgemeine System Informationen """
        self.menu()
        from PyLucid.buildin_plugins.show_internals.system_info \
                                                            import SystemInfo
        s = SystemInfo(self.request, self.response)
        s.display_all()

    def colubrid_debug(self):
        self.response.startFreshResponse()

        self.response.write("<h3>Colubrid debug information</h3>")
        self.response.write('<fieldset id="system_info"><legend>colubrid:</legend>')
        try:
            from colubrid.debug import debug_info
            self.response.write(debug_info(self.request))
        except Exception, e:
            self.response.write("(Error: %s)" % e)
        self.response.write("</fieldset>")

        return self.response

    #_______________________________________________________________________

    def sql_status( self ):
        self.menu()
        self.response.write("<hr>")

        self.response.write("<h3>SQL table status</h3>")

        SQLresult = self.db.process_statement("SHOW TABLE STATUS")

        self.response.write(
            '<table id="internals_log_information" class="internals_table">'
        )

        # Tabellen überschriften generieren
        self.response.write("<tr>")
        self.response.write("<th>name</th>")
        self.response.write("<th>entries</th>") # Rows)
        self.response.write("<th>update_time</th>")
        self.response.write("<th>size</th>")
        self.response.write("<th>overhang</th>") # data_free)
        self.response.write("<th>collation</th>")
        self.response.write("</tr>")

        total_rows = 0
        total_size = 0
        total_data_free = 0
        # eigentlichen Tabellen Daten erzeugen
        for line in SQLresult:
            self.response.write("<tr>")
            self.response.write("<td>%s</td>" % line["Name"])

            self.response.write(
                '<td style="text-align: right;">%s</td>' % line["Rows"]
            )
            total_rows += line["Rows"]

            self.response.write("<td>%s</td>" % line["Update_time"])

            size = line["Data_length"] + line["Index_length"]
            self.response.write(
                '<td style="text-align: right;">%s</td>' % \
                    filesizeformat(size)
            )
            total_size += size

            if line["Data_free"]>0:
                data_free_size = "%s" % \
                    filesizeformat(line["Data_free"])
            else:
                data_free_size = '-'
            self.response.write(
                '<td style="text-align: center;">%s</td>' % data_free_size
            )
            total_data_free += line["Data_free"]

            self.response.write("<td>%s</td>" % line["Collation"])
            #~ self.response.write("<td>%s</td>" % line["Comment"])
            self.response.write("</tr>")

        self.response.write('<tr style="font-weight:bold">')
        self.response.write("<td></td>")
        self.response.write(
            '<td style="text-align: right;">%s</td>' % total_rows
        )
        self.response.write("<td></td>")
        self.response.write(
            '<td style="text-align: right;">%s</td>' % \
                filesizeformat(total_size)
        )
        self.response.write(
            '<td style="text-align: center;">%s</td>' % \
                filesizeformat(total_data_free)
        )
        self.response.write("<td></td>")
        self.response.write("</tr>")

        self.response.write("</table>")

        self.response.write(
            '<p><a href="%s">optimize SQL tables</a></p>' % \
                self.URLs.actionLink("optimize_sql_tables")
        )


    #_______________________________________________________________________
    # Log Daten

    def log_data( self ):
        """ Logging Informationen anzeigen """
        self.menu()
        self.response.write("<hr>")

        limit = 100 # Anzahl der Einträge die angezeigt werden sollen

        result = self.db.get_last_logs(limit)

        self.response.write("<h3>log information (last %i)</h3>" % limit)
        self.response.write(
            self.tools.make_table_from_sql_select(
                result,
                id          = "internals_log_data",
                css_class   = "internals_table"
            )
        )



    #_______________________________________________________________________
    # Funktionen

    def optimize_sql_tables( self ):

        SQLresult = self.db.process_statement("SHOW TABLE STATUS")

        # Tabellen mit Überhang rausfiltern
        tables_to_optimize = []
        for line in SQLresult:
            if line["Data_free"]>0:
                # Tabelle hat Überhang
                tables_to_optimize.append( line["Name"] )

        if len(tables_to_optimize) > 0:
            self.response.write("<h3>optimize SQL tables</h3>")

            tables_to_optimize = ",".join( tables_to_optimize )

            SQLresult = self.db.process_statement(
                "OPTIMIZE TABLE %s" % tables_to_optimize
            )

            self.response.write(
                '<table id="optimize_table" class="internals_table">'
            )

            # Überschriften
            self.response.write("<tr>")
            for desc in SQLresult[0].keys():
                self.response.write("<th>%s</th>" % desc)
            self.response.write("</tr>")

            # Ergebniss Werte auflisten
            for line in SQLresult:
                self.response.write('<tr style="text-align: center;">')
                for value in line.values():
                    self.response.write("<td>%s</td>" % value)
                self.response.write("</tr>")

            self.response.write("</table>")
        else:
            self.page_msg( "All Tables already up to date." )

        self.sql_status()

    #_________________________________________________________________________

    def debug_plugin_data(self):
        self.page_msg.green("Debug all installed module/plugin data:")

        try:
            import cPickle as pickle
        except ImportError:
            import pickle

        #~ from PyLucid.components import plugin_cfg

        plugin_list = self.db.pluginsList(select_items=["*"])
        for id in plugin_list.keys():
            plugin_cfg = plugin_list[id]["plugin_cfg"]
            if plugin_cfg == None:
                continue

            data = plugin_cfg.tostring() # Aus der DB kommt ein array Objekt!
            data = pickle.loads(data)

            plugin_list[id]["plugin_cfg"] = data

        self.page_msg(plugin_list)




