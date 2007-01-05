#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
plugin_cfg Example

$LastChangedDate: 2007-01-04 16:41:47 +0100 (Do, 04 Jan 2007) $
$Author: jensdiemer $
"""

__version__ = "$Rev: 724 $"

HTML = """
<form method="post" action="%(url)s">
    data1: <input name="data1" value="%(data1)s" size="20" type="text">
    <br />
    data2: <input name="data2" value="%(data2)s" size="20" type="text">
    <br />
    <input type="submit" name="update" value="update" />
</form>
"""

from PyLucid.system.BaseModule import PyLucidBaseModule

class PluginCfgExample(PyLucidBaseModule):

    def lucidTag(self):

        if "update" in self.request.form:
            # update the plugin_cfg data
            self.plugin_cfg["data1"] = self.request.form.get("data1", "")
            self.plugin_cfg["data2"] = self.request.form.get("data2", "")
            self.page_msg.green("data updated.")
        else:
            self.page_msg("Used old data from db.")

        # Display the current saved plugin_cfg data
        page = HTML % {
            "url":self.URLs.currentAction(),
            "data1": self.plugin_cfg["data1"],
            "data2": self.plugin_cfg["data2"],
        }
        self.response.write(page)
