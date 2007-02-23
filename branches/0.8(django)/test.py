#~ import sys, inspect
#~ class PrintLocator(object):
    #~ """
    #~ Very slow! But in some case very helpfully ;)
    #~ """
    #~ def __init__(self, out):
        #~ self.out = out
        #~ self.oldFileinfo = ""

    #~ def write(self, *txt):
        #~ # Angaben zur Datei, Zeilennummer, aus dem die Nachricht stammt
        #~ stack = inspect.stack()[1]
        #~ fileinfo = (stack[1].split("/")[-1][-40:], stack[2])

        #~ if fileinfo != self.oldFileinfo:
            #~ self.oldFileinfo = fileinfo
            #~ self.out.write(
                #~ "<br />[stdout/stderr write from: ...%s, line %s]\n" % fileinfo
            #~ )

        #~ txt = " ".join([str(i) for i in txt])
        #~ self.out.write(txt)

    #~ def isatty(self):
        #~ return False

#~ old_stdout = sys.stdout
#~ sys.stdout = sys.stderr = PrintLocator(old_stdout)

import inspect

def inspect_object(obj, display_underscore=False):
    #~ display_underscore=True

    def print_info(obj, method_name):
        method = getattr(inspect, method_name)
        try:
            print "%-15s: %s" % (method_name, repr(method(obj)))
        except Exception, e:
            #~ print "Error:", e
            pass

    print "Inspect", obj
    print "repr:", repr(obj)

    inspect_methods = inspect.getmembers(inspect)
    inspect_methods = [i[0] for i in inspect_methods if i[0].startswith("get")]
    for method_name in inspect_methods:
        print_info(obj, method_name)
    print "-"*80

    members = inspect.getmembers(obj)
    if (not display_underscore):
        members = [i for i in members if not i[0].startswith("__")]

    for member in members:
        print "%-20s %s" % member
    print "-"*80

    for name,member in members:
        try:
            print "XXX" + inspect.getargvalues(member)
        except:
            pass

        if not callable(member):
            continue

        print "%-20s:" % name,
        try:
            print member()
        except Exception, e:
            print "Error:", e

    print "-"*80

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "PyLucid.settings"

from PyLucid.urls import urlpatterns

inspect_object(urlpatterns)
#~ inspect_object(urlpatterns[0])

#~ RegexURLResolver = urlpatterns[0]
#~ url_patterns = RegexURLResolver.url_patterns
#~ print url_patterns

#~ RegexURLPattern = urlpatterns[1:]




