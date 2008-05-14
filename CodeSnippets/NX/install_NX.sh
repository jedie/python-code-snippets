#!/bin/bash

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

info "Links:"
echo "http://wiki.ubuntuusers.de/FreeNX"
echo "http://www.nomachine.com/download.php"

if [ $(whoami) != 'root' ]; then
    info "Error: You must start this script with sudo!"
    exit
fi

info "Install NX .deb"
verbose_eval dpkg -i *.deb

echo 'ENTER'
read 'ENTER'