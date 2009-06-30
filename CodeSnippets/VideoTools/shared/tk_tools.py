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
    
    if isinstance(path, tuple):
        return [os.path.normpath(i) for i in path]
    else:
        return os.path.normpath(path)

def askdirectory2(*args, **kwargs):
    return _ask(askdirectory, *args, **kwargs)


def askopenfilename2(*args, **kwargs):
    return _ask(askopenfilename, *args, **kwargs)

def askopenfilename3(title, initialfile, filetypes):
    file_path = askopenfilename2(
        title=title,
        initialfile=initialfile,
        filetypes=filetypes,
    )
    if file_path == "":
        sys.exit()
    else:
        return file_path

def askfilepath(filename):
    return askopenfilename3(
        title = "Please select '%s':" % filename,
        initialfile=filename,
        filetypes=[(filename,filename)]
    )

def simple_input(title, pre_lable, init_value, post_lable=""):
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



def simple_select(items, title="Select", text="Please select:"):
    root = tk.Tk()
    root.title(title)
    tk.Label(root, text=text, font = "Tahoma 9 bold").pack()

    var = tk.IntVar()
    for no, item in enumerate(items):
        r = tk.Radiobutton(root, text=item, variable=var, value=no)
        r.pack()

    tk.Button(root, text = "OK", command=root.destroy).pack(side=tk.RIGHT)
    tk.Button(root, text = "Abort", command=sys.exit).pack(side=tk.RIGHT)
    tk.mainloop()
    
    selection = var.get()
    selected_item = items[selection]
    return selected_item