# -*- coding: utf-8 -*-

import os, sys
from pprint import pprint
from string import Template

import Tkinter as tk

from shared.config import VideoToolsConfig
from shared.tk_tools import askopenfilename2


def select_sourcefile(cfg):
    
    video_file_path = askopenfilename2(
        title = "Choose video source file:",
        initialdir = cfg["last sourcedir"],
        filetypes = cfg["videofiletypes"],
    )
    
    if video_file_path == "":
        sys.exit()
    path, filename = os.path.split(video_file_path)
    if path != cfg["last sourcedir"]:
        cfg["last sourcedir"] = path
        cfg.save_config()
        
    return video_file_path

class TemplateFile(object):
    def __init__(self, cfg, dirname, path):
        self.cfg = cfg
        self.dirname = dirname
        self.path = path
        
        rc_type, basename = dirname.split("-", 1)
        self.rc_type = rc_type.strip()
        self.basename = basename.strip()
    
    def files(self):
        for filename in os.listdir(self.path):
            abs_path = os.path.join(self.path, filename)
            if filename.startswith(".") or not os.path.isfile(abs_path):
                continue
            yield (filename, abs_path)
        
        
class Templates(list):
    def debug(self):
        print "_"*80
        print "Templates debug:"
        for item in self:
            print item.dirname
        print "-"*80


def select_template(cfg, video_file_path):
    template_dir = cfg["template dir"]
    
    templates = Templates()
    
    for item in os.listdir(template_dir):
        if item.startswith("."):
            continue
        
        item_path = os.path.join(template_dir, item)
        if not os.path.isdir(item_path):
            continue
        
        try:
            template = TemplateFile(cfg, item, item_path)
        except Exception, err:
            print "Error in template path '%s': %s -> skip" % (item_path, err)
        else: 
            templates.append(template)
        
    templates.debug()
    
    root = tk.Tk()
    root.title('Select Template')
    tk.Label(root, text="[%s]" % video_file_path).pack()
    tk.Label(root,
        text="Please select one template:",
        font = "Tahoma 9 bold",
    ).pack()

    var = tk.IntVar()
    for no, template in enumerate(templates):
        txt = "%s (Ratecontrol: '%s')" % (template.basename, template.rc_type)
        r = tk.Radiobutton(root, text=txt, variable=var, value=no)
        r.pack()

    tk.Button(root, text = "OK", command=root.destroy).pack(side=tk.RIGHT)
    tk.Button(root, text = "Abort", command=sys.exit).pack(side=tk.RIGHT)
    tk.mainloop()
    
    selection = var.get()
    template = templates[selection]
    return template




class Settings_x264(object):
    def __init__(self):
        self.base_settings = []
        self.extra_2pass = []
    
    def append_base(self, item):
        self.base_settings.append(item)
    def append_extra(self, item):
        self.extra_2pass.append(item)
      
    def get_base_string(self):
        return " ".join(self.base_settings)
    def get_extra_string(self):
        return " ".join(self.extra_2pass)
    
    get_firstpass_settings = get_base_string
    def get_finalpass_settings(self):
        return self.get_extra_string() + " " + self.get_firstpass_settings()    
    
    def debug(self):
        print "_"*79
        print "Settings_x264 debug:"
        print "base settings:", self.get_base_string()
        print "extra 2pass:", self.get_extra_string()
#        print " -"*40
#        print "get_firstpass_settings:", self.get_firstpass_settings()
#        print "get_finalpass_settings:", self.get_finalpass_settings()
        print "-"*79


def parse_x264_settings(filepath):
    extra_2pass = False
    x264_settings = Settings_x264()
    
    f = file(filepath, "r")
    for line in f:
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
        elif line.startswith("===="):
            extra_2pass = True
            continue
            
        if extra_2pass:
            x264_settings.append_extra(line)
        else:
            x264_settings.append_base(line)          

    f.close()
    
    return x264_settings
    

