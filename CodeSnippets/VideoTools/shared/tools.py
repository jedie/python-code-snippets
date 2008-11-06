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
