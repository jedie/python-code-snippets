#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Listet die neusten Verzeichnisse auf.

Dazu werden alle Verzeichnisse und Dateien abgesucht und deren
Änderungs-Datum festgehalten.

Das Ergebniss ist ein Dict bestehend aus:
    key....: neuste Änderungsdatum
    value..: vollständige Pfad
"""

import os, sys, stat, time, locale


class NewestFiles:
    def __init__(self, request, response):
        self.request    = request
        self.response   = response

        # Shorthands
        self.cfg        = self.request.cfg
        self.path       = self.request.path
        self.context    = self.request.context
        self.db         = self.request.db

        self.path.prepare_path("", u"browse")
        listPath = self.path.get_absolute_fs_path()

        self.dirCount = 0
        self.fileCount = 0
        self.totalSize = 0


        # Verz.baum einlesen
        start_time = time.time()
        newestDict = self.readdir(listPath)
        readTime = "%.2f" % (time.time() - start_time)

        # in jinja context einfügen
        self.request.context["newest_files"] = self.getContext(
            newestDict, count = 30
        )

        itemCount = locale.format("%i", (self.dirCount+self.fileCount), True)

        # In Log vermerken
        self.db.log(
            type="newest_files",
            item="(%s items, read in %sSec.)" % (
                itemCount, readTime
            )
        )

        self.request.context["stat"] = {
            "itemCount" : itemCount,
            "readTime"  : readTime,
            "dirCount"  : locale.format("%i", self.dirCount, True),
            "fileCount" : locale.format("%i", self.fileCount, True),
            "totalSize" : self.totalSize
        }

        # jinja Seite rendern
        self.request.render("NewestFiles_base")


    def filterFileNames(self, fileList, ext_whitelist):
        """
        Filtert aus der Datei-Liste die Dateien deren Endung in
        der ext_whitelist-Liste drin ist
        """
        result = []
        for fileName in fileList:
            try:
                ext = os.path.splitext(fileName)[1]
            except KeyError:
                continue

            if ext in ext_whitelist:
                result.append(fileName)
        return result

    def filesStat(self, absPath, fileList):
        """
        Liefert das Datum zurück, welches das neuste (max)
        aller Dateien ist
        """
        statList = []
        for fileName in fileList:
            absFilePath = os.path.join(absPath, fileName)
            fileStat = os.stat(absFilePath)
            statList.append(
                fileStat[stat.ST_MTIME]
            )
            self.fileCount += 1
            self.totalSize += fileStat[stat.ST_SIZE]
        return max(statList)


    def readdir(self, base_path):
        """
        Baut das newestDict auf.
        Das Dict besteht dabei aus:
            key....: neuste Änderungsdatum
            value..: vollständige Pfad
        """
        newestDict = {}

        ext_whitelist = self.cfg["ext_whitelist"]
        for dir,_,files in os.walk(base_path):
            files = self.filterFileNames(files, ext_whitelist)
            if not files:
                continue

            self.dirCount += 1
            dirStat = os.stat(dir)[stat.ST_MTIME]
            filesStat = self.filesStat(dir, files)

            maxStat = max(dirStat, filesStat)

            newestDict[maxStat] = dir

        return newestDict


    def getContext(self, newestDict, count = 20):
        timeList = newestDict.keys()
        timeList.sort(reverse=True)
        timeList = timeList[:count]

        fileList = []
        for key in timeList:
            path = newestDict[key]
            fileList.append({
                "mtime": time.strftime(
                    '%d.%m.%Y %H:%M', time.localtime(key)
                ),
                "path": self.path.relative_path(path),
                "url": self.path.url(path),
            })

        return fileList



#~ NewestFiles(base_path = u"M:\\_zum Brennen")
#~ NewestFiles(base_path = u"M:\\")

#~ NewestFiles(base_path = u"/daten/MP3z")

