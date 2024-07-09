#!/bin/bash

# This one is going to be simple for now,
# We'll make it needlessly complicated later

sudo rm -rf /etc/aesop
sudo rm -rf /srv/aesop
sudo rm -rf /opt/aesop
rm -rf ~/.config/aesop
sudo usermod -G aesop-service $(whoami)
sudo usermod -G aesop-service aesop-service
sudo userdel aesop-service --force
sudo groupdel aesop-service --force
