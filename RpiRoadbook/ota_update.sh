#!/bin/sh

if [ -e "/mnt/piusb/ota/ota.tar.gz" ]
then
    echo "Fichier OTA présent"
    mount / -o rw,remount
    sleep .5
    tar -C / -xvf "/mnt/piusb/ota/ota.tar.gz"; rm "/mnt/piusb/ota/ota.tar.gz"
    sync
    mount / -o ro,remount
else
    echo "Aucun fichier OTA"
fi
