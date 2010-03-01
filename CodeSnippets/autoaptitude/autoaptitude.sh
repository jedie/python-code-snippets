#!/bin/bash

# based on: http://ubuntuforums.org/showthread.php?t=442974

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

info "You should run 'aptitude update' before!"

info "keep all packages"
verbose_eval aptitude keep-all

info "Mark all installed packages as 'Automatically installed'"
verbose_eval aptitude markauto ~i --schedule-only

info "revert with: 'sudo aptitude keep-all' - aboard with Strg-C"

info "Remove unnecessary packages, except 'essential packages' and all packages from 'packagelist.txt'"
verbose_eval aptitude install -R ~i~prequired ~i~pimportant `cat packagelist.txt | grep -v '^#' | tr '\n' ' '`
