#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import wx

import os
from ConfigParser import ConfigParser

from ExifTool_GUI import FileHandler, ExifTool
from ExifTool_routines import process, WrongPathError

CONFIG_FILENAME = "ExifTool.ini"
DEFAULT_CONFIG = {
    "source_path": os.getcwd(),
    "dest_path": os.getcwd(),
}

class Out(object):
    def __init__(self, text_ctrl):
        self.text_ctrl = text_ctrl

    def write(self, txt):
        self.text_ctrl.AppendText("%s\n" % txt)

    def __call__(self, *args):
        for txt in args:
            self.text_ctrl.AppendText(str(txt))
        self.text_ctrl.AppendText("\n")



class FileHandler(FileHandler):

    _cfg_section = "path"

    def __init__(self, *args, **kwargs):
        super(FileHandler, self).__init__(*args, **kwargs)
        self.msg = Out(self.output)
        self.msg("init...")

        self.cfg = ConfigParser(DEFAULT_CONFIG)
        self.init_config()

    #___________________________________________________________________

    def init_config(self):
        self.cfg.read(CONFIG_FILENAME)

        if not self.cfg.has_section(self._cfg_section):
            self.cfg.add_section(self._cfg_section)

        def set_path(ctrl, txt):
            path = self.cfg.get(self._cfg_section, txt)
            self.set_path(ctrl, path)

        set_path(self.source_path, "source_path")
        set_path(self.dest_path, "dest_path")

    def save_config(self):
        def save(ctrl, txt):
            path = ctrl.GetValue()
            self.cfg.set(self._cfg_section, txt, path)

        save(self.source_path, "source_path")
        save(self.dest_path, "dest_path")

        fp = file(CONFIG_FILENAME, "w")
        self.cfg.write(fp)
        fp.close()

    #___________________________________________________________________

    def set_path(self, ctrl, path):
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            self.msg("Path '%s' doesn't exist." % path)
            return

        ctrl.SetValue(path)

    #___________________________________________________________________

    def _set_path(self, ctrl, txt):
        defaultPath = ctrl.GetValue()
        if not os.path.isdir(defaultPath):
            defaultPath = os.getcwd()

        dlg = wx.DirDialog(
            self, "Choose the %s path" % txt,
            defaultPath = defaultPath,
            style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            path = os.path.normpath(path)
            if path != ctrl.GetValue():
                self.msg("set %s path to: %s" % (txt, path))
                self.set_path(ctrl, path)

        dlg.Destroy()

    def set_source_path(self, event):
        self._set_path(self.source_path, "source")

    def set_dest_path(self, event):
        self._set_path(self.dest_path, "destination")

    #___________________________________________________________________

    def on_start(self, event):
        self.msg("start")

        source_path = self.source_path.GetValue()
        dest_path = self.dest_path.GetValue()

        simulate = self.simulate.GetValue()
        move_files = self.move_files.GetValue()
        copy_files = self.copy_files.GetValue()

        self.msg("simulate:", simulate)
        self.msg("move:", move_files)
        self.msg("copy:", copy_files)

        try:
            process(
                source_path, dest_path, self.msg, simulate,
                move_files, copy_files
            )
        except WrongPathError, e:
            self.msg("Error, wrong path:", e)


    def on_exit(self, event):
        self.save_config()
        self.Close()


class ExifTool(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        file_handler = FileHandler(None, -1, "")
        self.SetTopWindow(file_handler)
        file_handler.Show()
        return 1

if __name__ == "__main__":
    exif_tool = ExifTool(0)
    exif_tool.MainLoop()
