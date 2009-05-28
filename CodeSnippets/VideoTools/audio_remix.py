# coding: utf-8

"""
    remix audio channels
    ~~~~~~~~~~~~~~~~~~~~
    
    e.g.:
        Use front left/center/right from source file.
        remix it with suround left/right + LFE from second file.
        
    Use BeSweet to create six wave files for every channel.
    If source stream is in DTS format -> use eac3to for convert it into a AC3 file, because
    BeSweet can' hanlde DTS format directly.
    Use Aften audio encoder for remix the channels into a new AC3 file.
"""
import os
import sys
import subprocess
import Tkinter as tk

from shared import config, tk_tools, tools

# IMPORTAND: The sort of all channel info must be the same!
CHANNEL_MAP = (
    "Front Left",    # 0
    "Front Center",  # 1
    "Front Right",   # 2
    "Surround Left", # 3
    "Surround Right",# 4
    "LFE",           # 5
)
CHANNELS_BESWEET = ("FL", "C",  "FR", "SL", "SR", "LFE")
CHANNELS_AFTEN =   ("fl", "fc", "fr", "sl", "sr", "lfe")

OUT_NAME_ADDITION = "_AUDIO_REMIX"


def get_same_prefix(items):
    prefix = ""
    for index, char in enumerate(items[0]):
        for item in items:
            if item[index] != char:
                return prefix
        prefix += char
    return prefix


def select_source_stream(file_path, files):
    lb = tk_tools.TkListbox(
        title     = "Please select (%s)" % file_path,
        lable     = "Please select **source** stream (e.g. for ceft,center,right-channels):",
        items     = files,
        selectmode=tk.SINGLE,
        #activated = (0,2), # Preselect "one" and "three"
    )
    source_stream = files.pop(lb.curselection[0]) # tuple containing index of selected items
    second_stream = files[0]
    return source_stream, second_stream


def select_source_channels(log, source_stream):
    streams = CHANNEL_MAP
    lb = tk_tools.TkListbox(
        title     = "Please select (%s)" % source_stream,
        lable     = "Please select channels witch would be used from the source stream file\n%s" % source_stream,
        items     = streams,
        selectmode=tk.SINGLE,
        activated = (0,1,2), # Preselect front channels
    )
    log("Selected channels: %r" % lb.selection) # list of selected items.
    return lb.curselection # tuple containing index of selected items


def _run(log, cmd):
    log("_"*79)
    log("run '%s'..." % " ".join(cmd))

    process = subprocess.Popen(cmd, shell=True)
    process.wait()

    print


def BeSweetDemux(cfg, log, stream_filename, wave_temp_path, out_filename):
    """
    demux audio streams into six mono wave files fir BeSweet.
    Use eac3to if source stream is DTS (convert it into AC3).
    """
    log("demux %r" % stream_filename)
    print
    
    if not os.path.isdir(wave_temp_path):
        print "Create out path:", wave_temp_path
        os.makedirs(wave_temp_path)
       
    ext = os.path.splitext(stream_filename)[1]
    if ext == ".dts":
        log("create AC3 file from DTS with eac3to")
        eac3to_output = os.path.join(wave_temp_path, out_filename) + "_temp_640KBits.ac3"
        cmd = [cfg["eac3to"], stream_filename, eac3to_output, "-640"]
        _run(log, cmd)
        stream_filename = eac3to_output
    
    outfile = os.path.join(wave_temp_path, out_filename) + "_"
    
    cmd = [cfg["BeSweet"], '-core(', '-input', stream_filename, '-output', outfile, '-6ch', ')']
    _run(log, cmd)


def remix(cfg, log, source_stream, second_stream, wave_temp_path, source_out_filename, second_out_filename, \
                                                                                source_channels_indexes, name_prefix):
    """
    remix the mono wave files into a new AC3 file.
    """
    out_file = os.path.splitext(source_stream)[0] + OUT_NAME_ADDITION + ".ac3"
    log("Create %s" % out_file)
    print
    
    cmd = [cfg["aften"]]
    
    for index, besweet_file_code in enumerate(CHANNELS_BESWEET):
        if index in source_channels_indexes:
            filename = source_out_filename
        else:
            filename = second_out_filename
            
        log("use %r from %r" % (besweet_file_code, filename))
        
        filepath = os.path.join(wave_temp_path, filename + "_" + besweet_file_code + ".wav")

        aften_parameter_code = CHANNELS_AFTEN[index]
        cmd.append("-ch_%s" % aften_parameter_code)
        cmd.append(filepath)
    
    cmd.append(out_file)
    _run(log, cmd)


if __name__ == "__main__":
    cfg = config.VideoToolsConfig()
    cfg.debug()
    
    assert len(sys.argv)==3, "DROP two audio files!"
    files = sys.argv[1:]
    print "arguments:"
    print files
    print
    
    dir1, filename1 = os.path.split(files[0])
    dir2, filename2 = os.path.split(files[1])
    assert dir1 == dir2, "The two audio files must be exist in the same directory!"
    
    base_path = dir1
    os.chdir(base_path)
    print "base path: %s" % base_path
    print
    
    name_prefix = get_same_prefix([filename1, filename2])
    prefix_cut_len = len(name_prefix) # for later use
    name_prefix = name_prefix.strip(" -_")
    wave_temp_path = name_prefix
    print "used name prefix: %r" % name_prefix
    print "used out path: %s" % wave_temp_path
    print
    
    source_stream, second_stream = select_source_stream(base_path, [filename1, filename2])
    
    log = tools.SimpleLog(os.path.splitext(source_stream)[0] + OUT_NAME_ADDITION + ".log")
    
    log("source stream: %s" % source_stream)
    log("second stream: %s" % second_stream)
    print
    
    
    
    source_out_filename = "source_" + source_stream[prefix_cut_len:]
    second_out_filename = "second_" + second_stream[prefix_cut_len:]
    log("used source out name: %s" % source_out_filename)
    log("used second out name: %s" % second_out_filename)
    print 

    source_channels_indexes = select_source_channels(log, source_stream)
    log("used channels from source stream: %s" % source_channels_indexes)
    print
    
    BeSweetDemux(cfg, log, source_stream, wave_temp_path, source_out_filename)
    BeSweetDemux(cfg, log, second_stream, wave_temp_path, second_out_filename)
    
    remix(
        cfg, log,
        source_stream, second_stream,
        wave_temp_path, source_out_filename, second_out_filename,
        source_channels_indexes, name_prefix
    )
    
    log.close()
    print " -- END -- "