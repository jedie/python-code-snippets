# -*- coding: utf-8 -*-

"""
Demux with eac3to
"""

import os, sys, glob, time, datetime, logging
from pprint import pprint

import Tkinter as tk

import win32api

from shared.config import VideoToolsConfig
from shared.tk_tools import askopenfilename2, askdirectory2, TkListbox
from shared.tools import make_slug, human_filesize, subprocess2

DEBUG = False
#DEBUG = True


VIDEO_EXT = ".mkv" # ToDo: Should go into the config

STREAMINFOS = [
    {
        "txt_filter": ("Chapters",),
        "ext": ".txt",
    },
    {
        "txt_filter": ("h264", "VC-1", "MPEG2",),
        "ext": VIDEO_EXT
    },
    {
        "txt_filter": ("DTS Hi-Res",),
        "ext": ".dtshr",
    },
    {
        "txt_filter": ("DTS",),
        "ext": ".dts",
    },
    {
        "txt_filter": ("TrueHD/AC3",),
        "ext": ".ac3",
    },
    {
        "txt_filter": ("Subtitle",),
        "ext": ".sup",
    },
]



class Drive(dict):
    def __init__(self, driveletter, cfg):
        self["letter"] = driveletter
        self.cfg = cfg

        self["vol_info"] = None
        self["lable"] = None

        self["stream_dir"] = os.path.join(driveletter, cfg["stream_dir"])

    def set_vol_info(self, vol_info):
        self["vol_info"] = vol_info
        self["lable"] = vol_info[0]
        
    def debug(self):
        print "_"*79
        print "Drive debug:"
        pprint(self)
        print "-"*79

    def __str__(self):
        return "<Drive '%s'>" % self["letter"]
#    def __repr__(self):
#        return self.__str__()








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

        def get_file_ext(stream_txt):
            def in_list(txt, l):
                for item in l:
                    if item in txt:
                        return True
                return False
            
            for stream_info in STREAMINFOS:
                if in_list(stream_txt, stream_info["txt_filter"]):
                    return stream_info["ext"]
                
            raise RuntimeError(
                "No STREAMINFOS entry matched for '%s'" % stream_txt
            )
        
        selected_streams = {}
        for stream_txt in stream_selection:
            try:
                ids = value_dict[stream_txt]
            except KeyError:
                print "Stream '%s' doesn't exist. Skip file." % stream_txt
                return
            
            file_ext = get_file_ext(stream_txt)
            
            for id in ids:
                filename = "%s - %i - %s%s" % (
                    self["name_prefix"],
                    id,
                    make_slug(stream_txt),
                    file_ext,
                )
                out_filepath = os.path.join(self["out_path"], filename)
                
                cmd.append("%i:" % id)
                cmd.append(out_filepath)
                        
        return cmd


    def parse_streaminfo(self, txt):
        self["streams"] = {}
        lines = txt.splitlines()
        lines = lines[1:]
        for line in lines:
            if DEBUG:
                print ">", line
            no, info = line.split(":",1)
            
            try:
                no = int(no)
            except ValueError:
                continue
            
            info = info.strip()
            
            self["streams"][no] = info
 

    def get_stream_info(self):
        """
        Run eac3to and cache the output data.
        """
        if os.path.isfile(self["eac3to_txt_path"]):
            print "Use existing eac3to output from cache file '%s'..." % (
                self["eac3to_txt_path"]
            )
            f = file(self["eac3to_txt_path"], "r")
            output = f.read()
            f.close()
        else:
            # run eac3to and save the output data into self["eac3to_txt_path"]
            cmd = [self.cfg["eac3to"], self["abs_path"]]
            print "run '%s'..." % " ".join(cmd)
            process, output = subprocess2(cmd)
            
            f = file(self["eac3to_txt_path"], "w")
            f.write(output)
            f.close()
            
        return output

    #-------------------------------------------------------------------------
    
    def debug(self):
        print "_"*79
        print "VideoFile debug:"
        pprint(self)
        print "-"*79

    def __str__(self):
        return "<File '%s'>" % self["abs_path"]


#------------------------------------------------------------------------------



def get_existing_drives(cfg):
    result = []
    for item in win32api.GetLogicalDriveStrings().split(chr(0)):
        if item:
            result.append(Drive(item, cfg))
    return result


def get_stream_dirs(drives):
    result = []
    for drive in drives:
        drive_letter = drive["letter"]
        try:
            vol_info = win32api.GetVolumeInformation(drive_letter)
        except Exception, err:
            print "Skip drive '%s': %s" % (drive_letter, err)
            continue

        if os.path.isdir(drive["stream_dir"]):
            drive.set_vol_info(vol_info)
            result.append(drive)

    return result



