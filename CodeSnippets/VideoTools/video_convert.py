#!/usr/bin/env python
# coding: utf-8

"""
    video converter
    ~~~~~~~~~~~~~~~

    convert video files to h264 + MP3 in a .mkv container
    
    using:
        x264
        mencoder
        mplayer
        mkvmerge
        
    * works only under linux.
    * convert all files (with SOURCE_EXT extension) in the current directory
    * add date string to output filename

    :copyleft: 2011 by Jens Diemer
    :license: GNU GPL v3 or above
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


if __name__ == '__main__':
    v = VideoConverter()
