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
import glob
import subprocess
import Tkinter as tk

from shared import config, tk_tools, tools

CHANNELS_BESWEET = ("FL", "C",  "FR", "SL", "SR", "LFE")
CHANNELS_AFTEN =   ("fl", "fc", "fr", "sl", "sr", "lfe")

CHANNEL_MAP_DIR = "audio_remix_maps"
OUT_NAME_ADDITION = "_AUDIO_REMIX"


def parse_channel_map(txt):
    """
    input: 
        fl  <- 2: SL - sox: vol 0.5
        fc  <- 1: FL
        fr  <- 2: SR - sox: vol 0.5
        sl  <- 2: SL 
        sr  <- 2: SR
        lfe <- 2: LFE
    returns:
    [('fl', 2, 'SL'), ('fc', 1, 'FL'), ('fr', 2, 'SR'), ('sl', 2, 'SL'), ('sr', 2, 'SR'), ('lfe', 2, 'LFE')]
    """
    channel_map = []
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("#") or line=="":
            continue

        destination, source = line.split("<-")
        destination = destination.strip()
        assert destination in CHANNELS_AFTEN, \
            "Error in channel map file in line: %r\nDestination channel %r not in %r!" % (
                line, destination, CHANNELS_AFTEN
        )
        source = source.strip()
        
        temp = source.split("sox:")
        source = temp[0].strip(" -")
        if len(temp)==2:
            sox_cmd = temp[1].strip()
        else:
            sox_cmd = None
        
        source_no, source_channel = source.split(":")
        source_no = int(source_no)
        assert source_no in (1,2), \
            "Error in channel map file in line: %r\nstream number %r is not 1 or 2!" % (line, source_no)
        source_channel = source_channel.strip()
        assert source_channel in CHANNELS_BESWEET, \
            "Error in channel map file in line: %r\nsource channel %r is not in %r!" % (
                line, source_channel, CHANNELS_BESWEET
        )
        
        channel_map.append((destination, source_no, source_channel, sox_cmd))
    return channel_map


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


def get_raw_channel_map(log, cfg, script_path):
    """
    Select channel map text file via Tk and return the file content.
    """
    pathname = os.path.join(script_path, CHANNEL_MAP_DIR, "*.txt")
    pathname = os.path.abspath(pathname)
    files = glob.glob(pathname)
    if not files:
        raise RuntimeError("No channel maps files found in: %s" % pathname)
    
    lb = tk_tools.TkListbox(
        title     = "Please select (%s)" % pathname,
        lable     = "Please select channel map",
        items     = files,
        selectmode=tk.SINGLE,
        #activated = (0,1,2), # Preselect front channels
    )
    filepath = lb.selection[0] # list of selected items.
    log("Use channel map file: %r" % filepath)
    
    f = file(filepath, "r")
    raw_channel_map = f.read()
    f.close()
    
    return raw_channel_map
    


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
       
    ext = os.path.splitext(stream_filename)[1]
    if ext == ".dts":
        eac3to_output = os.path.join(wave_temp_path, out_filename) + "_temp_640KBits.ac3"
        if os.path.isfile(eac3to_output):
            log("Skip creating AC3 file from DTS, because it exist: %s" % eac3to_output)
        else:
            log("create AC3 file from DTS with eac3to")
            cmd = [cfg["eac3to"], stream_filename, eac3to_output, "-640"]
            _run(log, cmd)
        stream_filename = eac3to_output
    
    outfile = os.path.join(wave_temp_path, out_filename) + "_"
    
    existing_files = glob.glob(outfile+"*.wav")
    if existing_files:
        log("Skip creating wave files, seems to be exist: %r" % existing_files)
        return

    cmd = [cfg["BeSweet"], '-core(', '-input', stream_filename, '-output', outfile, '-6ch', ')']
    _run(log, cmd)


def apply_sox(cfg, log, source_stream, source_out_filename, channel_map, name_prefix):
    """
    Apply sox filter, if needed.
    """
    for aften_parameter_code, stream_no, besweet_file_code, sox_cmd in channel_map:
        if not sox_cmd:
            continue    
        
        if stream_no == 1:
            filename = source_out_filename
        elif stream_no == 2:
            filename = second_out_filename
        else:
            raise RuntimeError("Wrong stream_no!")
        
        infile = filename + "_" + besweet_file_code + ".wav"
        outfile = filename + "_" + besweet_file_code + "_sox.wav"
        
        if os.path.isfile(outfile):
            log("Skip sox, output file exist: %s" % outfile)
            continue
               
        cmd = [cfg["sox"],     # sox.exe
            "--show-progress", # show progress, otherwise we see nothing ;) 
            "-V3",             # set verbosity
            infile, outfile    # in/out wave files
        ]
        
        sox_cmds = sox_cmd.split(" ") # FIXME: IMHO this doesn't work in any cases
        cmd += sox_cmds # add all sox effects, form audio remix map file
        
        _run(log, cmd)
    print


def remix_ac3(cfg, log, source_stream, second_stream, wave_temp_path, source_out_filename, second_out_filename, \
                                                                                    channel_map, name_prefix):
    """
    remix the mono wave files into a new AC3 file.
    """
    
    out_file = os.path.splitext(source_stream)[0] + OUT_NAME_ADDITION + ".ac3"
    log("Create %s" % out_file)
    
    cmd = [cfg["aften"]]
    
    for aften_parameter_code, stream_no, besweet_file_code, sox_cmd in channel_map:
        if stream_no == 1:
            filename = source_out_filename
        elif stream_no == 2:
            filename = second_out_filename
        else:
            raise RuntimeError("Wrong stream_no!")
            
        if sox_cmd:
            beseet_filename = filename + "_" + besweet_file_code + "_sox.wav"
        else:
            beseet_filename = filename + "_" + besweet_file_code + ".wav"
            
        log("use %r from %s" % (aften_parameter_code, beseet_filename))
        
        filepath = os.path.join(wave_temp_path, beseet_filename)

        cmd.append("-ch_%s" % aften_parameter_code)
        cmd.append(filepath)
    
    cmd.append(out_file)
    _run(log, cmd)



if __name__ == "__main__":
    cfg = config.VideoToolsConfig()
    cfg.debug()
    
    script_path = os.getcwd()
    print "Script path:", script_path
    
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
    
    # Get remix info
    raw_channel_map = get_raw_channel_map(log, cfg, script_path)
    channel_map = parse_channel_map(raw_channel_map)
    
    # Create out dir
    if not os.path.isdir(wave_temp_path):
        print "Create out path:", wave_temp_path
        os.makedirs(wave_temp_path)
    
    # Try to use NTFS compression (effective on WAV files ;)
    cmd=["compact", "/C", wave_temp_path]
    try:
        _run(log, cmd)
    except Exception, err:
        log("Error using NTFS compression: %s" % err)
    
    # source files -> WAV files
    BeSweetDemux(cfg, log, source_stream, wave_temp_path, source_out_filename)
    print
    BeSweetDemux(cfg, log, second_stream, wave_temp_path, second_out_filename)
    print
    
    # Apply sox filter, if needed
    os.chdir(wave_temp_path)
    apply_sox(cfg, log, source_stream, source_out_filename, channel_map, name_prefix)
    os.chdir(base_path)
       
    # Remix into final AC3 file
    remix_ac3(
        cfg, log,
        source_stream, second_stream,
        wave_temp_path, source_out_filename, second_out_filename,
        channel_map, name_prefix
    )
    print
    
    log.close()
    print " -- END -- "