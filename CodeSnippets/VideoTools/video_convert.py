#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
http://wiki.ubuntuusers.de/MEncoder
"""

import os, sys, time, subprocess
import stat


#~ SOURCE_EXT = (".avi",)
SOURCE_EXT = (".avi", ".mov", ".mp4")

#~ X264_PRESET = "ultrafast"
X264_PRESET = "slow"

FIFO_FILENAME = "stream.y4m"

#~ CONVERT_ONLY_ONE_FILE = True
CONVERT_ONLY_ONE_FILE = False

#~ SIMULATE_ONLY = True
SIMULATE_ONLY = False


def change_title(txt):
    sys.stdout.write("\x1b]2;%s\x07" % txt)


class VideoFile(object):
    def __init__(self, filename):
        self.filename = filename

        self.name, self.ext = os.path.splitext(filename)

        #~ print "_"*79
        #~ print filename
        file_stat = os.stat(filename)
        #~ print file_stat
        #~ file_time = file_stat[stat.ST_CTIME]
        file_time = min([file_stat[stat.ST_MTIME], file_stat[stat.ST_CTIME]])
        #~ print file_time
        t = time.localtime(file_time)
        #~ print t
        date_str = time.strftime("%Y-%m-%d", t)
        #~ print filename, date_str

        self.out_name = date_str + "_" + self.name + "_h264_mp3.mkv"

        self.video_temp_name = "temp_video_" + self.name + ".mkv"
        self.audio_temp_name = "temp_audio_" + self.name + ".mp3"

    def test(self):
        if self.ext.lower() not in SOURCE_EXT:
            return False

        if "xvid" in self.name.lower():
            print "Skip Xvid file '%s'" % filename
            return False

        if "x264" in self.name.lower():
            print "Skip x264 file '%s'" % filename
            return False

        if os.path.isfile(self.out_name):
            print "Skip existing file '%s'" % self.out_name
            return False

        return True


class VideoConverter(object):
    def __init__(self):
        files = self.read_current_dir()
        file_count = len(files)
        print "found %s files to convert." % file_count

        for no, file in enumerate(files):
            print "_"
            txt = " *** convert file %i/%i - %s ***" % (no, file_count, file.filename)
            change_title(txt)
            print txt

            #~ sys.exit()

            processes = []
            try:
                fifo_process = self.make_fifo()
                processes.append(fifo_process)
                if not SIMULATE_ONLY:
                    fifo_process.wait()

                mplayer_process = self.startup_mplayer(file)
                processes.append(mplayer_process)

                video_process = self.convert_video(file)
                processes.append(video_process)
                if not SIMULATE_ONLY:
                    video_process.wait()


                audio_process = self.convert_audio(file)
                processes.append(audio_process)
                if not SIMULATE_ONLY:
                    audio_process.wait()

                muxing_process = self.muxing(file)
                processes.append(muxing_process)
                if not SIMULATE_ONLY:
                    muxing_process.wait()
            except (Exception, KeyboardInterrupt), e:
                print
                print
                print "Abort: %s" % e
                print
                print "kill processes...",
                for process in processes:
                    try:
                        process.kill()
                    except Exception, err:
                        print "Error:", err
                    else:
                        print "OK"

                self.delete_files([
                    FIFO_FILENAME, file.out_name,
                    file.video_temp_name, file.audio_temp_name
                ])
                print "bye ;)"
                sys.exit(1)

            print "_"
            print "converting video %s done." % file.filename
            print
            print "remove temp files..."
            self.delete_files([
                FIFO_FILENAME,
                file.video_temp_name, file.audio_temp_name
            ])

            if CONVERT_ONLY_ONE_FILE:
                return

    def delete_files(self, files):
        for filename in files:
            if os.path.exists(filename):
                print
                print "Remove %r..." % filename,
                try:
                    os.remove(filename)
                except Exception, err:
                    print "Error:", err
                else:
                    print "OK"

    def read_current_dir(self):
        files = []
        for filename in sorted(os.listdir(".")):
            f = VideoFile(filename)
            if f.test() != True:
                continue

            files.append(f)

        return files

    def make_fifo(self):
        cmd = ["mkfifo", FIFO_FILENAME]
        print "_"
        print " ".join(cmd)
        if SIMULATE_ONLY:
            print "(simulate only!)"
            return
        process = subprocess.Popen(cmd)#, stdout=subprocess.PIPE)
        return process

    def startup_mplayer(self, file):
        cmd = [
            "nice",
            "mplayer",
            "-msglevel", "all=5",
            "-vo", "yuv4mpeg:file=%s" % FIFO_FILENAME,
            "-nosound",
            file.filename
        ]
        print "_"
        print " ".join(cmd)
        if SIMULATE_ONLY:
            print "(simulate only!)"
            return
        process = subprocess.Popen(cmd)#, stdout=subprocess.PIPE)
        return process

    def convert_audio(self, file):
        cmd = [
            "nice",
            "mencoder", file.filename,
            "-msglevel", "all=2",
            "-of", "rawaudio",
            "-oac", "mp3lame",
            "-lameopts", "aq=0:q=0:mode=1",
            "-ovc", "copy",
            "-o", file.audio_temp_name
        ]
        print "_"
        print " ".join(cmd)
        if SIMULATE_ONLY:
            print "(simulate only!)"
            return
        process = subprocess.Popen(cmd)#, stdout=subprocess.PIPE)
        return process

    def convert_video(self, file):
        cmd = [
            "nice",
            "x264",
            "--crf", "22",
            "--nr", "255",
            "--profile", "high",
            "--preset", X264_PRESET,
            "--tune", "film",
            "--verbose",
            "-o", file.video_temp_name,
            FIFO_FILENAME
        ]
        print "_"
        print " ".join(cmd)
        if SIMULATE_ONLY:
            print "(simulate only!)"
            return
        process = subprocess.Popen(cmd)#, stdout=subprocess.PIPE)
        return process

    def muxing(self, file):
        cmd = [
            "nice",
            "mkvmerge",
            "-o", file.out_name,
            file.video_temp_name, file.audio_temp_name
        ]
        print "_"
        print " ".join(cmd)
        if SIMULATE_ONLY:
            print "(simulate only!)"
            return
        process = subprocess.Popen(cmd)#, stdout=subprocess.PIPE)
        return process


v = VideoConverter()

#~ subprocess.Popen("export PS1='\[\e]0;my Window Title\a\]\u@\h:\w\$'", shell=True)
#~ os.environ["PS1"] = '\[\e]0;my Window Title\a\]\u@\h:\w\$'

'''

for filename in os.listdir("."):
    name, ext = os.path.splitext(filename)
    if ext.lower() not in (".avi", ".mov"):
        continue

    if "xvid" in name.lower():
        print "Skip Xvid file '%s'" % filename
        continue

    if "x264" in name.lower():
        print "Skip x264 file '%s'" % filename
        continue

    #~ if name.startswith("2008"):
        #~ continue

    print "_"*79
    print filename
    #~ print name, ext

    file_time = os.stat(filename)[ST_CTIME]
    #~ print file_time
    t = time.localtime(file_time)
    #~ print t
    date_str = time.strftime("%Y%m%d", t)
    #~ print date_str

#~ Die Parameter bewirken folgendes:
#~ *datei.wmv - Hier wird der Name der Quelldatei eingesetzt
#~ *-ovc steht für ,,Output Video" Codec. Deutet an, dass im folgenden der zu verwendende Videocodec angegeben wird
#~ *lavc steht für ,,libavcodec". Es soll ein Codec aus der Codecfamilie libavcodec verwendet werden
#~ *-lavopts deutet an, dass nun genauere Infos zu dem zu verwendenden Codec erfolgen
#~ *vcodec=mpeg4 - Als Videocodec wird ein DIVX-kompatibler mpeg4-Codec verwendet
#~ *vbitrate - Die Videobitrate soll 2000 betragen. Je höher die Bitrate, desto höher ist im Allgemeinen die Qualität
#~ *-oac steht für ,,Output Audio Codec". Deutet an, dass im folgenden der zu verwendende Audiocodec angegeben wird
#~ *mp3lame zeigt an, dass der Audiocodec lame zur MP3-Codierung verwendet werden soll
#~ *-lameopts deutet an, dass nun genauere Infos zu dem zu verwendenden Codec erfolgen
#~ *cbr bedeutet ,,Contanst Bitrate", also konstante Bitrate
#~ *br=128 legt fest, dass eine Bitrate von 128 kbit/s verwendet werden soll
#~ *-of heißt ,,Output Format" und legt das Containerformat der Zieldatei, also die Dateierweiterung fest
#~ *avi - Das zu verwendende Containerformat
#~ *-o steht für ,,Output" und zeigt an, dass nun der Name der Zieldatei folgt
#~ *out.avi ist der Name der Zieldatei inklusive der Dateierweiterung

    #--vbr-new -V 2 -b 32 -B 224 -q 0 -m j

    # xvid:
    out_name = "%s_%s_XviDMP3.avi" % (date_str, name)
    cmd = "nice mencoder %s -ovc lavc -lavcopts vcodec=xvid xvidencopts=fixed_quant=2 -oac mp3lame -lameopts vbr=3 -of avi -o %s" % (filename, out_name)

    # x264:
    # http://mewiki.project357.com/wiki/X264_Settings
    # http://www.mplayerhq.hu/DOCS/HTML/de/menc-feat-x264.html
    #~ out_name = "%s_%s_x264crf20_MP3.avi" % (date_str, name)
    # :preset=slower:profile=high:tune=film
    #~ cmd = "nice mencoder %s -ovc x264 -x264encopts crf=20:threads=auto -oac mp3lame -lameopts vbr=3 -of avi -o %s" % (filename, out_name)

"""
mkfifo stream.y4m