def select_setting_file(cfg):
    settings_dir = cfg["x264 settings dir"]
    
    settings = []
    
    for item in os.listdir(settings_dir):
        item_path = os.path.join(settings_dir, item)
        if not os.path.isfile(item_path):
            continue
        
        settings.append(item_path)
    
    root = tk.Tk()
    root.title('Select x264 settings')
    
    tk.Label(root, text="[%s]" % video_file_path).pack()
    tk.Label(root,
        text="Please select one x264 setting:",
        font = "Tahoma 9 bold",
    ).pack()

    var = tk.IntVar()
    for no, filename in enumerate(settings):
        r = tk.Radiobutton(root, text=filename, variable=var, value=no)
        r.pack()

    tk.Button(root, text = "OK", command=root.destroy).pack(side=tk.RIGHT)
    tk.Button(root, text = "Abort", command=sys.exit).pack(side=tk.RIGHT)
    tk.mainloop()
    
    selection = var.get()
    filepath = settings[selection]
    
    return filepath
    



def select_rate(cfg, video_file_path, template):
    key = "last %s" % template.rc_type
    last_values = cfg[key]
    print "last %s values: %r" % (template.rc_type, last_values)
    
    root = tk.Tk()
    root.title('Input %s' % template.rc_type)
    tk.Label(root, text="[%s]" % video_file_path).pack()
    tk.Label(root,
        text="Please input the %s value for encoding:" % template.rc_type,
        font = "Tahoma 9 bold",
    ).pack()
    
    # Value input field
    var = tk.StringVar(root)
    var.set(last_values[0]) # insert last used value
    tk.Entry(root, textvariable = var).pack()
    
    tk.Label(root,
        text="Last %s values are: %r" % (template.rc_type, last_values)
    ).pack()
    
    # Buttons
    tk.Button(root, text = "OK", command=root.destroy).pack(side=tk.RIGHT)
    tk.Button(root, text = "Abort", command=sys.exit).pack(side=tk.RIGHT)
    
    tk.mainloop()
    
    new_value = int(var.get())
    
    if new_value != last_values[0]:
        # insert the new value into the "old values list"
        cfg[key].insert(0, new_value)
        cfg[key] = cfg[key][:cfg["max save"]] # Cut to mutch values
        cfg.save_config()
    
    return new_value


def render(filename, context):
    f = file(filename, "r")
    template = f.read()
    f.close()
    
    t = Template(template)
    return t.substitute(context)


def write_file(sourcefile, context, destination):
    content = render(sourcefile, context)
    print "Write '%s'..." % destination,
    f = file(destination, "w")
    f.write(content)
    f.close()
    print "OK"


def create_files(cfg, video_file_path, template, rate_value, x264_settings):
    template_dir = cfg["template dir"]
    
    basename = os.path.splitext(os.path.basename(video_file_path))[0]
    destination_path, video_filename = os.path.split(video_file_path)
    
    print "destination_path:", destination_path
    
    context = {
        "video_file_path": video_file_path,
        "video_filename": video_filename,
        "basename": basename,
        "rate_value": rate_value,
        "x264": cfg["x264"],
        
        "firstpass": x264_settings.get_firstpass_settings(),
        "finalpass": x264_settings.get_finalpass_settings(),     
    }
    print "context:"
    pprint(context)

    # Copy all files
    for filename, filepath in template.files():
        print filename
        print filepath

        dest_name = "%s %s" % (basename, filename)
        destination = os.path.join(destination_path, dest_name)
        
        write_file(filepath, context, destination)
        


if __name__ == "__main__":
    cfg = VideoToolsConfig()
    cfg.debug()
    
    if len(sys.argv)>1:
        video_file_path = sys.argv[1]
    else:
        video_file_path = select_sourcefile(cfg)
    
    if not os.path.isfile(video_file_path):
        print "Error: File '%s' doesn't exist!" % video_file_path
        sys.exit()
    
    template = select_template(cfg, video_file_path)
    print "Template:"
    pprint(template)
    
    filepath = select_setting_file(cfg)
    
    x264_settings = parse_x264_settings(filepath)
    x264_settings.debug()
    
    rate_value = select_rate(cfg, video_file_path, template)
    print "rate value:", rate_value
    
    create_files(cfg, video_file_path, template, rate_value, x264_settings)
    
    print " -- END -- "