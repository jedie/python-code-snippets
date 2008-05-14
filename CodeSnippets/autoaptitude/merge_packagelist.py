
import apt


PACKAGE_FILE = "packagelist.txt"


class Package(apt.Package):
    """
    Expanded version of apt.Package
    """
    def dependencies(self):
        """
        returns a list of package names from candidate dependencies
        """
        dependencies = []
        for dep in self.candidateDependencies:
            for o in dep.or_dependencies:
                dependencies.append(o.name)
        return sorted(dependencies)
    dependencies = property(dependencies)



class AptInfo(object):
    def __init__(self):
        self.cache = apt.apt_pkg.GetCache()
        self.depcache = apt.apt_pkg.GetDepCache(self.cache)
        self.records = apt.apt_pkg.GetPkgRecords(self.cache)
        self.sourcelist = apt.apt_pkg.GetPkgSourceList()

    def get_package(self, package_name):
        """
        returns a Package instance
        """
        pkgiter = self.cache[package_name]
#        pkg = apt.Package(
        package = Package(
            self.cache, self.depcache, self.records, self.sourcelist, None,
            pkgiter
        )
#        package = Package(pkg)
        return package

    def debug_package(self, package_name):
        package = self.get_package(package_name)

        print "_"*79
        print "\tDEBUG for package '%s':" % package_name
        print "-"*79
        for i in sorted(dir(package)):
            if not i.startswith("_"):
                print "'%s': %r" % (i, getattr(package, i, "---"))
        print "-"*79


def get_packages():
    """
    returns all package name from PACKAGE_FILE
    """
    print "read '%s'..." % PACKAGE_FILE
    f = file(PACKAGE_FILE, "r")
    lines = f.readlines()
    f.close()

    packages = []
    for line in lines:
        if line.startswith("#"):
            continue
        line = line.strip()
        if line == "":
            continue
        # Strip comment
        line = line.split("#", 1)[0]
        packages.append(line)

    print "done."
    return sorted(packages)

#import apt
#
if __name__ == "__main__":
    packages = get_packages()
    print packages

    apt_info = AptInfo()

    print "-"*79
    pkg = apt_info.get_package("ubuntu-minimal")
    print pkg.summary
    print pkg.dependencies
    print "-"*79

    apt_info.debug_package("ubuntu-minimal")

    count = 0
    for package_name in packages:
        count += 1
        if count > 3: break
        apt_info.debug_package(package_name)


