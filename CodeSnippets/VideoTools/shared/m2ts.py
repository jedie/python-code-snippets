# -*- coding: utf-8 -*-

import os

import tools
import tk_tools



def select_streams(stream_dict):
    """
    select witch streams should be convert.
    """
    print "*"*79
    items = []
    for key, txt in stream_dict.iteritems():
        stream_txt = "%i: %s" % (key, txt)
        items.append(stream_txt)
   
    selection = tk_tools.TkListbox(
        title     = "Please select",
        lable     = "Please select streams:",
        items     = items,
        activated = [0,1], # Preselect chapters and first video track
    ).selection
    print selection
    
    result = []
    for txt in selection:
        no = int(txt.split(":", 1)[0])
        result.append(no)
    
    return result


def parse_streaminfo(txt, debug=False):
    stream_dict = {}
    lines = txt.splitlines()
    lines = lines[1:]
    for line in lines:
        if debug:
            print ">", line
        no, info = line.split(":",1)
        
        try:
            no = int(no)
        except ValueError:
            continue
        
        info = info.strip()
        
        stream_dict[no] = info
        
    return stream_dict
 

def get_stream_info(cfg, m2ts_path, cache_filepath):
    """
    Run eac3to and cache the output data.
    """
    if os.path.isfile(cache_filepath):
        print "Use existing eac3to output from cache file '%s'..." % (
            cache_filepath
        )
        f = file(cache_filepath, "r")
        output = f.read()
        f.close()
    else:
        # run eac3to and save the output data into txt_path
        cmd = [cfg["eac3to"], m2ts_path]
        print "run '%s'..." % " ".join(cmd)
        process, output = tools.subprocess2(cmd)
        
        f = file(cache_filepath, "w")
        f.write(output)
        f.close()
    
    return parse_streaminfo(output)
