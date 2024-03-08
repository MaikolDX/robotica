#!/bin/bash
# Installing OpenCV 4.6.0

sudo rm -rf "$(pip3 cache dir)"

sudo pip3 install --upgrade --force-reinstall --no-cache-dir face-recognition==1.3.0



# run: chmod +x install-2-face-recognition.sh
# run: sudo ./install-2-face-recognition.sh