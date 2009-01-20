# -*- coding: utf-8 -*-

"""
demux selected streams from all m2ts files witch in a
movie playlist (\BDMV\mpls\*.mpls)

1. select movie playlist file
    (You will get a list of the biggest playlists)
2. select the streams
3. demux all streams from all m2ts files
    (You will get merged streams in separated video/audio files)
"""

import os
import sys
import re
from glob import glob

import Tkinter as tk

from shared.config import VideoToolsConfig
from shared import BD_objects, tk_tools, m2ts, eac3to, tools




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





def select_mpls(cfg, bluray):
    mpls = bluray.mpls.values()
    print mpls
    
    max_count = 15
    
    playlists = sorted(mpls, key=lambda x: x.size, reverse=True)[:max_count]

    lb = tk_tools.TkListbox(
        title     = "Please select",
        lable     = "Please select mpls file(s) witch should be converted:",
        items     = playlists,
        activated = (0,), # Preselect the first entry
    )
    print lb.curselection # tuple containing index of selected items
    return lb.selection # list of selected items.
    
    sys.exit()

#    return tk_tools.simple_select(
#        items, title="Select mpls files (the %s biggest)" % max_count,
#        text="Please select the mpls file witch will be converted:"
#    )

def select_streams(bluray, cfg, selected_mpls):
    stream_dict = selected_mpls.get_stream_dict()
    print stream_dict
    
    stream_numbers = m2ts.select_streams(stream_dict)
    print "Selected stream numbers:", stream_numbers
    
    new_stream_dict = {}
    for no in stream_numbers:
        new_stream_dict[no] = stream_dict[no]
    
    return new_stream_dict
    

def run_eac3to(cfg, out_dir, selected_mpls, stream_cmd):
    log_fn = "eac3to demux %s.log" % selected_mpls.filename
    log_abs_path = os.path.join(out_dir, log_fn)
    
    print "write into %r" % log_abs_path
    log = file(log_abs_path, "a")
    
    cmd = [cfg["eac3to"]]
    
    sourcefiles = []
    for m2ts_file in selected_mpls.m2ts_files:
        print m2ts_file
        sourcefiles.append(m2ts_file.abs_path)
    
    cmd.append("+".join(sourcefiles))
    
    cmd += stream_cmd
    
    log.write("run %r...\n" % cmd)
    print cmd
    
    process, output = tools.subprocess2(cmd)
    log.write("eac3to ready, outout:\n")
    log.write(output)
    log.close()
    
    


if __name__ == "__main__":
    cfg = VideoToolsConfig()
    cfg.debug()
    
    bluray = BD_objects.get_disc(cfg)
    
    print bluray.mpls
    print bluray.m2ts
    
    # Read all movie mpls files ...\BDMV\mpls\*.mpls
    # Attach all m2ts files to the mpls object and calc the total filesize
    bluray.read_mpls_files()
    
    selected_mpls = select_mpls(cfg, bluray)
    print "Selected mpls:", selected_mpls
    
    for playlist in selected_mpls:
    
        stream_dict = select_streams(bluray, cfg, playlist)
        print "selected streams: %r" % stream_dict
        
        stream_cmd = eac3to.build_stream_out(
            bluray.movie_name, bluray.out_dir, stream_dict
        )
        print "stream cmd: %r" % stream_cmd
        
        print "Create eac3to batch file."
        run_eac3to(cfg, bluray.out_dir, playlist, stream_cmd)
