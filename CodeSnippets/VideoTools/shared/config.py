# -*- coding: UTF-8 -*-


import os, sys, pickle
from pprint import pprint
from ConfigParser import RawConfigParser

from tools import askopenfilename2, askdirectory2


CONFIG_FILENAME = "config.dat"

DEFAULT_CONFIG = {
    "out_dir": "",

    "skip_size": 100 * 1024 * 1024,
    "stream_dir": "BDMV\\STREAM",
    "out_video_ext": "mkv",
    
    "last bitrate": [6730, ],
    "last crf": [17, ],
    "max save": 5, # How many values should be saved?
    
    "last sourcedir": None,

    "videofiletypes": [
        ('MKV File','*.mkv'),
        ('AVI File','*.avi'),
    ],
    
    "x264 settings dir": "x264 settings",
    "template dir": "templates",
}

EXE_FILES = ("eac3to", "x264")


class PickleConfig(dict):

    def __init__(self):
        self.update(DEFAULT_CONFIG)
        
        if os.path.isfile(CONFIG_FILENAME):
            try:
                f = file(CONFIG_FILENAME, "r")
            except IOError, err:
                print "Error reading config:", err
            else:
                pickle_data = pickle.load(f)
                f.close()
                self.update(pickle_data)

    def save_config(self):
        print "Save config to '%s'..." % CONFIG_FILENAME,
        f = file(CONFIG_FILENAME, "w")
        pickle.dump(self, f)
        f.close()
        print "OK"

    def debug(self):
        print "Debug config:"
        pprint(self)
        print "-"*80



class VideoToolsConfig(PickleConfig):
    def __init__(self):
        super(VideoToolsConfig, self).__init__()
        
        # Check/set the path to all EXE files
        for filename in EXE_FILES:
            while not os.path.isfile(self.get(filename, "")):
                fullname = "%s.exe" % filename
                
                self[filename] = askopenfilename2(
                    title = "Please select '%s':" % fullname,
                    initialfile=fullname,
                    filetypes=[('EXE Files','*.exe')]
                )
                self.save_config()
        
        self.out_dir_set = False
        if not os.path.isdir(self["out_dir"]):
            self.ask_out_dir()
            
    def ask_out_dir(self):
        if os.path.isdir(self["out_dir"]):
            initdir = self["out_dir"]
        else:
            initdir = "%s\\" % os.path.splitdrive(os.getcwd())[0]
            
        self["out_dir"] = askdirectory2(
            title = "Please select the out base directory:",
            initialdir = initdir,
        )
        self.out_dir_set = True
        self.save_config()
        

if __name__ == "__main__":
    from pprint import pprint

    CONFIG_FILENAME = "config_test.ini"
    if os.path.isfile(CONFIG_FILENAME):
        os.remove(CONFIG_FILENAME)

    # Simple Test
    c = PickleConfig()
    c.debug()
    print "-"*80
    # Change values:
    c["skip_size"] = 500
    c["stream_dir"] = "A/TEST/"
    c.save_config()
    c.debug()
    print "-"*80
    # Reopen the written ini file:
    c = PickleConfig()
    c.debug()