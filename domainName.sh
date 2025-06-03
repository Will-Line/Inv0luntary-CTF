#! /bin/bash

wget -O /etc/yum.repos.d/snapd.repo https://bboozzoo.github.io/snapd-amazon-linux/al2023/snapd.repo
dnf install snapd -y
echo snapd installed

sleep 5
snap install core
snap install --classic certbot
echo certbot installed
ln -s /snap/bin/certbot /usr/bin/certbot
printf "\nY\ninvoluntaryctf.net\n" | certbot --nginx
printf "\n"
printf "Y"
printf "involuntaryctf.net"
echo domain name set up



