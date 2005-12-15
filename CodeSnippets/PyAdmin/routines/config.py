#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-


import sys, os, ConfigParser


config_file = "PyAdmin.conf"

class Parser:
    def __init__( self ):
        self.current_section = ""
        if not os.path.isfile( config_file ):
            self.error( "file not found!" )

        self.cfg = ConfigParser.RawConfigParser()
        self.cfg.read( config_file )

    def set_section( self, section ):
        self.current_section = section

    def get( self, option, item_type = "str" ):
        self.check( option )
        if item_type == "str":
            return self.cfg.get( self.current_section, option )
        elif item_type == "int":
            return self.cfg.getint( self.current_section, option )
        elif item_type == "boolean":
            return self.cfg.getboolean( self.current_section, option )
        elif item_type == "list":
            value = self.cfg.get( self.current_section, option )
            value_list = value.split(",")
            return [i.strip() for i in value_list]
        self.error( "item_type '%s' unknown" % item_type )

    def check( self, option ):
        if not self.cfg.has_section( self.current_section ):
            self.error( "section '[%s]' not found!" % self.current_section )
        if not self.cfg.has_option( self.current_section, option ):
            self.error( "in section '[%s]' option '%s' not found!" %
                (self.current_section, option) )

    def error( self, txt ):
        import cgitb ; cgitb.enable()
        raise ValueError, "error in Config File '%s': %s" % (config_file, txt)
        sys.exit()

