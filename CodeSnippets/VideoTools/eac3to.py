# -*- coding: utf-8 -*-

"""
Demux with eac3to
"""

import os, sys, time, datetime, subprocess, logging

import win32api

from shared.config import VideoToolsConfig
from shared.tools import askopenfilename2, askdirectory2

DEBUG = False
#DEBUG = True


class StreamInfo(object):
    def __init__(self, filename, txt_filter, parameter=[]):
        self.filename = filename
        self.txt_filter = txt_filter
        self.parameter = parameter

    def __str__(self):
        return "<StreamInfo %s (%s)>" % (
            self.filename, self.parameter
        )
    def __repr__(self):
        return self.__str__()


VIDEO_EXT = "mkv" # ToDo: Should go into the config

STREAMINFOS = [
    StreamInfo(
        filename = "chapters.txt",
        txt_filter = ("Chapters",),
    ),
    StreamInfo(
        filename = "h264."+VIDEO_EXT,
        txt_filter = ("h264",),
    ),
    StreamInfo(
        filename = "VC1."+VIDEO_EXT,
        txt_filter = ("VC-1",),
    ),
    StreamInfo(
        filename = "MPEG2."+VIDEO_EXT,
        txt_filter = ("MPEG2",),
    ),
    StreamInfo(
        filename = "ger 384KBits.ac3",
        txt_filter = ("German",),
        parameter = ["-384", "-down6", "-quality=4"],
    ),
]



class Drive(object):
    def __init__(self, driveletter, cfg):
        self.letter = driveletter
        self.cfg = cfg

        self.vol_info = None
        self.lable = None

        self.stream_dir = os.path.join(driveletter, cfg["stream_dir"])

    def set_vol_info(self, vol_info):
        self.vol_info = vol_info
        self.lable = vol_info[0]

    def __str__(self):
        return "<Drive '%s'>" % self.letter
    def __repr__(self):
        return self.__str__()


class Files(list):
    def print_info(self):
        for file in self:
            print file.abs_path,
            size = file.stat.st_size/1024.0/1024.0/1024.0
            print "%.1f GB" % size
            print "output path....:", file.output_path
            print "log file path..:", file.log_file_path
            print










class VideoFile(object):
    def __init__(self, name, drive, abs_path, stat, cfg):
        self.name = name # Filename

        self.fn, self.ext = os.path.splitext(self.name)

        self.drive = drive # class "Drive"
        self.abs_path = abs_path # File path + filename
        self.stat = stat # os.stat
        
        self.cfg = cfg

        self.output_path = os.path.join(cfg["out_dir"], drive.lable)

        log_fn = "%s.log" % self.name.replace(".", "_")
        self.log_file_path = os.path.join(self.output_path, log_fn)

        self.streams = None # set in self.parse_streaminfo()

    def create_outdir(self):
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

    #-------------------------------------------------------------------------

    def open_log(self):
        """
        Open the log file
        """
        self.log_file = file(self.log_file_path, "a")
        self.log("Start logging")

    def log(self, txt):
        dt = datetime.datetime.now()
        timestamp = dt.strftime("%d.%m.%Y %H:%M:%S")
        self.log_file.write("%s %s\n" % (timestamp, txt))
        self.log_file.flush()

    def close_log(self):
        self.log_file.close()

    #-------------------------------------------------------------------------

    def get_command(self):
        cmds = [self.cfg["eac3to"], self.abs_path]
        for no, stream in self.streams:
            #~ print stream
            out_name = "%s_%s" % (self.fn, stream.filename)
            out_fn = os.path.join(self.output_path, out_name)
            cmds.append("%s: %s" % (no, out_fn))

            if stream.parameter:
                cmds += stream.parameter

        return " ".join(cmds)

    def parse_line(self, no, info):
        def in_list(txt, l):
            for item in l:
                if item in txt:
                    return True
            return False

        for stream_info in STREAMINFOS:
            if in_list(info, stream_info.txt_filter):
                self.streams.append([no, stream_info])
                return


    def parse_streaminfo(self, txt):
        self.streams = []
        lines = txt.splitlines()
        lines = lines[1:]
        for line in lines:
            #~ print ">", line
            no, info = line.split(":",1)
            no = int(no)
            info = info.strip()
            if info.startswith("Subtitle"):
                # Skip all subtitle streams
                continue

            self.parse_line(no, info)


    def get_stream_info(self):
        cmd = [self.cfg["eac3to"], self.abs_path]
        print "run '%s'..." % " ".join(cmd)
        process, output = subprocess2(cmd)
        return process, output

    #-------------------------------------------------------------------------

    def __str__(self):
        return "<File '%s'>" % self.abs_path
    def __repr__(self):
        return self.__str__()






