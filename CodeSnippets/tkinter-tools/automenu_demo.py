#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk
import tkMessageBox

from automenu import automenu


class AutoMenuDemoApp(object):
    """Die Beispielanwendung."""

    def __init__(self):
        self.root = tk.Tk()

        # example menu
        menudata = (
            [
                "_File", (
                    ("_New", "Control-n", self.new),
                    ("_Open...", "Control-o", self.open),
                    ("_Save", "Control-s", self.dummy),
                    (), # Add a separator here
                    ("_Exit","Alt-F4", self.destroy),
                ),
            ],
            [
                "_Edit", (
                    ("_Undo", "Control-z", self.dummy),
                    ("_Find", "F3", self.dummy),
                    ("F_ooBar", "Control-Shift-A", self.dummy),
                    ("Foo_Bar2","Alt-s", self.dummy),
                ),
            ],
            [
                "_Help", (
                    ("_Help", "F1", self.dummy),
                    (), # Add a separator here
                    ("_About", "", self.about),
                )
            ],
        )

        # Create menu
        automenu(self.root, menudata)

        # text field
        self.textfield = tk.Text(
            self.root, width = 79, height = 20,
        )
        self.textfield.pack()
        self.textfield.insert(tk.END, "automenu demo")

        self.root.mainloop()

    def dummy(self, *args):
        self.textfield.insert(
            tk.END, "\ndummy function.\n"
        )

    def new(self, *args):
        self.textfield.insert(tk.END, "\nFile/New\n")

    def open(self, *args):
        self.textfield.insert(tk.END, "\nFile/Open\n")

    def about(self, *args):
        tkMessageBox.showinfo(title = "about", message = "This is just a demo")

    def destroy(self, *args):
        close = tkMessageBox.askyesno(title="close?", message="Quit?")
        if close:
            self.root.destroy()

if __name__ == '__main__':
    AutoMenuDemoApp()