def choose_drive(cfg):
    """
    Choose a stream dir manuely.
    """
    path = askopenfilename2(
        title = "Choose the stream dir:",
        initialdir = cfg["last sourcedir"],
        filetypes = [('M2TS File','*.m2ts')],
    )
    
    vol_info = path.replace("\\", "_").replace(":","_") # Fallback
    for part in reversed(path.split(os.sep)[:-1]):
        # Use the last part of the path as a vol_info
        if part.upper() not in ("BDMV", "STREAM"):
            vol_info = part
            break
    
    drive = Drive(os.path.splitdrive(path)[0], cfg)
    drive["stream_dir"] = os.path.split(path)[0]
    drive.set_vol_info((vol_info,))
    
    drive.debug()
    
    drives = [drive,]
    
    cfg["last sourcedir"] = path
    
    return drives


#------------------------------------------------------------------------------


def get_stream_files(drives, cfg):
    files = []
    for drive in drives:
        print drive,
        path = drive["stream_dir"]
        print path
        if not os.path.isdir(path):
            print "Error: Path '%s' doesn't exist -> skip." % path
            continue
        
        glob_path = os.path.join(path, cfg["glob"])
        print "Looking in", glob_path
        file_list = glob.glob(glob_path)
        print "Files found:", file_list
        for abs_path in sorted(file_list):
            filename = os.path.basename(abs_path)
            
            stat = os.stat(abs_path)
            
            if stat.st_size < cfg["ignore_size"]:
                print "File '%s' to small -> ignore file complete" % filename
                continue

#            print (filename, drive, abs_path, stat, cfg)
            f = VideoFile(filename, drive, abs_path, stat, cfg)
            files.append(f)

    return files


def continue_loop(question="Continue (y/n) ?"):
    while True:
        print question
        char = raw_input().lower()
        if char == "y":
            return True
        elif char == "n":
            return False
        else:
            print "Wrong input ;)"



def select_videofiles(videofiles):
    """
    Select witch founded files should be recordnized.
    """
    activated = []
    item_list = []
    for index, videofile in enumerate(videofiles):
        filesize = videofile["stat"].st_size
        
        line = "%s - %s" % (videofile["abs_path"], human_filesize(filesize))
        item_list.append(line)
        
        if filesize>cfg["skip_size"]:
            activated.append(index)
    
#    size = stat.st_size
#    if size<cfg["skip_size"]:
#        # Skip small files
#        continue  
    
    lb = TkListbox(
        title = "Please select",
        lable = "Please select files witch should be converted:",
        items = item_list,
        activated = activated
    )
    print "selected items:"
    pprint(lb.selection) # list of selected items.
    
    curselection = lb.curselection # tuple containing index of selected items
    print "curselection:", curselection      
        
    new_list = [
        item
        for index, item in enumerate(videofiles)
        if index in curselection
    ]

    return new_list







    
def select_streams(videofiles):
    """
    select witch streams should be convert.
    """
    print "*"*79
    streams_txt = []
    for videofile in videofiles:
#        videofile.debug()
        for stream_txt in videofile["streams"].values():
            if not stream_txt in streams_txt:
                streams_txt.append(stream_txt)
#    
#    lb = TkListbox(
#        title = "Please select",
#        lable = "Please select streams:",
#        items = streams_txt
#    )
#    print lb.selection
    
    selection = TkListbox(
        title = "Please select",
        lable = "Please select streams:",
        items = streams_txt
    ).selection
    
    return selection

def convert_streams(videofile, stream_selection):
    print "convert_streams():", videofile, stream_selection
    videofile.debug()
    
    


if __name__ == "__main__":    
    cfg = VideoToolsConfig()
    cfg.debug()
    
    if DEBUG:
        print "DEBUG!!!"
        drive = Drive("d:", cfg)
        drive["stream_dir"] = r"d:\TEST\BDMV\STREAM"
        drive.set_vol_info(("TEST_LABLE",))
        drives = [drive,]
    else:
        # Scan all drive letters for stream dirs
        drives = get_existing_drives(cfg)
        drives = get_stream_dirs(drives)

    if not drives:
        print "No drives with stream files found -> choose manuel"
        drives = choose_drive(cfg)

    # Get from all path all m2ts files
    videofiles = get_stream_files(drives, cfg)

    # Select via Tk the files witch realy convert
    videofiles = select_videofiles(videofiles)
    
    if not videofiles:
        print "No stream files found -> abort, ok."
        sys.exit()

#    if not continue_loop():
#        print "Abort, ok."
#        sys.exit()

    for videofile in videofiles:
        print videofile

        videofile.create_outdir()

        output = videofile.get_stream_info()
        print "-"*80
        videofile.log("eac2to analyse output: %s" % output.lstrip("- "))
        videofile.parse_streaminfo(output)

        if videofile["streams"]:
            print "Streams found:", videofile["streams"]
        else:
            print "ERROR: No streams found!"
            continue
        


    stream_selection = select_streams(videofiles)
    print "selected streams:", stream_selection

    for videofile in videofiles:
        print videofile
        cmd = videofile.get_command(stream_selection)
        if cmd == None:
            print "No cmd -> Skip file."
            continue

        videofile.log("run: %s" % cmd)
        if DEBUG:
            print "DEBUG, skip real run..."
        else:
            process, output = subprocess2(cmd)
            videofile.log("eac2to output: %s" % output.lstrip("- "))

        videofile.close_log()
        print "-"*79

    print " -- END -- "