def get_existing_drives(cfg):
    result = []
    for item in win32api.GetLogicalDriveStrings().split(chr(0)):
        if item:
            result.append(Drive(item, cfg))
    return result


def get_stream_dirs(drives):
    result = []
    for drive in drives:
        try:
            vol_info = win32api.GetVolumeInformation(drive.letter)
        except Exception, err:
            #~ print "Skip drive '%s': %s" % (drive.letter, err)
            continue

        if os.path.isdir(drive.stream_dir):
            drive.set_vol_info(vol_info)
            result.append(drive)

    return result




def get_stream_files(drives, skip_size):
    files = Files()
    for drive in drives:
        print drive,
        path = drive.stream_dir
        print path
        if not os.path.isdir(path):
            print "Error: Path '%s' doesn't exist -> skip." % path
            continue
        
        for fn in sorted(os.listdir(path)):
            abs_path = os.path.join(path, fn)
            stat = os.stat(abs_path)
            size = stat.st_size
            if size<cfg["skip_size"]:
                # Skip small files
                continue

            f = VideoFile(fn, drive, abs_path, stat, cfg)
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




def subprocess2(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        shell=True,
    )
    output = ""
    char_count = 0
    while True:
        char = process.stdout.read(1)
        if char=="":
            break

        if char in ("\r", "\x08"):
            continue
        
        if char == "\n":
            char_count = 0
        else:
            char_count += 1

        output += char
        sys.stdout.write(char)
        if char_count>79:
            sys.stdout.write("\n")
            char_count = 0            
        sys.stdout.flush()

    return process, output




if __name__ == "__main__":    
    cfg = VideoToolsConfig()
    cfg.debug()
    
    if DEBUG:
        print "DEBUG!!!"
        drive = Drive("d:", cfg)
        drive.stream_dir = r"d:\TEST\BDMV\STREAM"
        drive.set_vol_info(("TEST_LABLE",))
        drives = [drive,]
    else:
        # Scan all drive letters for stream dirs
        drives = get_existing_drives(cfg)
        drives = get_stream_dirs(drives)

    if not drives:
        print "No drives with stream files found -> abort, ok."
        sys.exit()

    files = get_stream_files(drives, cfg)
    files.print_info()
    
    if not files:
        print "No stream files found -> abort, ok."
        sys.exit()

    if not continue_loop():
        print "Abort, ok."
        sys.exit()

    for videofile in files:
        print videofile

        videofile.create_outdir()
        videofile.open_log()

        #~ file.parse_streaminfo(txt)
        process, output = videofile.get_stream_info()
        print "-"*80
        videofile.log("eac2to analyse output: %s" % output.lstrip("- "))
        videofile.parse_streaminfo(output)

        cmd = videofile.get_command()
        videofile.log("run: %s" % cmd)
        print cmd
        if DEBUG:
            print "DEBUG, skip real run..."
        else:
            process, output = subprocess2(cmd)
        videofile.log("eac2to output: %s" % output.lstrip("- "))

        videofile.close_log()
        
        break

    print " -- END -- "