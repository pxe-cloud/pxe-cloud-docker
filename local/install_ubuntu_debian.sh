#!/bin/bash

# Make sure that Docker isn't installed
sudo apt-get remove docker docker-engine docker.io -y

# Install Docker
sudo apt-get update
sudo apt-get install \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common -y

curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
   $(lsb_release -cs) \
   stable"

sudo apt update
sudo apt install docker-ce -y

# Install Docker Compose
sudo apt install python3 python3-pip -y
sudo pip3 install docker-compose

# Enable and start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Install the required packages to compile iPXE
sudo apt install git liblzma-dev -y

echo "To start the services, please run 'python3 start.py'"
