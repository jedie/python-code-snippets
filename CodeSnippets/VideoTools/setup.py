# -*- coding: utf-8 -*-

"""
Only for changing the "out path" if a config file exist.
"""

from shared.tk_tools import simple_input
from shared.config import VideoToolsConfig, DEFAULT_CONFIG

def set_size(cfg, key):
    txt = key.replace("_", " ")
    raw_skip_size = simple_input(      
        title="Setup m2ts file %s:" % txt,
        pre_lable="m2ts file %s:" % txt,
        init_value=cfg[key],
        post_lable="(in Bytes)",
    )
    cfg[key] = int(raw_skip_size)


if __name__ == "__main__":
    cfg = VideoToolsConfig()
    cfg.debug()
    
    cfg["videofiletypes"] = DEFAULT_CONFIG["videofiletypes"]
    
    if cfg.out_dir_set == False:
        # No new config file created, and out dir requested in the past
        cfg.ask_out_dir()
    
    set_size(cfg, "skip_size")
    set_size(cfg, "ignore_size")
        
    cfg.save_config()
    cfg.debug()