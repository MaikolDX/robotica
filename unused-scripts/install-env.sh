#!/bin/bash

# Update package list
sudo apt-get update

# install python3-venv
sudo apt-get install -y python3-venv

# create env with name "pi-env"
sudo python3 -m venv pi_env

# run: chmod +x install-env.sh
# run: sudo ./install-env.sh
# to active run: source ./pi_env/bin/activate
# to deactivate pi_env, run: deactivate