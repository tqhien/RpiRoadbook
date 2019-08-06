#!/bin/sh
# On recupere les secteurs deja utilises et on calcule la taille des deux partitions a creer
DISK_SIZE=$(fdisk -l /dev/mmcblk0 | grep Disk | awk '{print $7-1}')
LAST_SECTOR=$(fdisk -l /dev/mmcblk0 | grep mmcblk0p2 | awk '{print $5+1}')
echo $DISK_SIZE
echo $LAST_SECTOR
let FREE_SIZE=$DISK_SIZE-$LAST_SECTOR-2
let HALF_SIZE=$FREE_SIZE/2
echo $FREE_SIZE
echo $HALF_SIZE

# on va creer les partitions avec fdisk
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk /dev/mmcblk0
  n # new partition
  p # primary partition
  3 # partition number 3, first new one
    # default - start at the beginning of unallocated free space
  +$HALF_SIZE # half the free space
  n # new partition again
  p # primary partition, no number as it is the last one
    # default - start at the end of previously created one
  +$HALF_SIZE # half the free space
  p # print the in-memory partition table
  w # save and quit
EOF

# on copie la suite du traitement
mount / -o rw,remount
sleep .5
cp /home/rpi/scripts/S02_gen_btrfs.sh /etc/init.d/S02_gen_btrfs.sh
chmod +x /etc/init.d/S02_gen_btrfs.sh

# on supprime le script courant
rm /etc/init.d/S01_gen_piusb.sh

# on s'assure d'ecrire le cache sue le disque
sync
mount / -o ro,remount
# deux securites valent mieux qu'une
sleep 5
# on redemarre
reboot


