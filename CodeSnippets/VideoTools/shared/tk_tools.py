# -*- coding: utf-8 -*-

import os, sys

import Tkinter as tk
from tkFileDialog import askopenfilename, askdirectory



def _ask(method, *args, **kwargs):
    root = tk.Tk()
    kwargs["parent"] = root
    path = method(*args, **kwargs)
    root.destroy()
    
    if path == "": # Nothing selected.
        sys.exit()
    
    return os.path.normpath(path)

def askdirectory2(*args, **kwargs):
    return _ask(askdirectory, *args, **kwargs)


def askopenfilename2(*args, **kwargs):
    return _ask(askopenfilename, *args, **kwargs)


def simple_input(title, pre_lable, init_value, post_lable):
    """
    bsp.:
    new_value = simple_input(      
        title="The window title",
        pre_lable="Please input:",
        init_value=old_value,
        post_lable="(in Bytes)",
    )
    """   
    root = tk.Tk()
    root.title(title)
    
    tk.Label(root, text=pre_lable).pack()
    
    # Value input field
    var = tk.StringVar(root)
    var.set(init_value)
    tk.Entry(root, textvariable = var).pack()
    
    tk.Label(root, text=post_lable).pack()
    
    # Buttons
    tk.Button(root, text = "OK", command=root.destroy).pack(side=tk.RIGHT)
    tk.Button(root, text = "Abort", command=sys.exit).pack(side=tk.RIGHT)
    
    tk.mainloop()
    
    return var.get()



class TkListbox(object):
    """
    Simple Tkinter listbox.
    example:

        streams_txt = ["one", "two", "three"]

        lb = TkListbox(
            title     = "Please select",
            lable     = "Please select streams:",
            items     = streams_txt,
            activated = (0,2), # Preselect "one" and "three"
        )
        print lb.curselection # tuple containing index of selected items
        print lb.selection # list of selected items.
    """
    def __init__(self, title, lable, items, activated=[], \
                                            selectmode=tk.MULTIPLE, width=100):
        self.selection = []
        self.items = items

        self.root = tk.Tk()
        self.root.title(title)
        tk.Label(self.root, text=lable, font = "Tahoma 9 bold").pack()

        self.listbox = tk.Listbox(
            self.root, selectmode=selectmode, height=len(items), width=width
        )
        self.listbox.pack()

        for txt in self.items:
            self.listbox.insert(tk.END, txt)

        for index in activated:
            self.listbox.selection_set(index)

        b = tk.Button(self.root, text = "OK", command=self.save_selection)
        b.pack(side=tk.RIGHT)
        b = tk.Button(self.root, text = "Abort", command=sys.exit)
        b.pack(side=tk.RIGHT)

        tk.mainloop()

    def save_selection(self):
        self.curselection = [int(i) for i in self.listbox.curselection()]
        self.selection = []
        for index in self.curselection:
            self.selection.append(self.items[index])

        self.root.destroy()

