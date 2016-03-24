#!/usr/bin/python3
# coding: ISO-8859-15


"""
    Ermittelt anhand der timestamp von Verz. und Dateien die Arbeitszeit
    an einem Projekt.

    http://www.jensdiemer.de

    license = GNU General Public License v3 or above
      en -> http://www.opensource.org/licenses/gpl-license.php
      de -> http://jensdiemer.de/Programmieren/GPL-License
"""

__version__ = "v0.1"
__history__ = """
v0.1
    - erste Version
"""

import os, datetime, time, math

weekDaysMap = {
    "Mon": "MO",
    "Tue": "DI",
    "Wed": "MI",
    "Thu": "DO",
    "Fri": "FR",
    "Sat": "SA",
    "Sun": "SO"
}

day_additionals = {
    "SA":1.5,
    "SO":1.5,
}

time_additionals = {
    "18-6h": (datetime.time(18), datetime.time(6), 1.5)
}

class TimeStore(dict):
    def add(self, time, filePath):
        if time not in self:
            self[time] = []
        self[time].append(filePath)



class Chronologer:
    def __init__(self,
        projectPath, # Pfad in dem die Projectdateinen liegen
        hourlyRate, # Stundenlohn
        maxTimeDiff=60 * 60, # max Zeit, die ein Arbeitsblock trennt
        minBlockTime=30 * 60, # kleinste Zeiteinheit, für einen Block
        # Erster und letzter Tag, andere Zeiten werden ignoriert
        projectStart=datetime.datetime(year=1977, month=1, day=1),
        projectEnd=datetime.datetime(year=2200, month=12, day=31),
        exclude_dirs=None,
        day_additionals=day_additionals,
        time_additionals=time_additionals,
        debug=False,
        only_mtime=False,
            ):

        self.projectPath = projectPath
        self.maxTimeDiff = maxTimeDiff
        self.minBlockTime = minBlockTime
        self.hourlyRate = hourlyRate
        self.projectStart = projectStart
        self.projectEnd = projectEnd
        self.exclude_dirs = exclude_dirs or []
        self.day_additionals = day_additionals
        self.time_additionals = time_additionals
        self.debug = debug
        self.only_mtime = only_mtime

        self.total_costs = None
        self.statistics = {}
        self.dayData = {}
        self.timeStore = TimeStore()

        print("read %r..." % self.projectPath)
        count = self.readDir(self.projectPath)
        print("OK (%s items)" % count)

        print("calc blocks...", end="")
        timeBlocks = self.makeBlocks()
        print("OK")

        print("analyseBlocks...", end="")
        self.analyseBlocks(timeBlocks)
        print("OK")

    def readDir(self, path):
        """ Einlesen der Verzeichnis Informationen """

        def exclude_dir(dir):
            dir = "\\%s\\" % dir.strip("\\")
            for exclude_dir in self.exclude_dirs:
                exclude_dir = "\\%s\\" % exclude_dir.strip("\\")

                #~ print(dir, exclude_dir
                #~ if dir.startswith(exclude_dir):
                if exclude_dir in dir:
                    return True
            return False

        next_update = time.time() + 1

        count = 0
        if not os.path.isdir(path):
            raise SystemError("Path '%s' not found!" % path)

        for root, dirs, files in os.walk(path):
            if exclude_dir(root):
                if self.debug:
                    print("Skip dir %r..." % root)
                continue
            for dir in dirs:
                count += 1
                self.statFile(os.path.join(root, dir))
            for fileName in files:
                count += 1
                self.statFile(os.path.join(root, fileName))

            if time.time()>next_update:
                print("%i dir items readed..." % count)
                next_update = time.time() + 1

        return count

    def statFile(self, path):
        """ Zeiten für Verz.Eintrag festhalten """
        try:
            pathStat = os.stat(path)
        except Exception as err:
            print("Error getting stat for %r: %s" % (path, err))
            return
        creationTime = pathStat.st_ctime
        lastAccess = pathStat.st_atime
        lastModification = pathStat.st_mtime

        if self.debug:
            print("File %r:" % path)
            print("creation time...: %r" % datetime.datetime.fromtimestamp(creationTime))
            print("last access time: %r" % datetime.datetime.fromtimestamp(lastAccess))
            print("last modify time: %r" % datetime.datetime.fromtimestamp(lastModification))

        if not self.only_mtime:
            self.timeStore.add(creationTime, path)
            self.timeStore.add(lastAccess, path)
        self.timeStore.add(lastModification, path)

    def makeBlocks(self):
        """ Zusammenhängende Arbeitszeiten ermitteln """
        timeList = list(self.timeStore.keys())
        timeList.sort()

        # Ende-Datum soll inkl. des angegebenen Tags sein
        projectEnd = self.projectEnd + datetime.timedelta(days=1)

        timeBlocks = []
        lastTime = 0
        for t in timeList:
            d = datetime.datetime.fromtimestamp(t)
            if d < self.projectStart: continue
            if d > projectEnd: continue

            if (t - lastTime) > self.maxTimeDiff:
                # Ein neuer Block, weil die Differenz zu groï¿œ ist
                timeBlocks.append([])

            timeBlocks[-1].append(t)
            lastTime = t

        return timeBlocks

    def blockTime(self, block):
        """ Liefert die Zeit eines Blocks zurück """
        if len(block) == 1:
            return self.minBlockTime

        workTime = block[-1] - block[0]
        if workTime < self.minBlockTime:
            return self.minBlockTime

        return workTime

    def analyseBlocks(self, timeBlocks):
        """
        Ermittelt gesammt Arbeitszeit und kalkuliert die Zeit für
        jeden Arbeits-Block
        """
        self.statistics["totalTime"] = 0
        self.statistics["day_additionals"] = {}
        self.statistics["time_additionals"] = 0
        days = {}
        for block in timeBlocks:
            day_additional = 0
            time_additional = 0

            blockTime = self.blockTime(block)
            self.statistics["totalTime"] += blockTime

            d = datetime.datetime.fromtimestamp(block[0])
            key = d.strftime("%y%m%d")
            day_name = weekDaysMap[d.strftime("%a")]

            if day_name in self.statistics["day_additionals"]:
                self.statistics["day_additionals"][day_name] += blockTime
            else:
                self.statistics["day_additionals"][day_name] = blockTime

            last_datetime = datetime.datetime.fromtimestamp(block[-1])
            last_time = last_datetime.time()
            for desc, data in time_additionals.items():
                start_time, end_time, factor = data
                if last_time>start_time and end_time<last_time:
                    time_additional = (blockTime * factor) - blockTime
                    time_additional = int(math.ceil(time_additional / 60.0 / 60.0)) # Aufrunden
                    #~ print("%.1fh Aufschlag (%s)" % (time_additional, last_datetime)

            if key in self.dayData:
                self.dayData[key]["blockTime"] += blockTime
                self.dayData[key]["time_additionals"] += time_additional
                self.dayData[key]["block"].append(block)
            else:
                self.dayData[key] = {
                    "dayName"   : day_name,
                    "week"      : int(d.strftime("%W")),
                    "dateStr"   : d.strftime("%d.%m.%Y"),
                    "blockTime" : blockTime,
                    "block"     : [block],
                    "day_additionals": day_additional,
                    "time_additionals": time_additional,
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

                if not dir in dirInfo:
                    dirInfo[dir] = []

                dirInfo[dir].append(file)

            dirs = list(dirInfo.keys())
            dirs.sort()
            for dirName in dirs:
                shortDirName = ".%s" % dirName[len(self.projectPath):]

                if verbose == 1:
                    print("\t%3s files in %s" % (
                        len(dirInfo[dirName]), shortDirName
                    ))
                else:
                    print("\t%s" % shortDirName)
                    for fileName in dirInfo[dirName]:
                        print("\t\t%s" % fileName)
        print()

    def displayResults(self, verbose=0):
        """
        Anzeigen der Ergebnisse
        verbose = 0 -> normale Ansicht, nur Tag und Std.-Anzahl
        verbode = 1 -> Anzahl der geänderten Dateien
        verbode = 2 -> Auflistung der geänderten Dateien
        """
        totalTime = self.statistics["totalTime"]
        print()
        print(">display Results")
        print()
        print("totalTime: %sSec -> %.2fStd -> %.2f 8-Std-Tage" % (
            totalTime, totalTime / 60.0 / 60.0,
            totalTime / 60.0 / 60.0 / 8.0
        ))
        keys = list(self.dayData.keys())
        keys.sort()

        print("-" * 40)

        lastWeek = 0
        total_hours = 0
        for i, key in enumerate(keys):
            #~ print(key)
            data = self.dayData[key]
            #~ print(data)

            dayName = data["dayName"]
            week = data["week"]
            dateStr = data["dateStr"]
            blockTime = data["blockTime"]
            block = data["block"]
            time_additionals = data["time_additionals"]

            #~ print("XXX",week)
            if week != lastWeek: # Leerzeile zwischen den Wochen
                print()
                print("Woche: %s" % week)
                lastWeek = week

            blockTime = int(math.ceil(blockTime / 60.0 / 60.0)) # Aufrunden
            print("%4s - %s, %s:%3i Std ->%4s EUR" % (
                i + 1, dayName, dateStr, blockTime, blockTime * self.hourlyRate
            ))
            total_hours += blockTime
            if verbose:
                self.displayBlock(block, verbose)

        print("_" * 40)
        totalCosts = total_hours * self.hourlyRate
        print(" %s Std * %s EUR (an %i Tage) = %s EUR" % (
            total_hours, self.hourlyRate, len(self.dayData), totalCosts
        ))

        print()
        print("day additionals:")
        for day, factor in self.day_additionals.items():
            if day in self.statistics["day_additionals"]:
                day_time = self.statistics["day_additionals"][day]
                day_hours = day_time / 60.0 / 60.0
                day_hourly_rate = self.hourlyRate*factor
                print("\t%s: %s EUR * %.1f = %.2f EUR/Std | %.2fStd. * %.2f EUR/Std = %.2f EUR" % (
                    day,
                    self.hourlyRate, factor, day_hourly_rate,
                    day_hours, day_hourly_rate, day_hours*day_hourly_rate,
                ))

        self.total_costs = totalCosts
        return self.total_costs

    def displayPushedResults(self, exchangeRatio,
        displayMoneyOnly=False, maxDayTime=14, display_additionals=True):
        """
        Rechnet die Anzahl der Stunden pro Tag so um, das unterm Strich
        ungefähr der gleiche Betrag, trotz eines anderen Stundenlohns
        herrauskommt.
        maxDayTime - Max. Arbeitszeit pro Tag, überzählige Stunden werden auf
            den nächten Tag "verschoben"
        """
        print()
        print("-" * 40)
        print(">PushedResults (exchangeRatio: %s, maxDayTime: %s)" % (
            exchangeRatio, maxDayTime
        ))

        keys = list(self.dayData.keys())
        keys.sort()

        #~ print(keys
        #~ from pprint(import pprint(
        #~ pprint((self.dayData)

        lastWeek = 0
        total_hours = 0

        total_addition_hours = 0
        additionals = {}

        overhang = 0
        for i, key in enumerate(keys):
            additional_info = ""

            #~ print(key)
            data = self.dayData[key]
            #~ print(data)

            dayName = data["dayName"]
            week = data["week"]
            dateStr = data["dateStr"]
            blockTime = data["blockTime"]
            block = data["block"]
            time_additionals = data["time_additionals"]

            #~ print("XXX",week)
            if week != lastWeek: # Leerzeile zwischen den Wochen
                print()
                print("Woche: %s" % week)
                lastWeek = week

            blockTime = blockTime * self.hourlyRate / exchangeRatio
            pushedTime = int(math.ceil(blockTime / 60.0 / 60.0))

            pushedTime += time_additionals

            # Tägliche Abeitszeit begrenzen
            pushedTime += overhang
            if pushedTime > maxDayTime:
                overhang = pushedTime - maxDayTime
                pushedTime = maxDayTime
            else:
                overhang = 0

            if dayName in self.day_additionals:
                factor = self.day_additionals[dayName]
                additional_time = (pushedTime * factor) - pushedTime
                pushedTime += additional_time
                total_addition_hours += additional_time
                if dayName in additionals:
                    additionals[dayName] += additional_time
                else:
                    additionals[dayName] = additional_time

                if display_additionals:
                    additional_info += "(inkl. %.1fStd %s Aufschlag)" % (additional_time, dayName)

            if time_additionals:
                if display_additionals:
                    additional_info += "(inkl. %.1fStd spät Aufschlag)" % time_additionals
                total_addition_hours += time_additionals

            if displayMoneyOnly:
                print("%3s - %s, %s:%4i EUR %s" % (
                    i + 1, dayName, dateStr, pushedTime * exchangeRatio,
                    additional_info
                ))
            else:
                print("%3s - %s, %s:%3i Std %s" % (
                    i + 1, dayName, dateStr, pushedTime,
                    additional_info
                ))
            total_hours += pushedTime

        if overhang > 0:
            print("-> rest overhang: %sStd !!!" % overhang)

        print("_" * 79)

        if display_additionals:
            print()
            print("day additionals:")#, additionals)
            for day, factor in self.day_additionals.items():
                if day in additionals:
                    day_time = additionals[day]
                    day_costs = day_time * exchangeRatio
                    print("\t%s: %sStd * %s EUR = %.2f EUR" % (
                        day,
                        day_time, exchangeRatio, day_time * exchangeRatio
                    ))

        print()
        self.total_costs = total_hours * exchangeRatio
        if displayMoneyOnly:
            if display_additionals:
                print("Gesamt..: %5s EUR (inkl. %sStd (%s EUR) spät Aufschlag)" % (
                    self.total_costs,
                    total_addition_hours, total_addition_hours*exchangeRatio
                ))
            else:
                print("Gesamt..: %5s EUR" % self.total_costs)
        else:
            if display_additionals:
                print("Gesamt..: %s Std * %s EUR = %s EUR (inkl. %sStd (%s EUR) spät Aufschlag)" % (
                    total_hours, exchangeRatio, self.total_costs,
                    total_addition_hours, total_addition_hours*exchangeRatio
                ))
            else:
                print("Gesamt..: %s Std * %s EUR = %s EUR" % (
                    total_hours, exchangeRatio, self.total_costs,
                ))

        return self.total_costs

    def display_unpaid(self, *args):
        if self.total_costs is None:
            raise RuntimeError("Call display methods first!")

        unpaid = self.total_costs - sum(args)
        t = "+".join([str(i) for i in args])
        print("%i EUR - (%s) EUR = %i EUR" % (self.total_costs, t, unpaid))


if __name__ == "__main__":
    import tempfile
    #~ test_path = tempfile.gettempdir()

    test_path = os.path.expanduser("~")

    #~ c = Chronologer(
        #~ projectPath     = test_path,
        #~ hourlyRate      = 80,
    #~ ).displayResults()

    c = Chronologer(
        projectPath=test_path,
        hourlyRate=80,
        maxTimeDiff=60 * 60,
        minBlockTime=55 * 60,
        projectStart=datetime.datetime(year=2005, month=3, day=1),
        projectEnd=datetime.datetime(year=2007, month=3, day=31),
    )

    print("\n" * 3, "="*79)
    print("(verbose: 0)")
    c.displayResults()

    #~ print("\n" * 3, "="*79
    #~ print("(verbose: 1)"
    #~ c.displayResults(verbose=1)

    #~ print("\n" * 3, "="*79
    #~ print("(verbose: 2)"
    #~ c.displayResults(verbose=2)

    #~ print("\n" * 3, "="*79

    # Umrechnung auf anderen Stundenlohn
    c.displayPushedResults(exchangeRatio=35)
    print("\n" * 3, "="*79)
    #~ c.displayPushedResults(exchangeRatio=30)
    #~ print("\n" * 3, "="*79
    #~ c.displayPushedResults(exchangeRatio=35, displayMoneyOnly=True)





