#!/bin/bash

# Update package list
sudo apt-get update

# Install required packages
sudo apt-get install -y build-essential python3-dev

# Install sqlite3
sudo apt-get install -y sqlite3

sudo sqlite3 --version

# Delete the existing file
sudo rm app_db.db

# Install pip3
sudo apt-get install -y python3-pip

# Install all app requirements
sudo pip3 install -r requirements.txt

# create SSL certificates
openssl req -x509 -nodes -newkey rsa:4096 -keyout localhost-ssl_keyfile.pem -out localhost-ssl_certfile.pem -days 365

sudo chmod +r ./localhost-ssl_keyfile.pem ./localhost-ssl_certfile.pem


# run: chmod +x install-3.sh
# run: sudo ./install-3.sh