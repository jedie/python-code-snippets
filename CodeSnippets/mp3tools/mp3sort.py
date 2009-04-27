#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    MP3 sort
    ~~~~~~~~
    Create a sorted directory structure of you MP3s via symbolic links.

    Structure of you MP3s:
        ... / BASE_DIR / artist-1 / ...
        ... / BASE_DIR / artist-2 / ...
        ... / BASE_DIR / artist-n / ...

    sorted dir looks like this:
        ... / SORT_DIR / TAG-1 / artist-1, artist-2, ... , artist-x
        ... / SORT_DIR / TAG-2 / artist-1, artist-2, ... , artist-x
        ... / SORT_DIR / TAG-x / artist-1, artist-2, ... , artist-x

    1. Reads alle direcotries from BASE_DIR
    2. Request the artist tag information from last.fm
    3. write toptags.xml into the artist dir (caching)
    4. create symbolic links from /BASE_DIR/artist/ to /SORT_DIR/tag/


    using
    ~~~~~
    You can edit the Config here in this file or create a small dispatcher file
    like this:
    ---------------------------------------------------------------------------
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    import sys
    sys.path.insert(0, "/path/to/MP3_sort/directory/")

    from MP3_sort import Config, check, auto_sort

    # Set the config
    Config.base_dir = "~/MP3s/"
    Config.sort_dir = "~/MP3s/sorted/"
    Config.use_tags = 2
    Config.debug = False

    check()
    auto_sort()

    raw_input("ENTER") # If you start it with the mouse ;)
    ---------------------------------------------------------------------------

    known bugs
    ~~~~~~~~~~
    There are problems with special characters in the arist name.

    TODO:
    ~~~~~
    Wenn ein Artist nicht gefunden werden kann, ist evtl. die Schreibweise
    nicht ganz korrekt. Helfen würde es, die Suche zu nutzten, z.B.:
        http://www.lastfm.de/music/?q=Coverdale+%26+Page

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007-2008 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__version__ = "SVN $Rev: $"

import os, subprocess, time, urllib, urllib2, re
from pprint import pprint


TAGS_XML = "toptags.xml"


class Config(object):
    """
    Contains the configurations.

    base_dir
        Directory witch contains the MP3 files. (The artist direcories)

    sort_dir
        Direcotry in witch the gerne-direcotries and the symlinks created.

    use_tags
        How many tags should be used? (Creates a symlinc for each tags)
    """
    base_dir = None
    sort_dir = None

    use_tags = 2
    
    # Delete MP3 file witch are too small (broken files) 
    mp3_del_min_size = 1000 #Bytes

    #__________________________________________________________________________
    # Variables how should not changed:

    # Tge tag Feed url from http://www.audioscrobbler.net/data/webservices/
    tag_url = "http://ws.audioscrobbler.com/1.0/artist/%s/toptags.xml"
    tag_re = re.compile(r"<name>(.*?)</name>")

    debug = False # Make more verbose output?


CFG = Config()


class Artist(object):
    """
    Holds information around a artist.
    """
    def __init__(self, cfg, artist):
        self.cfg = cfg
        self.name = artist

        self.path = os.path.join(self.cfg.base_dir, self.name)

    def get_quoted_name(self):
        """
        returns the url safe artist name
        """
        quoted_name = self.name.replace("_", " ")
        quoted_name = urllib.quote_plus(quoted_name)
        return quoted_name

    def get_feed_url(self):
        """
        returns the audioscrobbler feed url (Config.tag_url)
        """
        return self.cfg.tag_url % self.get_quoted_name()

    def get_feed_fs_path(self):
        """
        returns the toptags.xml cache filesystem path
        """
        return os.path.join(self.path, TAGS_XML)

    def cleanup(self):
        """
        Delete empty directories and delete all mp3 files witch are smaller than self.cfg.mp3_del_min_size
        """
        deleted_mp3s = 0
        deleted_dirs = 0
        
        empty_dirs = []
        for root, dirs, files in os.walk(self.path):
            if not dirs and files in ([], [TAGS_XML]):
                # empty directory or contains only the toptags xml file
                empty_dirs.append(root)
                continue
            
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext != ".mp3":
                    continue
                
                mp3path = os.path.join(root, filename)
                mp3size = os.path.getsize(mp3path)
                if mp3size<=self.cfg.mp3_del_min_size:
                    print ">>> File smaller than %sBytes:" % self.cfg.mp3_del_min_size
                    print "path:", root
                    print "file name:", filename
                    print "file size: %iBytes" % mp3size
                    print "delete mp3 file!"
                    os.remove(mp3path)
                    deleted_mp3s += 1
        
        empty_artist = False
        for path in empty_dirs:
            if TAGS_XML in os.listdir(path):
                print "delete toptags.xml file."
                os.remove(self.get_feed_fs_path())
                
            try:
                os.removedirs(path)
            except OSError, err:
                if self.cfg.debug:
                    print "debug: %s" % err
            else:
                if path == self.path:
                    print ">>> Empty artist directory removed:"
                    empty_artist = True
                else:
                    print ">>> empty directory removed:"
                print path
                deleted_dirs += 1
                
        
        return empty_artist, deleted_mp3s, deleted_dirs
                    
    def OLDcleanup(self):
        """ Delete empty directories. """
        dir_items = os.listdir(self.path)
                
        if TAGS_XML not in dir_items:
            has_toptags_file = False
        else:
            has_toptags_file = True
            index = dir_items.index(TAGS_XML)
            del(dir_items[index])
       
        if dir_items != []:
            # No empty artist dir -> do nothing
            return False
        
        # It's a empty artist dir -> delete it
        
        if has_toptags_file:
            # delete toptags.xml file
            os.remove(self.get_feed_fs_path())
            
        print "Info: Delete empty artist dir:", self.path
        os.rmdir(self.path)
        
        return True
            

    def __str__(self):
        return "<Artist '%s'>" % self.name


