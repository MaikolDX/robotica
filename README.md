# README #

Setup Instructions

### Setup your raspberry pi ###

* For instructions on raspberry pi setup, please see: https://www.youtube.com/watch?v=e8thKtjkAv0
* Download and Open "Raspberry Pi Imager"
* Set Advanced Options 
    * press cntrl + shift + X to open Advanced Options
    * enable ssh, set pi username, ssh password, and other necessary settings. Please see [link above](https://www.youtube.com/watch?v=e8thKtjkAv0)
    * select your pi device, operating system image, and storage.
    * click "Next" or burn image into your sd-card.
    * put your sd-card into your raspberry pi.

### Construct your circuit ###

* See "circuit" folder for circuit connection image.


### SSH into your Pi ###

* You can use Visual studio to ssh and copy files into your raspberry pi
* it is preferrable to use cmd or terminal for ssh installation. to ssh using terminal, run:
    * ssh pi@raspberrypi-001.local

### Install and run the application ###
1. expand File system if not expanded:  
    * check if file system is expanded:
        * run: df -h
    * to expand:
        * run: sudo raspi-config  
    * use arrow keys to 
        * move to "Advanced Options"
    * use "Enter" to select "Advanced Options"
    * use "Enter" to select "Expand Filesystem"
    * press "Right Arrow Key" twice to htghlight "Finish"
    * you will be asked to reboot. select "YES" and press enter.

2. reboot your raspberry pi
    * run: sudo reboot
    * or shutdown & restart 
        * run: sudo shutdown now

3. install opencv (19 minutes):
    * run: chmod +x install-1-cv.sh
    * run: sudo ./install-1-cv.sh
    * check if opencv is installed:
        * run: python
        * run: import cv2
        * to exit python run: quit()
        * if not installed, run: 
            * sudo pip uninstall dlib
            * sudo rm -rf "$(pip3 cache dir)"
            * sudo pip3 install --upgrade --force-reinstall --no-cache-dir opencv-python==4.5.1.48

4. install face recognition (2 minutes):
    * run: chmod +x install-2-face-recognition.sh
    * run: sudo ./install-2-face-recognition.sh
    * check if face_recognition.py is installed:
        * run: python
        * run: import face_recognition
        * to exit python run: quit()
        * if not installed, run: 
            * sudo pip3 install --upgrade --force-reinstall --no-cache-dir face-recognition==1.3.0

5. install other application dependencies:
    * run: chmod +x install-3.sh
    * run: sudo ./install-3.sh

6. edit the ".env" file to use http:// or https://

7. run: 
    * python main.py