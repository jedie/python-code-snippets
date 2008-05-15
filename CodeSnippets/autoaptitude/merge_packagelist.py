
"""
/usr/share/doc/python-apt/examples

    python-apt module:
        http://sourceforge.net/projects/python-apt
"""

from pprint import pprint
import datetime

import apt



PACKAGE_FILE = "packagelist.txt"
NEW_PACKAGE_FILE = "filtered_packagelist.txt"


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
        return dependencies
    dependencies = property(dependencies)

    def get_section(self):
        raw_section = self.section
        section = raw_section.rsplit("/", 1)[-1]
        return section




class AptInfo(object):
    def __init__(self):
        print "*"*79
        self.cache = apt.apt_pkg.GetCache()
        self.depcache = apt.apt_pkg.GetDepCache(self.cache)
        self.records = apt.apt_pkg.GetPkgRecords(self.cache)
        self.sourcelist = apt.apt_pkg.GetPkgSourceList()
        print "*"*79

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


class PackageMerger(object):
    def __init__(self, package_list, apt_info):
        self.apt_info = apt_info
        self.package_list = set(package_list)

        self.data = {}
        for package in self.package_list:
            self.data[package] = apt_info.get_package(package)

    def get_section_packages(self, section_name):
        result = set()
        for package_name, data in self.data.iteritems():
            if data.section == section_name:
                result.add(package_name)
        return result

    def get_merged_dependencies(self, package_list):
        dependencies = set()
        for package_name in package_list:
            package = self.data[package_name]
            dep_packages = set(package.dependencies)
            dependencies.update(dep_packages)
        return dependencies

    def filter_metapackages(self):
        """
        delete all package from self.package_list if there exist as
        dependencies in a metapackage
        """
        metapackages = self.get_section_packages(section_name="metapackages")
        print " * Found metapackages:"
        print ">>>", ", ".join(metapackages)

#        print len(self.package_list), self.package_list
#        packages = self.package_list -  metapackages
#        print len(packages), packages

        dependencies = self.get_merged_dependencies(metapackages)
        print dependencies

        print " * Unused packages, because there are in the meatepackages:"
        print ">>>", ", ".join(self.package_list.intersection(dependencies))

        # Update package list
        self.package_list -= dependencies

    def write_package_list(self, filename):
        write_data = {}
        for package_name in self.package_list:
            section = self.data[package_name].get_section()
            if section not in write_data:
                 write_data[section] = set()

            write_data[section].add(package_name)

        pprint(write_data)

        f = file(filename, "w")
        f.writelines([
            "#" * 79, "\n",
            "# automatic generated with %s" % __file__, "\n",
            "# (%s)" % datetime.datetime.now(), "\n",
            "#" * 79, "\n",
        ])
        for section, packages in sorted(write_data.iteritems()):
            f.writelines([
                "#" * 20, "\n",
                "# %s" % section, "\n",
                "#" * 20, "\n",
            ])
            f.write("\n".join(sorted(packages)))
            f.write("\n\n")

        f.close()





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


if __name__ == "__main__":
    package_list = get_packages()
    print package_list

    apt_info = AptInfo()
    packages = PackageMerger(package_list, apt_info)
    packages.filter_metapackages()
    packages.write_package_list(NEW_PACKAGE_FILE)


#
#    print "-"*79
#    pkg = apt_info.get_package("ubuntu-minimal")
#    print pkg.summary
#    print pkg.dependencies
#    print "-"*79
#
#    apt_info.debug_package("ubuntu-minimal")
#
#    count = 0
#    for package_name in packages:
#        count += 1
#        if count > 3: break
#        apt_info.debug_package(package_name)


