#!/bin/bash

if [ "$#" -eq 1 ] ; then
    	nome=$1	
    	echo "virtual rasp name: "$nome ;
elif [ "$#" -eq 0 ] ; then
	echo "virtual rasp name? "
	read -r b
	nome=$b ;	
else
   	echo "error: missing mandatory name" 
   	exit
fi


echo "virtual rasp name: "$nome

grep -w $nome virtual_rasp.ini
result=$?
echo "result: " $result 
 
if [ $result -eq 0  ]; then
	echo "name in virtual_rasp.ini";
else 
	echo "missing name in virtual_rasp.ini"; 
	exit;
fi


pass="filesystem_virtualizer.py"
echo $pass

echo "restarting filesystem "$nome"!"

sudo umount --force /gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio
sudo umount --force /gpio_mnt/"$nome"/sys/class/gpio

python3 "$pass" /sys/devices/platform/soc/3f200000.gpio /gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio/ $nome &
python3 "$pass" /sys/class/gpio/ /gpio_mnt/"$nome"/sys/class/gpio/ $nome &
