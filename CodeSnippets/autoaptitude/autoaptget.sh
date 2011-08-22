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

info "You should run 'apt-get update' before!"

info "Mark all packages as 'Automatically installed'"
verbose_eval apt-mark markauto `apt-mark showauto`

info "Remove unnecessary packages, except 'essential packages' and all packages from 'packagelist.txt'"
verbose_eval apt-mark unmarkauto `cat packagelist.txt | grep -v '^#' | tr '\n' ' '`

verbose_eval apt-get install `cat packagelist.txt | grep -v '^#' | tr '\n' ' '`

verbose_eval apt-get autoremove
