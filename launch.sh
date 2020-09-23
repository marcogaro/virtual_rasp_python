#!/bin/bash

if [ "$#" -eq 1 ] ; then
    	nome=$1	
    	echo "name of virtual rasp: "$nome ;
elif [ "$#" -eq 0 ] ; then
	echo "name of virtual rasp? "
	read -r b
	nome=$b ;	
else
   	echo "error" 
   	exit
fi
   
   
grep -w $nome example.ini
result=$?
echo "result: " $result 
 
if [ $result -eq 0  ]; then
	echo "name in example.ini";
else 
	echo "missing name in example.ini"; 
	exit;
fi
   
pass="examplenuovo.py"

echo "$nome"
echo "$pass"
   
   
lxc list  -c n | grep -w $nome
result=$?
echo "result: " $result 
 
if [ $result -eq 0  ]; then
	echo "virtual rasp already exists";
	./destroynuovo.sh $nome;
else 
	echo "virtual rasp doesn't exist"; 
fi

   
lxc list   
  
#da qui creo container
echo "Creating virtual rasp "$nome"!"

lxc launch ubuntu:16.04 "$nome"
sleep 20
lxc exec "$nome" -- sudo --login --user ubuntu cat /etc/group
lxc exec "$nome" -- sudo --login --user ubuntu cat /etc/group


sleep 3
sudo mkdir -p /gpio_mnt/"$nome"
sudo chmod 777 -R /gpio_mnt/"$nome"
sudo mkdir -p /gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio
sudo mkdir -p /gpio_mnt/"$nome"/sys/class/gpio

sudo mkdir -p /gpio_mnt/"$nome"/sys/devices/platform/soc/soc\:firmware/soc\:firmware\:expgpio/gpio/gpiochip504/

sleep 3




lxc exec "$nome" -- addgroup gpio
sleep 20
lxc exec "$nome" -- usermod -a -G gpio ubuntu
sleep 1

lxc exec "$nome" -- sudo --login --user ubuntu cat /etc/group





lxc exec "$nome" -- mkdir -p /gpio_mnt/sys/class/gpio
lxc exec "$nome" -- mkdir -p /gpio_mnt/sys/devices/platform/soc/3f200000.gpio

lxc exec "$nome" -- mkdir -p /gpio_mnt/sys/devices/platform/soc/soc\:firmware/soc\:firmware\:expgpio/gpio/gpiochip504/

lxc exec "$nome" -- mkdir -p /gpio_mnt/sys/firmware/devicetree/base/soc/gpio@7e200000/

lxc exec "$nome" -- mkdir -p /gpio_mnt/sys/bus/gpio/
#######################################
lxc exec "$nome" -- mkdir -p /gpio_mnt/sys/bus/platform/drivers/
lxc exec "$nome" -- mkdir -p /gpio_mnt/sys/bus/platform/




sudo chmod -R 777 /gpio_mnt/"$nome"

lxc config set "$nome" security.privileged true
lxc restart "$nome"




lxc config device add "$nome" gpiomnt disk source=/gpio_mnt/"$nome"/sys/class/gpio path=/gpio_mnt/sys/class/gpio
lxc config device add "$nome" devicesmnt disk source=/gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio path=/gpio_mnt/sys/devices/platform/soc/3f200000.gpio

lxc config device add "$nome" socmnt disk source=/sys/devices/platform/soc/soc\:firmware/soc\:firmware\:expgpio/gpio/gpiochip504/ path=/gpio_mnt/sys/devices/platform/soc/soc\:firmware/soc\:firmware\:expgpio/gpio/gpiochip504/


#così in /sys/class/gpio vedo quello che vedrei su /gpio_mnt...
lxc config device add "$nome" gpio disk source=/gpio_mnt/"$nome"/sys/class/gpio path=/sys/class/gpio
lxc config device add "$nome" devices disk source=/gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio path=/sys/devices/platform/soc/3f200000.gpio

lxc config device add "$nome" soc disk source=/sys/devices/platform/soc/soc\:firmware/soc\:firmware\:expgpio/gpio/gpiochip504/ path=/sys/devices/platform/soc/soc\:firmware/soc\:firmware\:expgpio/gpio/gpiochip504/

#lxc config device add "$nome" firmware disk source=/sys/firmware/devicetree/base/soc/gpio@7e200000/ path=/sys/firmware/devicetree/base/soc/gpio@7e200000/

#lxc config device add "$nome" bus disk source=/sys/bus/gpio/ path=/sys/bus/gpio/


sleep 2

ls

sudo chmod -R 777 /sys/class/gpio/
sudo chmod -R 777 /sys/devices/platform/soc/
sudo chmod -R 777 /gpio_mnt/"$nome"
sudo chmod -R 777 /gpio_mnt/"$nome"/sys/

sudo groupadd gpio
sudo chgrp gpio -R /sys/class/gpio/

sleep 10

python3 "$pass" /sys/devices/platform/soc/3f200000.gpio /gpio_mnt/"$nome"/sys/devices/platform/soc/3f200000.gpio/ $nome &
python3 "$pass" /sys/class/gpio/ /gpio_mnt/"$nome"/sys/class/gpio/ $nome &

cd

lxc exec "$nome" -- su --login ubuntu -l


