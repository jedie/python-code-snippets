# -*- coding: utf-8 -*-

"""
About Blu-ray Disc Folder and File Structure:
    http://www.videohelp.com/hd
"""

import os
import re
import sys
import win32api
from pprint import pprint

import m2ts
import tk_tools
import tools



#------------------------------------------------------------------------------

STREAM_DIR = "BDMV\\STREAM"
MPL_DIR    = "BDMV\\PLAYLIST"

class FileBase(object):
    def __init__(self, cfg, out_dir, path, filename):
        self.cfg = cfg
        self.out_dir = out_dir
        self.path = path
        self.filename = filename
        
        self.abs_path = os.path.join(path, filename)


class M2TS_File(FileBase):
    def __init__(self, *args, **kwargs):
        super(M2TS_File, self).__init__(*args, **kwargs)
        
        self.eac3to_cache = os.path.join(
            self.out_dir, "eac3to %s cache.txt" % self.filename
        )
        
        self.stat = os.stat(self.abs_path)
        self.size = self.stat.st_size
        
        self.streams = None      
        
    def read_streaminfo(self):
        self.stream_dict = m2ts.get_stream_info(
            self.cfg, self.abs_path, self.eac3to_cache
        )
    
    def __str__(self):
        return "M2TS File: %r - %r" % (self.path, self.filename)
    def __repr__(self):
        return "<%s>" % self.__str__()

    


class MoviePlayList(FileBase):
    def __init__(self, *args, **kwargs):
        super(MoviePlayList, self).__init__(*args, **kwargs)
        
        self.m2ts_no = None    # List of m2ts filenumbers, set in load_info()
        self.m2ts_files = None # Add in add_m2ts()
        self.size = None       # The total m2ts filesize, set in calc_site()
        
        self.eac3to_cache = os.path.join(
            self.out_dir, "eac3to %s cache.txt" % self.filename
        )
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir)
    
    def get_biggest_m2ts(self):
        return sorted(self.m2ts_files, key=lambda x: x.size, reverse=True)[0]
    
#    def get_source_cmd(self):
#        filelist = [m2ts.abs_path for m2ts in self.m2ts_files]
#        return "+".join(filelist)
    
    def get_stream_dict(self):
#        source_cmd = self.get_source_cmd()
        source_cmd = self.abs_path
        stream_dict = m2ts.get_stream_info(
            self.cfg, source_cmd, self.eac3to_cache
        )
        return stream_dict
    
    def human_size(self):
        if self.size == None:
            return "-"
        return tools.human_filesize(self.size)
    
    def add_m2ts(self, m2ts_file):
        if self.m2ts_files == None:
            # the first add
            self.m2ts_files = []
            self.size = 0
        
        if m2ts_file not in self.m2ts_files:
            self.m2ts_files.append(m2ts_file)
            self.size += m2ts_file.size
        
    def load_info(self):       
        f = file(self.abs_path, "rb")
        self.m2ts_no = re.findall(r"(\d+)M2TS", f.read())
        f.close()

    def __str__(self):
        txt = "Playlist %r " % self.filename
        if self.size == None:
            txt += "(No m2ts files added, yet.)"
        else:
            txt += "(total m2ts size: %s)" % self.human_size()
        return txt

    def __repr__(self):
        return "<%s>" % self.__str__()
        



#------------------------------------------------------------------------------




class BD(object):
    def __init__(self, cfg, root_path, movie_name):
        self.cfg = cfg
        self.root_path = root_path
        self.movie_name = movie_name
        
        self.stream_dir = os.path.join(self.root_path, STREAM_DIR)
        self.playlist_dir = os.path.join(self.root_path, MPL_DIR)
        self.out_dir = os.path.join(self.cfg["out_dir"], self.movie_name)
        
        self.m2ts = self.read_files(self.stream_dir, M2TS_File)
        self.mpls = self.read_files(self.playlist_dir, MoviePlayList)
        
    def read_files(self, path, FileClass):
        result = {}
        for fn in os.listdir(path):
            result[fn] = FileClass(self.cfg, self.out_dir, path, fn)
        return result
    
    def read_mpls_files(self):
        for fn, mpl_file in self.mpls.iteritems():
            print "read %r..." % fn
            mpl_file.load_info()
            
            print "m2ts Files:", mpl_file.m2ts_no
            
            # Attach the associated m2ts files to the playlist
            for m2ts_no in mpl_file.m2ts_no:
                filename = "%s.m2ts" % m2ts_no
                mpl_file.add_m2ts(self.m2ts[filename])
            
            print "m2ts total size:", mpl_file.human_size()
        print "-"*79
            
    
    #--------------------------------------------------------------------------

    def __str__(self):
        return "<Drive %r - %r>" % (self.root_path, self.movie_name)