nice mplayer -vo yuv4mpeg:file=stream.y4m -nosound P1000164.MOV &

#~ nice x264 --crf 23 --nr 255 --profile main --preset slow --tune film --verbose -o P1000164_x264_video.mkv stream.y4m
nice x264 --crf 23 --nr 255 --profile baseline --preset faster --tune film --verbose -o P1000164_x264_video.mkv stream.y4m

rm stream.y4m

       #~ q=<0-9>
              #~ QualitÃ¤t (0 - hÃ¶chste, 9 - niedrigste) (nur bei VBR)

       #~ aq=<0-9>
              #~ QualitÃ¤t des Algorithmus (0 -  am  besten/langsamsten,  9  -  am  schlechtesten/
              #~ schnellsten)
       #~ mode=<0-3>
              #~ (Standard: automatisch)
                 #~ 0    Stereo
                 #~ 1    Joint-Stereo
                 #~ 2    Dual-Channel
                 #~ 3    Mono


nice mencoder P1000164.MOV -of rawaudio -oac mp3lame -lameopts aq=0:q=0:mode=1 -ovc copy -o P1000164.mp3

nice mkvmerge -o P1000164_x264.mkv P1000164_x264_video.mkv P1000164.mp3

rm P1000164.mp3
rm P1000164_x264_video.mkv
"""


    cmd = cmd.split(" ")

    print out_name

    if os.path.isfile(out_name):
        print "Skip existing file '%s'" % out_name
        continue

    print cmd
    print "-"*79
    print " ".join(cmd)
    print "-"*79
    try:
        process = subprocess.Popen(cmd)#, stdout=subprocess.PIPE)
        process.wait()
    except KeyboardInterrupt:
        print
        print
        print "Keyboard interrupt!"
        print "kill process...",
        try:
            process.kill()
        except Exception, err:
            print "Error:", err
        else:
            print "OK"

        print
        print "Remove %r" % out_name
        os.remove(out_name)
        sys.exit(1)
    #print process.stdout.read()
    print

'''