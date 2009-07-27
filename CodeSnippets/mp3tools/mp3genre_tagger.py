#!/usr/bin/env python
# coding: UTF-8

"""
    MP3 genre tagger
    ~~~~~~~~~~~~~~~~
    
    set the genre tag in MP3 files. Use last.fm data for it.
    
    Used http://eyed3.nicfit.net/
    
    Works only, if mp3s are organized in this order:
    
        /artist/album/tracks.mp3
    
    using
    ~~~~~
    You can edit the Config here in this file or create a small dispatcher file
    like this:
    ---------------------------------------------------------------------------
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    
    import os, sys
    
    #path = os.path.expanduser("~/path/to/mp3tools")
    #sys.path.insert(0, path)
    
    from mp3genre_tagger import CFG, check, setup_genre
    
    CFG.debug = False
    # CFG.debug = True
    CFG.base_dir = "~/path/to/mp3s/"
    check()
    setup_genre()
    
    raw_input("ENTER") # If you start it with the mouse ;)
    ---------------------------------------------------------------------------

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2009 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE.txt for more details.
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__version__ = "SVN $Rev: $"


import re
import os
import sys
import time
import urllib
import urllib2
import httplib

try:
    import eyeD3
except ImportError, err:
    print "Can't import eyeD3:" % err
    print
    print "Please install 'python-eyed3'"
    print "See also: http://eyed3.nicfit.net/"
    print
    sys.exit()


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
    api_key = "b25b959554ed76058ac220b7b2e0a026"

    # Delete MP3 file witch are too small (broken files) 
    mp3_del_min_size = 1000 #Bytes

    #__________________________________________________________________________
    # Variables how should not changed:

    # Track top tags
    # http://www.lastfm.de/api/show?service=289 
    track_toptags_url = (
        "http://ws.audioscrobbler.com/2.0/"
        "?method=track.gettoptags"
        "&artist=%(artist)s"
        "&track=%(track)s"
        "&api_key=%(api_key)s"
    )

    # Album info
    # http://www.lastfm.de/api/show?service=290
    album_info_url = (
        "http://ws.audioscrobbler.com/2.0/"
        "?method=album.getinfo"
        "&artist=%(artist)s"
        "&album=%(album)s"
        "&api_key=%(api_key)s"
    )

    # Artist top tags
    # http://www.lastfm.de/api/show?service=288
    artist_toptags_url = (
        "http://ws.audioscrobbler.com/2.0/"
        "?method=artist.gettoptags"
        "&artist=%(artist)s"
        "&api_key=%(api_key)s"
    )

    # Node: all tags would be automaticly lowercase!
    tag_rename = {
        "hip-hop": ("hip hop", "hiphop"),
    }

    clean_abum_re = re.compile(r"(\[\d{4}\] ).*?")
    clean_track_re = re.compile(r"^([\d\s\-]*).*?")

    toptags_area_re = re.compile(r"<toptags(.*?)</toptags>", re.DOTALL)
    tag_re = re.compile(r"<name>(.*?)</name>")

    skip_tags = ("albums i own",)

    debug = False # Make more verbose output?


    def get_artist_toptags_url(self, artist):
        return self.artist_toptags_url % {
            "api_key": self.api_key,
            "artist": urllib.quote_plus(artist),
        }

    def get_album_info_url(self, artist, album):
        return self.album_info_url % {
            "api_key": self.api_key,
            "artist": urllib.quote_plus(artist),
            "album": urllib.quote_plus(album),
        }

    def get_track_toptags_url(self, artist, album, track):
        return self.track_toptags_url % {
            "api_key": self.api_key,
            "artist": urllib.quote_plus(artist),
            "album": urllib.quote_plus(album),
            "track": urllib.quote_plus(track),
        }

CFG = Config()


def check():
    """
    Some base checks before we start...
    """
    assert os.name == "posix", "only for linux!!!"
    assert CFG.base_dir != None, "Please set Config.base_dir!"

    CFG.base_dir = os.path.expanduser(CFG.base_dir)

    assert os.path.isdir(CFG.base_dir), "CFG.base_dir path '%s' not exist!" % CFG.base_dir


class Lastfm(object):
    def __init__(self, cfg, cache_file, url, renew_cache):
        self.cfg = cfg
        self.cache_file = cache_file
        self.url = url
        self.renew_cache = renew_cache

    def get_toptags(self):
        raw_content = self.request()
        if raw_content == None:
            if self.cfg.debug:
                print "no content!"
            return []

        toptags_area = self.cfg.toptags_area_re.findall(raw_content)[0]
        if not toptags_area:
            if self.cfg.debug:
                print "no toptag area found!"
            return []

        raw_tags = self.cfg.tag_re.findall(toptags_area)

        tags = []
        for tag in raw_tags:
            tag = tag.lower()
            if tag not in tags:
                tags.append(tag)

        return tags

    def request(self):
        """ returns the raw content back from a lastfm request """
        if self.renew_cache == False and os.path.isfile(self.cache_file):
            if self.cfg.debug:
                print "Use existing cache file."
            f = file(self.cache_file, "r")
            content = f.read()
            f.close()
            return content

        if self.cfg.debug:
            print "request %r..." % self.url

        start_time = time.time()
        try:
            f = urllib2.urlopen(self.url)
            #~ pprint(dict(f.info()))
            content = f.read()
            f.close()
        except (urllib2.HTTPError, httplib.HTTPException), err:
            print self.url
            print "lastfm response error: %s" % err
            return None

        duration = time.time() - start_time
        print "lastfm response in %.2fsec, url: %s" % (duration, self.url)

        if self.cfg.debug:
            print "save cache file %r." % self.cache_file
        try:
            f = file(self.cache_file, "w")
            f.write(content)
            f.close()
        except IOError, err:
            print "Error writing cache file %r: %s" % (self.cache_file, err)

        return content


class ArtistAlbumTrackBase(object):
    def get_genre(self):
        if self.top_tags == None:
            self.set_top_tags()

        if self.top_tags:
            genre = self.top_tags[0]
            if self.cfg.debug:
                print "use genre %r from %s" % (genre, self)
            return genre

        # Use parent genre, if exist
        if self.parent:
            if self.cfg.debug:
                print "use genre from %r" % self.parent
            return self.parent.get_genre()

    def get_artist_clean_name(self):
        return self.artist.clean_name

    def set_top_tags(self):
        l = Lastfm(self.cfg, self.toptag_cache_path, self.toptags_url, self.renew_cache)
        self.top_tags = l.get_toptags()

        # remove artist name
        artist = self.get_artist_clean_name().lower()
        self.top_tags = [i for i in self.top_tags if i != artist]

        # remove skip tags
        self.top_tags = [i for i in self.top_tags if i not in self.cfg.skip_tags]

        if self.cfg.debug:
            print "set top tags:", self.top_tags




class Track(ArtistAlbumTrackBase):
    def __init__(self, cfg, artist, album, name, ext, path, renew_cache):
        self.cfg = cfg
        self.artist = artist
        self.album = album
        self.name = name
        self.ext = ext
        self.path = path
        self.renew_cache = renew_cache

        self.parent = self.album

        self.clean_name = self.cfg.clean_track_re.sub("", self.name)
        self.toptag_cache_path = os.path.join(self.album.path, "%s_toptags.xml" % self.name)

        self.toptags_url = self.cfg.get_track_toptags_url(
            self.artist.clean_name, self.album.clean_name, self.clean_name
        )

        self.top_tags = None # would be set in get_genre()
        self.tag = None # would be set in self.auto_set_tags()

    def auto_set_tags(self):
        """
        - create ID3tags if not exist
        - fill empty Artist, Album, Titel tags
        - set mp3 genre
        """
        self.tag = eyeD3.Tag()
        has_tags = self.tag.link(self.path)
        if has_tags == False: # no tag in this file, link returned False
            print "Track has no tags, create it: ", self
            self.tag.header.setVersion(eyeD3.ID3_V2_3)
            self.tag.setArtist(self.artist.clean_name)
            self.tag.setAlbum(self.album.clean_name)
            self.tag.setTitle(self.clean_name)
            self.set_mp3_genre()
            return

        # fill empty tag info's
        data = (
            ("getArtist", "setArtist", self.artist.clean_name),
            ("getAlbum", "setAlbum", self.album.clean_name),
            ("getTitle", "setTitle", self.clean_name),
        )
        for get_func, set_func, txt in data:
            mp3_tag = getattr(self.tag, get_func)()
            if mp3_tag == "":
                print "set %s to %s" % (set_func, txt)
                getattr(self.tag, set_func)(txt)
                self.tag.update()

        self.set_mp3_genre()


    def set_mp3_genre(self):
        self.genre = self.get_genre()
        if self.genre == None:
            print "No genre for track: %s" % self
            return

        try:
            tag_genre = self.tag.getGenre()
        except eyeD3.tag.GenreException, err:
            print "getGenre error:", err
            tag_genre = None

        if tag_genre and tag_genre.name.lower() == self.genre:
            if CFG.debug:
                print "No change needed."
            return

        g = eyeD3.Genre(id=None, name=self.genre)
        print "set genre: %15r for: %s" % (g.name, self.path)
        self.tag.setGenre(g)
        self.tag.update()

    def __str__(self):
        return "<Track %r from artist %r album %r path: %r>" % (
            self.name, self.artist.clean_name, self.album.name, self.path
        )
    __repr__ = __str__


class Album(ArtistAlbumTrackBase):
    def __init__(self, cfg, artist, name, path, renew_cache):
        self.cfg = cfg
        self.artist = artist
        self.name = name
        self.path = path
        self.renew_cache = renew_cache

        self.parent = self.artist

        self.clean_name = self.cfg.clean_abum_re.sub("", self.name)
        self.toptag_cache_path = os.path.join(self.path, "album_toptags.xml")

        self.top_tags = None # would be set in get_genre()
        self.toptags_url = self.cfg.get_album_info_url(self.artist.clean_name, self.clean_name)

    def tracks(self, renew_cache=False):
        for filename in os.listdir(self.path):
            path = os.path.join(self.path, filename)
            if not os.path.isfile(path):
                continue

            name, ext = os.path.splitext(filename)
            if ext.lower() != ".mp3":
                continue

            track = Track(self.cfg, self.artist, self, name, ext, path, renew_cache)
            yield track

    def __str__(self):
        return "<Album %r from artist %r path: %r>" % (self.name, self.artist.clean_name, self.path)
    __repr__ = __str__


class Artist(ArtistAlbumTrackBase):
    """
    Holds information around a artist.
    """
    def __init__(self, cfg, artist, path, renew_cache=False):
        self.cfg = cfg
        self.name = artist
        self.path = path
        self.renew_cache = renew_cache

        self.parent = None

        self.clean_name = self.name.replace("_", " ")

        self.toptag_cache_path = os.path.join(self.path, "artist_toptags.xml")

        self.top_tags = None # would be set in get_genre()
        self.toptags_url = self.cfg.get_artist_toptags_url(self.name)

    def get_artist_clean_name(self):
        return self.clean_name

    def albums(self, renew_cache=False):
        for dir in os.listdir(self.path):
            path = os.path.join(self.path, dir)
            if os.path.isdir(path):
                album = Album(self.cfg, self, dir, path, renew_cache)
                yield album

    def __str__(self):
        return "<Artist %r %r>" % (self.name, self.path)
    __repr__ = __str__




def setup_genre():
    for artist_dir in os.listdir(CFG.base_dir):
        artist_path = os.path.join(CFG.base_dir, artist_dir)
        if not os.path.isdir(artist_path):
            continue

        artist = Artist(CFG, artist_dir, artist_path, renew_cache=False)
        if CFG.debug:
            print "_" * 79
            print artist

        for album in artist.albums():
            if CFG.debug:
                print "-" * 79
                print album

            for track in album.tracks(renew_cache=False):
                if CFG.debug:
                    print " -" * 39
                    print track.path

                track.auto_set_tags()

        if CFG.debug:
            print


if __name__ == "__main__":
#    CFG.debug = False
    CFG.debug = True
    CFG.base_dir = "~/test/"
    check()
    setup_genre()
