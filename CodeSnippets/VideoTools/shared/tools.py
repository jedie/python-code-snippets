# -*- coding: utf-8 -*-

import os

import Tkinter as tk
from tkFileDialog import askopenfilename


def askopenfilename2(*args, **kwargs):
    root = tk.Tk()
    kwargs["parent"] = root
    path = askopenfilename(*args, **kwargs)
    root.destroy()
    
    if path != "":
        path = os.path.normpath(path)
    
    return path