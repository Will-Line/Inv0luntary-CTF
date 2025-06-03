#! /bin/bash

wget -O /etc/yum.repos.d/snapd.repo https://bboozzoo.github.io/snapd-amazon-linux/al2023/snapd.repo
dnf install snapd -y

sleep 5
snap install core
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
certbot --nginx
printf "\n"
printf "Y"
printf "involuntaryctf.net"
