# -*- coding: utf-8 -*-

"""
    Tkinter automenu
    ~~~~~~~~~~~~~~~~
    
    A menu generator for simple Tkinter apps.
    See automenu_demo.py
"""

import Tkinter as tk


def automenu(master, menudata):
    def prepstr(label, used):
        """
        Based on prepstr() from python/Lib/idlelib/EditorWindow.py
        Helper to extract the underscore from a string, e.g.
        prepstr("Co_py") returns (2, "Copy").
        Check if the used character is unique in the menu part.
        """
        i = label.find('_')
        if i >= 0:
            label = label[:i] + label[i+1:]

            char = label[i]
            assert char not in used, (
                "underline %r used in %r is not unique in this menu part!"
            ) % (char, label)
            used.append(char)

        return i, label

    # Add a menubar to root
    menubar = tk.Menu(master)
    master.config(menu=menubar)

    used_topunderline = []
    for toplabel, menuitems in menudata:
        # add new main menu point
        menu = tk.Menu(menubar, tearoff=False)
        underline, toplabel = prepstr(toplabel, used_topunderline)
        menubar.add_cascade(label=toplabel, menu=menu, underline=underline)

        # add all sub menu points
        used_underlines = []
        for index, menudata in enumerate(menuitems):
            if not menudata:
                menu.add_separator()
                continue

            label, keycode, command = menudata

            underline, label = prepstr(label, used_underlines)

            menu.add_command(label=label, underline=underline, command=command)
            if keycode:
                menu.entryconfig(index, accelerator=keycode)
                master.bind("<"+keycode+">", command)



if __name__ == '__main__':
    from automenu_demo import AutoMenuDemoApp
    AutoMenuDemoApp()