def choose_BD_root(cfg):
    """
    Choose a stream dir manuely.
    """
    path = tk_tools.askopenfilename2(
        title = "Choose the BD root dir (.../BDMV/index.bdmv) :",
        initialfile = "index.bdmv",
        initialdir = os.path.join(cfg["last sourcedir"], "BDMV"),
        filetypes = [('BDMV contents file','*.bdmv')],
    )
    bd_root = os.path.split(os.path.split(path)[0])[0]
    
    if cfg["last sourcedir"] != bd_root:
        cfg["last sourcedir"] = bd_root
        cfg.save_config()
        
    print path
    
    lable = os.path.split(bd_root)[1]
    print "use movie lable:", lable
    
    return BD(cfg, bd_root, lable)
    




def autodetect_drive(cfg):
    for drive_letter in win32api.GetLogicalDriveStrings().split(chr(0)):
        if not drive_letter:
            continue
        print drive_letter

        try:
            vol_info = win32api.GetVolumeInformation(drive_letter)
        except Exception, err:
            print "Skip drive '%s': %s" % (drive_letter, err)
            continue
        
        print vol_info
        drive_lable = vol_info[0]
        
        if os.path.isdir(os.path.join(drive_letter, STREAM_DIR)):
            return BD(cfg, drive_letter, drive_lable)


def get_disc(cfg):
    # Scan all drive letters for stream dirs
    drive = autodetect_drive(cfg)

    if not drive:
        print "No drives with stream files found -> choose manually"
        drive = choose_BD_root(cfg)
       
    return drive



#------------------------------------------------------------------------------








class VideoFile(dict):
    def __init__(self, name, drive, abs_path, stat, cfg):
        self["name"] = name # Filename

        self["fn"], self.ext = os.path.splitext(self["name"])

        self["drive"] = drive # class "Drive"
        self["abs_path"] = abs_path # File path + filename
        self["stat"] = stat # os.stat
        
        self.cfg = cfg

        self["out_path"] = os.path.join(cfg["out_dir"], drive["lable"])
        if not os.path.isdir(self["out_path"]):
            os.makedirs(self["out_path"])

        self["name_prefix"] = self["name"].replace(".", "_")

        self["eac3to_txt_path"] = os.path.join(
            self["out_path"],
            "%s_eac3to.txt" % self["name_prefix"]
        )

        self["log_file_path"] = os.path.join(
            self["out_path"],
            "%s.log" % self["name_prefix"]
        )
        self._log_open = False

        self["streams"] = None # set in self.parse_streaminfo()

    def create_outdir(self):
        if not os.path.isdir(self["out_path"]):
            os.makedirs(self["out_path"])

    #-------------------------------------------------------------------------

    def log(self, txt):
        if self._log_open == False:
            self.log_file = file(self["log_file_path"], "a")
            self._log_open = True
            self.log("Start logging")
            
        dt = datetime.datetime.now()
        timestamp = dt.strftime("%d.%m.%Y %H:%M:%S")
        self.log_file.write("%s %s\n" % (timestamp, txt))
        self.log_file.flush()

    def close_log(self):
        self.log_file.close()

    #-------------------------------------------------------------------------

    def get_command(self, stream_selection):
        cmd = [self.cfg["eac3to"], self["abs_path"]]
        
        value_dict = {}
        for k,v in self["streams"].iteritems():
#            print k,v
            if v not in value_dict:
                value_dict[v] = []
        
            value_dict[v].append(k)
        
#        pprint(value_dict)

    def get_stream_info(self):
        """
        Run eac3to and cache the output data.
        """
        self["streams"] = m2ts.get_stream_info(
            self.cfg, self["abs_path"], self["eac3to_txt_path"]
        )

    #-------------------------------------------------------------------------
    
    def debug(self):
        print "_"*79
        print "VideoFile debug:"
        pprint(self)
        print "-"*79

    def __str__(self):
        return "<File '%s'>" % self["abs_path"]

