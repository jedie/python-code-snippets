# -*- coding: utf-8 -*-

import os

import tools


STREAMINFOS = [
    {
        "txt_filter": ("Chapters",),
        "ext": ".txt",
    },
    {
        "txt_filter": ("h264", "VC-1", "MPEG2",),
        "ext": ".mkv",
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
        "txt_filter": ("TrueHD/AC3", "AC3"),
        "ext": ".ac3",
    },
    {
        "txt_filter": ("Subtitle",),
        "ext": ".sup",
    },
]

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



def build_stream_out(out_name, out_path, stream_dict):
    """
    >>> d = {1: 'h264/AVC, 1080p24 /1.001 (16:9)', \
    13: 'Subtitle (PGS), Danish', \
    22: 'Subtitle (PGS), English'}
    >>> build_stream_out("movie1", "/out/", d)
    ... ['1:', '/out/movie1 - 1 - h264 AVC, 1080p24 1.001 16 9.mkv', '13:',\
 '/out/movie1 - 13 - Subtitle PGS , Danish.sup',\
 '22:', '/out/movie1 - 22 - Subtitle PGS , English.sup']
    """
    cmd = []
    for no, txt in stream_dict.iteritems():
        cmd.append("%i:" % no)
        
        filename = "%s - %i - %s%s" % (
            out_name,
            no,
            tools.make_slug(txt),
            get_file_ext(txt),
        )
        out_filepath = os.path.join(out_path, filename)
        
        cmd.append(out_filepath)
    return cmd
    
    
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
                tools.make_slug(stream_txt),
                file_ext,
            )
            out_filepath = os.path.join(self["out_path"], filename)
            
            cmd.append("%i:" % id)
            cmd.append(out_filepath)
                    
    return cmd



if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    print "DocTest end."