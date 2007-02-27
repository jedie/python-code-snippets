#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
EvilEval - a PyLucid Plugin

Created by Jens Diemer
license: GNU General Public License (GPL)

 - execute Python
 - execute commands on the shell

Inspired of code from the package:
colubrid.debug by Armin Ronacher, Benjamin Wiegand, Georg Brandl
"""



__version__ = "$Rev: 0 $"

__ToDo__ = """
"""


import os, sys, traceback, time

select_function = """
<ul>
    <li>
        <a href="%(python_url)s">execute Python code</a><br />
        with <em>Python v%(sysversion)s</em>
    </li>
    <li>
        <a href="%(shell_url)s">execute shell commands</a><br />
        as <em title="Username">%(userinfo)s</em> on <em title="os uname">%(osuname)s</em>
    </li>
</ul>
<h2>Note:</h2>
<ul>
    <li>This is a potential safety hole!</li>
    <li>For security reasons, you should deactivate that plugin, if you do not need it any longer!</li>
</ul>
"""

python_input_form = """Execute code with Python v%(sysversion)s:<br />
<form method="post" action="%(url)s">
    <textarea name="codeblock" rows="10" style="width: 95%%;">%(old_code)s</textarea>
    <br />
    <label for="pylucid_access">access to pylucid objects:</label>
    <input name="pylucid_access" value="1" type="checkbox" checked="checked">
    <br />
    <input value="execute" name="execute" type="submit">
</form>
<p>
    With access to pylucid objects you can use this objects:<br />
    <p>%(objectlist)s</p>
    Use <em>help(object)</em> for more information ;)
</p>
"""

shell_input_form = """Execute a command as <em title="Username">%(userinfo)s</em> on <em title="os uname">%(osuname)s</em><br />
<form method="post" action="%(url)s">
    <label for="command">page name:</label>
    <input name="command" value="" maxlength="255" type="text" style="width: 95%%;">
    <input value="execute" name="execute" type="submit">
</form>
"""


from PyLucid.tools.out_buffer import Redirector
from PyLucid.system.BaseModule import PyLucidBaseModule


class EvilEval(PyLucidBaseModule):

    def lucidTag(self):
        #~ self.response.debug()
        try:
            osuname = " ".join(os.uname())
        except AttributeError:
            # Windows?!?
            osuname = ""
        context = {
            "python_url": self.URLs.actionLink("python"),
            "shell_url": self.URLs.actionLink("shell"),
            "sysversion": sys.version,
            "userinfo": self._userinfo(),
            "osuname": osuname,
        }
        self.response.write(select_function % context)

    def _userinfo(self):
        try:
            return os.getlogin()
        except Exception,e:
            return "[os.getlogin error: %s]" % e

    #_________________________________________________________________________

    def python(self):
        """ Führt Python code aus """

        if "codeblock" in self.request.form:
            # abgeschickter code ausführen
            old_code = self.exec_python()
        else:
            old_code = (
                "for i in xrange(5):\n"
                "    print 'This is cool', i"
            )

        objectlist = self._get_objectlist()

        context = {
            "url": self.URLs.actionLink("python"),
            "sysversion": sys.version,
            "old_code": old_code,
            "objectlist": ", ".join(objectlist),
        }
        self.response.write(python_input_form % context)

    def exec_python(self):
        try:
            codeblock = self.request.form["codeblock"]
        except KeyError:
            # Noch kein code abgeschickt
            return ""

        codeblock = codeblock.replace("\r\n", "\n") # Windows

        self.exec_code(codeblock)

        #~ self.page_msg(codelines)
        return codeblock

    def exec_code(self, sourcecode):

        start_time = time.time()

        stdout_redirector = Redirector(self.page_msg)
        globals = {}
        locals = {}

        try:
            code = compile(sourcecode, "<stdin>", "exec", 0, 1)
            if "pylucid_access" in self.request.form:
                exec code
            else:
                exec code in globals, locals
        except:
            etype, value, tb = sys.exc_info()
            tb = tb.tb_next
            msg = ''.join(traceback.format_exception(etype, value, tb))
            sys.stdout.write(msg)

        output = stdout_redirector.get()

        duration = time.time() - start_time

        self.response.write(
            "<fieldset><legend>executed in %.3fsec.:</legend>" % duration
        )
        self.response.write("<pre>")
        self.response.write(output)
        self.response.write("</pre></fieldset>")

    def _get_objectlist(self):
        objectlist = []
        for obj in dir(self):
            if obj.startswith("_"):
                continue
            objectlist.append("self.%s" % obj)
        return objectlist

    #_________________________________________________________________________

    def shell(self):
        """ Führt einen Befehl auf der shell aus """

        if "command" in self.request.form:
            # abgeschickter Befehl ausführen
            self.run_command()

        try:
            userinfo = os.getlogin()
            osuname = " ".join(os.uname())
        except AttributeError:
            # Windows?!?!
            userinfo = ""
            osuname = "[Windows ?]"

        context = {
            "url": self.URLs.actionLink("shell"),
            "userinfo": userinfo,
            "osuname": osuname,
        }
        self.response.write(shell_input_form % context)

    def run_command(self):

        command = self.request.form["command"]

        start_time = time.time()

        timeout = 5
        process = self.tools.subprocess2(command, ".", timeout)

        output = process.out_data

        duration = time.time() - start_time

        self.response.write(
            "<fieldset><legend>executed in %.3fsec.:</legend>" % duration
        )
        self.response.write("<pre>")
        self.response.write(output)
        self.response.write("</pre></fieldset>")

        if process.killed == True:
            self.page_msg(
                result, process.returncode,
                "Error: subprocess timeout (%.2fsec.>%ssec.)" % (
                    time.time()-start_time, timeout
                )
            )

        if process.returncode != 0 and process.returncode != None:
            self.page_msg(result, process.returncode, "subprocess Error!")
