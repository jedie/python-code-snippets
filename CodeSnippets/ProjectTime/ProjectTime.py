#!/usr/bin/python
# -*- coding: ISO-8859-1

"""
Ermittelt anhand der timestamp von Verz. und Dateien die Arbeitszeit
an einem Projekt.

http://www.jensdiemer.de

license = GNU General Public License v2 or above
  en -> http://www.opensource.org/licenses/gpl-license.php
  de -> http://jensdiemer.de/Programmieren/GPL-License
"""

__version__ = "v0.1"
__history__ = """
v0.1
    - erste Version
"""

import os, datetime, math

weekDaysMap = {
    "Mon": "MO",
    "Tue": "DI",
    "Wed": "MI",
    "Thu": "DO",
    "Fri": "FR",
    "Sat": "SA",
    "Sun": "SO"
}

class TimeStore(dict):
    def add(self, time, filePath):
        if not self.has_key(time):
            self[time] = []
        self[time].append(filePath)



class Chronologer:
    def __init__(self,
        projectPath,            # Pfad in dem die Projectdateinen liegen
        hourlyRate,             # Stundenlohn
        maxTimeDiff = 60*60,    # max Zeit, die ein Arbeitsblock trennt
        minBlockTime = 30*60,   # kleinste Zeiteinheit, für einen Block
        # Erster und letzter Tag, andere Zeiten werden ignoriert
        projectStart = datetime.datetime(year = 1977, month = 1, day = 1),
        projectEnd = datetime.datetime(year = 2200, month = 12, day = 31)
            ):

        self.projectPath    = projectPath
        self.maxTimeDiff    = maxTimeDiff
        self.minBlockTime   = minBlockTime
        self.hourlyRate     = hourlyRate
        self.projectStart   = projectStart
        self.projectEnd     = projectEnd

        self.statistics = {}
        self.dayData = {}
        self.timeStore = TimeStore()

        print "read dir...",
        count = self.readDir(self.projectPath)
        print "OK (%s items)" % count

        print "calc blocks...",
        timeBlocks = self.makeBlocks()
        print "OK"

        print "analyseBlocks...",
        self.analyseBlocks(timeBlocks)
        print "OK"

    def readDir(self, path):
        """ Einlesen der Verzeichnis Informationen """
        count = 0
        if not os.path.isdir(path):
            raise SystemError("Path '%s' not found!" % path)

        for root, dirs, files in os.walk(path):
            for dir in dirs:
                count += 1
                self.statFile(os.path.join(root, dir))
            for fileName in files:
                count += 1
                self.statFile(os.path.join(root, fileName))
        return count

    def statFile(self, path):
        """ Zeiten für Verz.Eintrag festhalten """
        pathStat = os.stat(path)
        creationTime        = pathStat.st_ctime
        lastAccess          = pathStat.st_atime
        lastModification    = pathStat.st_mtime

        self.timeStore.add(creationTime, path)
        self.timeStore.add(lastAccess, path)
        self.timeStore.add(lastModification, path)

    def makeBlocks(self):
        """ Zusammenhängende Arbeitszeiten ermitteln """
        timeList = self.timeStore.keys()
        timeList.sort()

        # Ende-Datum soll inkl. des angegebenen Tags sein
        projectEnd = self.projectEnd + datetime.timedelta(days=1)

        timeBlocks = []
        lastTime = 0
        for t in timeList:
            d = datetime.datetime.fromtimestamp(t)
            if d<self.projectStart: continue
            if d>projectEnd: continue

            if (t-lastTime)>self.maxTimeDiff:
                # Ein neuer Block, weil die Differenz zu groß ist
                timeBlocks.append([])

            timeBlocks[-1].append(t)
            lastTime = t

        return timeBlocks

    def blockTime(self, block):
        """ Liefert die Zeit eines Blocks zurück """
        if len(block) == 1:
            return self.minBlockTime

        workTime = block[-1] - block[0]
        if workTime<self.minBlockTime:
            return self.minBlockTime

        return workTime

    def analyseBlocks(self, timeBlocks):
        """
        Ermittelt gesammt Arbeitszeit und kalkuliert die Zeit für
        jeden Arbeits-Block
        """
        self.statistics["totalTime"] = 0
        days = {}
        for block in timeBlocks:
            blockTime = self.blockTime(block)
            self.statistics["totalTime"] += blockTime

            d = datetime.datetime.fromtimestamp(block[0])
            key = d.strftime("%y%m%d")

            if self.dayData.has_key(key):
                self.dayData[key]["blockTime"] += blockTime
                self.dayData[key]["block"].append(block)
            else:
                self.dayData[key] = {
                    "dayName"   : weekDaysMap[d.strftime("%a")],
                    "week"      : d.strftime("%W"),
                    "dateStr"   : d.strftime("%d.%m.%Y"),
                    "blockTime" : blockTime,
                    "block"     : [block],
                }

    def displayBlock(self, dayBlock, verbose):
        """
        Anzeige eines zusammenhängenden Blockes
        """
        for coherentBlocks in dayBlock:
            dirInfo = {}
            for timestamp in coherentBlocks:
                fileList = self.timeStore[timestamp]
                for path in fileList:
                    dir, file = os.path.split(path)

                if not dirInfo.has_key(dir):
                    dirInfo[dir] = []

                dirInfo[dir].append(file)

            dirs = dirInfo.keys()
            dirs.sort()
            for dirName in dirs:
                shortDirName = ".%s" % dirName[len(self.projectPath):]

                if verbose == 1:
                    print "\t%3s files in %s" % (
                        len(dirInfo[dirName]), shortDirName
                    )
                else:
                    print "\t%s" % shortDirName
                    for fileName in dirInfo[dirName]:
                        print "\t\t%s" % fileName
        print

    def displayResults(self, verbose=0):
        """
        Anzeigen der Ergebnisse
        verbose = 0 -> normale Ansicht, nur Tag und Std.-Anzahl
        verbode = 1 -> Anzahl der geänderten Dateien
        verbode = 2 -> Auflistung der geänderten Dateien
        """
        totalTime = self.statistics["totalTime"]
        print
        print ">display Results"
        print
        print "totalTime: %sSec -> %.2fStd -> %.2f 8-Std-Tage" % (
            totalTime, totalTime/60.0/60.0,
            totalTime/60.0/60.0/8.0
        )
        keys = self.dayData.keys()
        keys.sort()

        print "-"*40

        lastWeek = 0
        totalStd = 0
        for i, key in enumerate(keys):
            dayName     = self.dayData[key]["dayName"]
            week        = self.dayData[key]["week"]
            dateStr     = self.dayData[key]["dateStr"]
            blockTime   = self.dayData[key]["blockTime"]
            block       = self.dayData[key]["block"]

            if week>lastWeek: # Leerzeile zwischen den Wochen
                print
                print "Woche: %s" % week
            lastWeek = week

            blockTime = int(math.ceil(blockTime/60.0/60.0)) # Aufrunden
            print "%4s - %s, %s:%3i Std ->%4s€" % (
                i+1, dayName, dateStr, blockTime, blockTime*self.hourlyRate
            )
            totalStd += blockTime
            if verbose:
                self.displayBlock(block, verbose)

        print "_"*40
        totalCosts = totalStd * self.hourlyRate
        print " %s Std * %s€ = %s€" % (totalStd, self.hourlyRate, totalCosts)

    def displayPushedResults(self, exchangeRatio,
        displayMoneyOnly=False, maxDayTime=14):
        """
        Rechnet die Anzahl der Stunden pro Tag so um, das unterm Strich
        ungefähr der gleiche Betrag, trotz eines anderen Stundenlohns
        herrauskommt.
        maxDayTime - Max. Arbeitszeit pro Tag, überzählige Stunden werden auf
            den nächten Tag "verschoben"
        """
        print
        print "-"*40
        print ">PushedResults (exchangeRatio: %s, maxDayTime: %s)" % (
            exchangeRatio, maxDayTime
        )

        keys = self.dayData.keys()
        keys.sort()

        lastWeek = 0
        totalStd = 0
        overhang = 0
        for i, key in enumerate(keys):
            dayName     = self.dayData[key]["dayName"]
            week        = self.dayData[key]["week"]
            dateStr     = self.dayData[key]["dateStr"]
            blockTime   = self.dayData[key]["blockTime"]
            block       = self.dayData[key]["block"]

            if week>lastWeek: # Leerzeile zwischen den Wochen
                print
                print "Woche: %s" % week
                lastWeek = week

            blockTime = blockTime * self.hourlyRate / exchangeRatio
            pushedTime = int(math.ceil(blockTime/60.0/60.0))

            # Tägliche Abeitszeit begrenzen
            pushedTime += overhang
            if pushedTime>maxDayTime:
                overhang = pushedTime-maxDayTime
                pushedTime = maxDayTime
            else:
                overhang = 0

            if displayMoneyOnly:
                print "%3s - %s, %s:%4i€" % (i+1, dayName, dateStr, pushedTime*exchangeRatio)
            else:
                print "%3s - %s, %s:%3i Std" % (i+1, dayName, dateStr, pushedTime)
            totalStd += pushedTime

        if overhang>0:
            print "-> rest overhang: %sStd !!!" % overhang

        print "_"*40
        totalCosts = totalStd * exchangeRatio
        if displayMoneyOnly:
            print "%5s€" % totalCosts
        else:
            print " %s Std * %s€ = %s€" % (totalStd, exchangeRatio, totalCosts)


if __name__ == "__main__":
    #~ c = Chronologer(
        #~ projectPath     = r".",
        #~ hourlyRate      = 80,
    #~ ).displayResults()

    c = Chronologer(
        projectPath     = r".",
        hourlyRate      = 80,
        maxTimeDiff     = 60 * 60,
        minBlockTime    = 55 * 60,
        projectStart    = datetime.datetime(year = 2005, month = 3, day = 1),
        projectEnd      = datetime.datetime(year = 2007, month = 3, day = 31),
    )

    print "\n"*3, "="*79
    print "(verbose: 0)"
    c.displayResults()

    print "\n"*3, "="*79
    print "(verbose: 1)"
    c.displayResults(verbose=1)

    print "\n"*3, "="*79
    print "(verbose: 2)"
    c.displayResults(verbose=2)

    print "\n"*3, "="*79

    # Umrechnung auf anderen Stundenlohn
    c.displayPushedResults(exchangeRatio=35)
    print "\n"*3, "="*79
    c.displayPushedResults(exchangeRatio=30)
    print "\n"*3, "="*79
    c.displayPushedResults(exchangeRatio=35, displayMoneyOnly=True)





