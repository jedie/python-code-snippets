#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, stat, time

#~ defaultencoding="latin-1"
#~ if sys.getdefaultencoding()!=defaultencoding:
    # Hack, damit defaultencoding auf UTF-8 gesetzt wird.
    #~ try:
        #~ reload(sys)
        #~ sys.setdefaultencoding(defaultencoding)
    #~ except:
        #~ pass


"""
Listet die neusten Verzeichnisse auf.

Dazu werden alle Verzeichnisse und Dateien abgesucht und deren
Änderungs-Datum festgehalten.

Das Ergebniss ist ein Dict bestehend aus:
    key....: neuste Änderungsdatum
    value..: vollständige Pfad
"""


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

        start_time = time.time()
        self.response.write("<p>read dir...")

        # Verz.baum einlesen
        newestDict = self.readdir(listPath)

        statTxt = "(%s items, readed in %.3fSec)" % (
            len(newestDict), (time.time() - start_time)
        )
        self.response.write("OK %s</p>" % statTxt)

        # In Log vermerken
        self.db.log(type="newest_files", item=statTxt)

        # in jinja context einfügen
        self.request.context["newest_files"] = self.getContext(
            newestDict, count = 30
        )

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
            statList.append(
                os.stat(absFilePath)[stat.ST_MTIME]
            )
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

