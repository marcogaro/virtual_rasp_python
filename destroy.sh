#!/bin/bash

if [ "$#" -eq 1 ] ; then
    	nome=$1	
    	echo "virtual rasp name: "$nome ;
elif [ "$#" -eq 0 ] ; then
	echo "virtual rasp name? "
	read -r b
	nome=$b ;	
else
   	echo "error" 
   	exit
fi


echo "Destroying virtual rasp "$nome"!"

sudo umount /gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio
sudo umount /gpio_mnt/"$nome"/sys/class/gpio

sudo umount --force /gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio
sudo umount --force /gpio_mnt/"$nome"/sys/class/gpio

lxc config device remove "$nome" gpio 
lxc config device remove "$nome" devices
lxc config device remove "$nome" soc
lxc config device remove "$nome" gpiomnt
lxc config device remove "$nome" devicesmnt
lxc config device remove "$nome" socmnt

sudo rm -rf /gpio_mnt/"$nome"
sudo rm -rf /tmp/passthrough/

lxc delete --force "$nome"
