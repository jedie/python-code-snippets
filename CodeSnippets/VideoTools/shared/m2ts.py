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

def parse_m2ts_streaminfo(txt, debug=False):
    """ convert eac3to output into stream_dict for **m2ts file** """
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

def parse_mpls_streaminfo(txt, debug=False):
    """ convert eac3to output into stream_dict for **mpls file** """
    stream_dict = {}
    lines = txt.splitlines()
    no = 0
    for line in lines:
        if debug:
            print ">", line
        line = line.strip()
        if not line.startswith("-"):
            continue
        
        no += 1       
        stream_dict[no] = line.strip("- ")
        
    return stream_dict


def get_stream_info(cfg, source_cmd, cache_filepath):
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
        cmd = [cfg["eac3to"], source_cmd]
        print "run '%s'..." % " ".join(cmd)
        process, output = tools.subprocess2(cmd)
        
        f = file(cache_filepath, "w")
        f.write(output)
        f.close()
    
    if source_cmd.endswith(".mpls"):
        return parse_mpls_streaminfo(output)
    elif source_cmd.endswith(".m2ts"):
        return parse_m2ts_streaminfo(output)
    else:
        raise
