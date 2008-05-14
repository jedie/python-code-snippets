#!/bin/bash

# from http://ubuntuforums.org/showthread.php?t=442974

function info {
    echo ""
    echo "**** $1 ****"
    echo ""
}
function verbose_eval {
    echo "--------------------------------------------------------------------"
    echo $*
    echo "--------------------------------------------------------------------"
    eval $*
}

if [ $(whoami) != 'root' ]; then
    info "Error: You must start this script with sudo!"
    exit
fi

info "keep all packages"
verbose_eval aptitude keep-all

info "Mark all installed (~i) packages as 'Automatically installed'"
verbose_eval aptitude markauto ~i --schedule-only

info "Mark essential packages as 'manually installed'"
#1. ~i~prequired: This is an aptitude regex formula meaning any installed packages whose priority level is 'required'
#2. ~i~pimportant: This is an aptitude regex formula meaning any installed packages whose priority level is 'important'
#3. ~i~pstandard: This is an aptitude regex formula meaning any installed packages whose priority level is 'standard'.
#Any Debian package has a priotiy value in it's metadata. The priority can be: reaquired, important, standard, optional and extra. Packages belonging to any of the first three priority levels comprise a basic debian system. So they will be kept installed.
#4. ubuntu-minimal: This metapackage depends on all of the packages in the Ubuntu minimal system, that is a functional command-line system.
#5. ubuntu-standard: This metapackage depends on all of the packages in the Ubuntu standard system. This set of packages provides a comfortable command-line Unix-like environment.
#6. linux-generic: This metapackage always depends on the latest generic Linux kernel available.
#7. linux-headers-generic: This metapackage always depends on the latest generic kernel headers available.
verbose_eval aptitude install -R ~i~prequired ~i~pimportant --schedule-only
#ubuntu-minimal ubuntu-standard
#linux-generic linux-headers-generic

info "set all packages from 'packagelist.txt' to 'manually installed'"
verbose_eval aptitude install -R `cat packagelist.txt | grep -v '^#' | tr '\n' ' '` --schedule-only

info "remove unncessary packages"
verbose_eval aptitude install -R

info "revert with: 'sudo aptitude keep-all'"
info "do all changes with: sudo aptitude install -R"