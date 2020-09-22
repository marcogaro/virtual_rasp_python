#!/bin/bash

sudo sh -c "echo '127.0.0.1 ubuntu' >> /etc/hosts"

sudo apt update
sudo apt upgrade
sudo apt install -y python3.8
sudo apt install -y python3-pip

#installazione libfuse
sudo pip3 install meson
sudo apt-get install -y pkg-config
sudo apt-get install ninja-build
sudo pip3 install pytest

git clone https://github.com/libfuse/libfuse.git
cd libfuse/
mkdir build; cd build
sudo ldconfig
meson ..
ninja
sudo python3 -m pytest test/

sudo ninja install
pip3 install pyfuse3

sudo apt update
sudo apt install snapd
sudo snap install lxd 
lxd --version

sudo ldconfig

sudo addgroup gpio
sudo usermod -a -G gpio ubuntu

cat<<EOF | sudo tee /etc/udev/rules.d/99-gpio.rules
SUBSYSTEM=="input", GROUP="input", MODE="0660"
SUBSYSTEM=="i2c-dev", GROUP="i2c", MODE="0660"
SUBSYSTEM=="spidev", GROUP="spi", MODE="0660"
SUBSYSTEM=="bcm2835-gpiomem", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c '\\
chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio;\\
chown -R root:gpio /sys/devices/virtual/gpio && chmod -R 770 /sys/devices/virtual/gpio;\\
chown -R root:gpio /sys\$devpath && chmod -R 770 /sys\$devpath\\
'"
KERNEL=="ttyAMA[01]", PROGRAM="/bin/sh -c '\\
ALIASES=/proc/device-tree/aliases; \\
if cmp -s \$ALIASES/uart0 \$ALIASES/serial0; then \\
echo 0;\\
elif cmp -s \$ALIASES/uart0 \$ALIASES/serial1; then \\
echo 1; \\
else \\
exit 1; \\
fi\\
'", SYMLINK+="serial%c"
KERNEL=="ttyS0", PROGRAM="/bin/sh -c '\\
ALIASES=/proc/device-tree/aliases; \\
if cmp -s \$ALIASES/uart1 \$ALIASES/serial0; then \\
echo 0; \\
elif cmp -s \$ALIASES/uart1 \$ALIASES/serial1; then \\
echo 1; \\
else \\
exit 1; \\
fi \\
'", SYMLINK+="serial%c"
EOF

echo "Setup completed. Please, reboot and then launch 'sudo lxd init' and 'allow other users'."
