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
echo "http://www.nomachine.com/ar/view.php?ar_id=AR01C00126"

if [ $(whoami) != 'root' ]; then
    info "Error: You must start this script with sudo!"
    exit
fi

info "generate the new keys with nxserver utility"
verbose_eval /usr/NX/scripts/setup/nxserver --keygen

info "setup file rights"
verbose_eval chown nx:root /usr/NX/home/nx/.ssh/*
verbose_eval chmod 0644 /usr/NX/home/nx/.ssh/*

info "The private key for the clients:"
verbose_eval cat /usr/NX/share/keys/default.id_dsa.key
info "Copy&Paste to update your clients!"

echo 'ENTER'
read 'ENTER'