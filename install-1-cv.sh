#!/bin/bash
# Installing OpenCV 4.6.0

echo "Installing required dependencies"

sudo apt-get install -y build-essential cmake git unzip pkg-config
sudo apt-get install -y libjpeg-dev libtiff-dev libpng-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install -y libgtk2.0-dev libcanberra-gtk* libgtk-3-dev
sudo apt-get install -y libgstreamer1.0-dev gstreamer1.0-gtk3
sudo apt-get install -y libgstreamer-plugins-base1.0-dev gstreamer1.0-gl
sudo apt-get install -y libxvidcore-dev libx264-dev

sudo apt-get install -y python3-dev python3-numpy python3-pip python3-pyqt5 zip
sudo apt-get install -y libtbb2 libtbb-dev libdc1394-22-dev
sudo apt-get install -y libv4l-dev v4l-utils
sudo apt-get install -y libopenblas-dev libatlas-base-dev libblas-dev
sudo apt-get install -y liblapack-dev gfortran libhdf5-dev
sudo apt-get install -y libprotobuf-dev libgoogle-glog-dev libgflags-dev
sudo apt-get install -y protobuf-compiler

#extras
echo "Installing Extras"
sudo apt-get install -y libhdf5-serial-dev libhdf5-103
sudo apt-get install -y libqtgui4
sudo apt-get install -y libqtwebkit4
sudo apt-get install -y libqt4-test
sudo apt-get install -y libjasper-dev
sudo apt-get install -y libtiff5-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev
sudo apt-get install -y libpango1.0-dev
sudo apt-get install -y libqt5gui5
sudo apt-get install -y libqt5webkit5
sudo apt-get install -y libqt5test5
sudo apt-get install -y libopenexr25
sudo apt-get install -y libopenexr23
sudo apt-get install -y libcblas3
echo "Finished Extras"

echo "Installing dlib, numpy and opencv-contrib-python"
sudo pip3 install dlib
sudo pip3 install numpy

# start installation

# sudo pip3 install --upgrade --force-reinstall --no-cache-dir opencv-contrib-python
sudo pip3 install --upgrade --force-reinstall --no-cache-dir opencv-python==4.5.1.48
sudo apt-get install -y libopenexr25

echo "Successfully installed dlib, numpy and opencv-contrib-python"




# run: chmod +x install-1-cv.sh
# run: sudo ./install-1-cv.sh