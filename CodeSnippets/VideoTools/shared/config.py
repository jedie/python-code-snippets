# -*- coding: UTF-8 -*-


import os, sys, pickle
from pprint import pprint
from ConfigParser import RawConfigParser

from tk_tools import askopenfilename2, askdirectory2, askfilepath


CONFIG_FILENAME = "config.dat"

DEFAULT_CONFIG = {
    "out_dir": "",

    "glob": "*.m2ts",
    "skip_size": 500 * 1024 * 1024,   # Smaller files are not selected
    "ignore_size": 200 * 1024 * 1024, # Smaller files complete ignored
    "stream_dir": "BDMV\\STREAM",
    "out_video_ext": "mkv",
    
    "last bitrate": [6730, ],
    "last crf": [17, ],
    "max save": 5, # How many values should be saved?
    
    "last sourcedir": None,

    "videofiletypes": [
        ('MKV File','*.mkv'),
        ('M2TS File','*.m2ts'),
        ('AVI File','*.avi'),
    ],
    
    "x264 settings dir": "x264 settings",
    "template dir": "templates",
}

# Use external programs. google to find the download links ;)
EXE_FILES = ("eac3to", "x264", "BeSweet", "aften", "sox")


class PickleConfig(dict):

    def __init__(self, filename, defaults={}):
        self.filename = filename
        
        self.update(defaults)
        
        if not os.path.isfile(self.filename):
            print "Info: Config file '%s' doesn't exist, yet." % self.filename
        else:
            print "Reading '%s'..." % self.filename
            try:
                f = file(filename, "r")
            except IOError, err:
                print "Error reading config:", err
            else:
                pickle_data = pickle.load(f)
                f.close()
                self.update(pickle_data)
        

    def save_config(self):
        print "Save '%s'..." % self.filename,
        f = file(self.filename, "w")
        pickle.dump(self, f)
        f.close()
        print "OK"

    def debug(self):
        print "PickleConfig debug:"
        pprint(self)
        print "-"*80









class VideoToolsConfig(PickleConfig):
    def __init__(self):
        super(VideoToolsConfig, self).__init__(CONFIG_FILENAME, DEFAULT_CONFIG)
        
        # Check/set the path to all EXE files
        for filename in EXE_FILES:
            self.get_filepath(filename)
        
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
        

    def get_filepath(self, filename):
        if filename in self:
            old_path = self[filename]
            if os.path.isfile(old_path) == True:
                return old_path
        
        filepath = askfilepath(filename + ".exe")
        if os.path.isfile(filepath):
            self[filename] = filepath
            self.save_config()
            return filepath
        

if __name__ == "__main__":
    from pprint import pprint

    test_config = "config_test.ini"
    if os.path.isfile(test_config):
        os.remove(test_config)

    # Simple Test
    c = PickleConfig(test_config, DEFAULT_CONFIG)
    c.debug()
    print "-"*80
    # Change values:
    c["skip_size"] = 500
    c["stream_dir"] = "A/TEST/"
    c.save_config()
    c.debug()
    print "-"*80
    # Reopen the written ini file:
    c = PickleConfig(test_config)
    c.debug()