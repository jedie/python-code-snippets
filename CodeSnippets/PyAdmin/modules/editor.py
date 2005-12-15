#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.2"

#~ import cgitb ; cgitb.enable()
import os, sys, locale

import CompressedOut, CGIdata

MyOut = CompressedOut.AutoCompressedOut( "gzip" )

htmlPre = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=%(charset)s" />
<title>editor @ %(uname)s</title>
<script type="text/javascript">
</script>
<style type="text/css">
* {
	font-family:tahoma, arial, sans-serif;
}
#cmd {
   background-color:#FFEEEE;
}
#cmd:focus {
   background-color:#EEFFEE;
}
body {
    font-size: 0.9em;
    background-color: #CCCCCC;
    padding: 5px;
    margin: 5px;
}
textarea {
    font-family: "Courier New", Courier, mono;
    font-size: 0.9em;
}
</style>
</head>
<body>'''

htmlPost = '''
<form name="form" id="form" method="post" action="%(self)s">
  <p>
    <input name="edit_file" type="text" id="edit_file" value="%(file_name)s" size="80" />
    <input name="edit" type="submit" id="edit" value="edit" />
  <br />
    <textarea name="textfield" cols="120" rows="28">%(file_content)s</textarea>
  <br />
      <input name="backup" type="checkbox" id="backup" value="backup" checked="checked" />
      backup edit file
  <br />
    <input name="save" type="submit" id="save" value="save" />
    <a href="FileBrowser?cwd=%(cwd)s">exit to FileBrowser</a>
  </p>
</form>
</body>
</html>'''











def get_edit_file( edit_file ):
    "Dateiinhalt auslesen"
    if not os.path.isfile( edit_file ):
        print "edit_file [%s] not found!" % edit_file
        sys.exit()
    f = file( edit_file, "r" )
    txt = f.read()
    f.close()
    return txt

def save_new_content( file_name, content, backup = True ):
    "Neuen Inhalt in Datei schreiben"
    if backup:
        name, ext = os.path.splitext( file_name )
        backup_file = name + ".bak"
        print "Make backup [%s] -&gt; [%s]<br>" % ( file_name, backup_file )

        #~ if os.path.exists( backup_file ):
            #~ print "Error: backup file exists!"
            #~ sys.exit()

        from shutil import copyfile
        try:
            copyfile( file_name, backup_file )
        except IOError:
            print "Error: can't create backup file!"
            sys.exit()

    print "Save new content..."
    f = file( file_name, "w" )
    f.write( content )
    f.close()
    print "OK"
    sys.exit()






def start_module( selfURL ):
    # HTML-Pre Ausgeben
    print htmlPre % {
        "charset"       : locale.getdefaultlocale()[1],
        "uname"         : os.uname()
    }

    if CGIdata.has_key("exit"):
        print "EXIT!"
        sys.exit()



    if CGIdata.has_key("edit_file"):
        file_name = CGIdata["edit_file"]
    else:
        file_name = ""



    file_content = ""
    if CGIdata.has_key("edit"):
        "Eine neue Datei soll editiert werden"
        if file_name == "":
            print "no file specified!"
            sys.exit()
        file_content = get_edit_file( CGIdata["edit_file"] )


    if CGIdata.has_key("save"):
        "Änderungen sollen abgespeichert werden"
        if file_name == "":
            print "no file specified!"
            sys.exit()

        if CGIdata.has_key("backup"):
            backup_oldfile = True
        else:
            backup_oldfile = False


        print "save [%s]<br>" % file_name
        print "Backup:", backup_oldfile
        print "<hr>"
        if not CGIdata.has_key("textfield"):
            print "error no textfield found!"
            sys.exit()

        new_content = CGIdata["textfield"].strip()
        print "<pre>%s</pre>" % new_content
        print "<hr>"
        save_new_content( file_name, new_content, backup_oldfile )



    print htmlPost % {
        "self"          : selfURL,
        "file_content"  : file_content,
        "file_name"     : file_name,
        "cwd"           : os.path.split( file_name )[0]
        }



if __name__ == "__main__":
    CGIdata = CGIdata.GetCGIdata()
    selfURL = os.environ['SCRIPT_NAME']
    start_module( selfURL )

def inetd_start():
    "durch inetd-Server gestartet"
    selfURL = "editor"
    start_module( selfURL )








