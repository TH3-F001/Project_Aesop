#!/bin/bash

# This one is going to be simple for now,
# We'll make it needlessly complicated later

sudo rm -rf /etc/aesop
sudo rm -rf /srv/aesop
rm -rf ~/.config/aesop
sudo userdel aesop-service
sudo usermod -G aesop-service $(whoami)
sudo groupdel aesop-service