def check():
    """
    Some base checks before we start...
    """
    assert os.name == "posix", "only for linux!!!"
    assert CFG.base_dir != None, "Please set Config.base_dir!"
    assert CFG.sort_dir != None, "Please set Config.sort_dir!"

    assert CFG.use_tags >= 1

    CFG.base_dir = os.path.expanduser(CFG.base_dir)
    CFG.sort_dir = os.path.expanduser(CFG.sort_dir)

    assert os.path.isdir(CFG.base_dir), \
                            "CFG.base_dir path '%s' not exist!" % CFG.base_dir
    assert os.path.isdir(CFG.sort_dir), "Please create CFG.sort_dir path!"


def get_toptags_file(artist):
    """
    returns toptags.xml file content.

    Gets the toptags.xml file from audioscrobbler.com, stores it into the
    artist directory and use this file as a cache.
    """
    # Try to use toptags.xml from the filesystem
    feed_fs_path = artist.get_feed_fs_path()
    if CFG.debug:
        print "toptags.xml path:", feed_fs_path
    if os.path.isfile(feed_fs_path):
        if CFG.debug:
            print "toptags.xml found in filesystem"
        f = file(feed_fs_path, "r")
        content = f.read()
        f.close()
        if CFG.debug:
            print "Use toptags.xml from the filesystem"
        return content
    else:
        if CFG.debug:
            print "toptags.xml not found in filesystem."

    # get toptags.xml from audioscrobbler
    feed_url = artist.get_feed_url()
    if CFG.debug:
        print feed_url
    start_time = time.time()
    try:
        f = urllib2.urlopen(feed_url)
        #~ pprint(dict(f.info()))
        content = f.read()
        f.close()
    except urllib2.HTTPError, e:
        print "Error get toptags.xml from audioscrobbler:", e
        return None

    duration = time.time() - start_time
    print "Get toptags.xml from audioscrobbler in %.2fsec" % duration

    if CFG.debug:
        print "save toptags.xml in", feed_fs_path
    try:
        f = file(feed_fs_path, "w")
        f.write(content)
        f.close()
    except IOError, e:
        print "Error writing toptags.xml:", e

    return content



def get_tags(toptags_xml):
    """
    returns the first tag content (<name>XXX</name>).
    Use only the first x tags specified with CFG.use_tags.
    """
    tags = CFG.tag_re.findall(toptags_xml)
    if CFG.debug:
        print "all tags:", tags

    tags = tags[:CFG.use_tags]
    return tags


def link_artist(artist, tags):
    """
    Create the gerne sorted symlinks.

    -Create the gerne direcotry in CFG.sort_dir.
    -Create a symlincs from the source artist directory into the gerne dir
    """
    created_links = 0
    for tag in tags:
        print ">>> %s -" % tag,
        source_path = artist.path

        tag_dir = os.path.join(CFG.sort_dir, tag)
        if not os.path.isdir(tag_dir):
            if CFG.debug:
                print "makedirs: '%s'" % tag_dir
            os.makedirs(tag_dir)

        dst_dir = os.path.join(CFG.sort_dir, tag, artist.name)
        if CFG.debug:
            print source_path, dst_dir

        if os.path.isdir(dst_dir):
            print "symbolic link exist, skip."
            continue

        os.symlink(source_path, dst_dir)
        print "symbolic link created."
        created_links += 1
        
    return created_links



def auto_sort():
    """
    The main routine
    """
    count = 0
    created_links = 0
    deleted_mp3s = 0
    deleted_dirs = 0
    for artist in os.listdir(CFG.base_dir):
        artist = Artist(CFG, artist)
        if not os.path.isdir(artist.path):
            # not a directory (e.g. a file)
            if CFG.debug:
                print "skip '%s' (it's not a direcotry)" % artist.name
            continue

        count += 1
        print "_"*80
        print "%s - %s" % (count, artist.name)

        # Delete empty directories and small mp3 files
        empty_artist, mp3s, dirs = artist.cleanup()
        deleted_mp3s += mp3s
        deleted_dirs += dirs
        
        if empty_artist == True:
            # The artist dir was empty and has been deleted
            continue

        toptags_xml = get_toptags_file(artist)
        if not toptags_xml:
            print "no toptags_xml available."
            continue

        tags = get_tags(toptags_xml)
        if not tags:
            print "No tags found!!!"
            continue

        if CFG.debug:
            print "tags:", tags

        created_links += link_artist(artist, tags)
        
    print
    print
    
    print "Existing Artists:", count
    print "Deleted small mp3 files:", deleted_mp3s
    print "Deleted empty directories:", deleted_dirs
    print "new symbolic links:", created_links

if __name__ == "__main__":
    check()
    auto_sort()