#!/bin/sh

# inserer ici l'affichage de l'image d'info
# dd if=/root/update.fb of=/dev/fb0 bs=1536000 count=1 > /dev/null 2>&1
# on cree le noeud udev pour le btrfs
mknod /dev/btrfs-control c 10 234
# on cree le systeme de fichiers btrfs sur la partition 3
mkfs.btrfs -f /dev/mmcblk0p3
# idem sur la partition 4
mkfs.btrfs -f /dev/mmcblk0p4
# On monte la 1ere partition
mount /dev/mmcblk0p3 /mnt/piusb
# On ajoute la 2eme partition
btrfs device add -f /dev/mmcblk0p4 /mnt/piusb
# et on definit le raid miroir
btrfs balance start -dconvert=raid1 -mconvert=raid1 /mnt/piusb

# maintenant on peut decompresser l'archive initiale
mount / -o rw,remount
sleep .5
tar -C / -xvf "/home/rpi/scripts/init.tar.gz"
sleep .5

# on supprime le script courant
rm /etc/init.d/S02_gen_btrfs.sh
sync
mount / -o ro,remount

# et on redemarre une derniere fois
reboot

