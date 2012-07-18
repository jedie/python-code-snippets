# coding: utf-8

"""
    Extract all pictures from LibreOffice / OpenOffice files
    
    :copyleft: 2012 by Jens Diemer
    :license: GNU GPL v3 or above
"""

import os
import zipfile


def extract(path, exts, min_size):
    for filename in os.listdir(path):
        filename_prefix, ext = os.path.splitext(os.path.basename(filename))

        if ext not in exts:
            print "Skip file %s" % filename
            continue

        print "_"*79
        print " ***", filename

        abs_path = os.path.join(path, filename)
        with zipfile.ZipFile(abs_path, "r") as myzip:
            count = 0
            for item in myzip.namelist():
                if not item.startswith("Pictures/"):
                    continue

                info = myzip.getinfo(item)
                if info.file_size<min_size:
                    print "Skip file (too small): %s" % info.filename
                    continue

                count += 1

                out_ext = os.path.splitext(item)[1]

                out_name = "%s_%03d%s" % (filename_prefix, count, out_ext)
                out_filepath = os.path.join(path, out_name)

                print "%s -> %s" % (item, out_filepath),

                with myzip.open(item, "r") as zip_item:
                    with file(out_filepath, "wb") as out_file:
                        out_file.write(zip_item.read())

                print "OK"

        print "-"*79


if __name__=="__main__":
    extract(path=".", exts=[".ods", ".odt", ".odp"], min_size=8*1024)

