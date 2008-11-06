# -*- coding: utf-8 -*-

"""
Only for changing the "out path" if a config file exist.
"""

from shared.config import VideoToolsConfig, DEFAULT_CONFIG

if __name__ == "__main__":
    cfg = VideoToolsConfig()
    cfg.debug()
    
    cfg["videofiletypes"] = DEFAULT_CONFIG["videofiletypes"]
    
    if cfg.out_dir_set == False:
        # No new config file created, and out dir requested in the past
        cfg.ask_out_dir()
        
    cfg.debug()