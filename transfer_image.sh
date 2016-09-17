#!/bin/bash

# Prepare name of folder of the day
date=`date +"%Y%m%d"`
echo $date

# Read last snapshot image from folder of the day
last=`ls /home/pi/IPCAM/$date/IMG001 -tr | tail -1`
echo $last

# Copy last snapshot to folder /IPCAM
cp /home/pi/IPCAM/$date/IMG001/$last /home/pi/IPCAM/ipcam.jpg

# Transfer last snapshot to external webserver
curl -T  /home/pi/IPCAM/ipcam.jpg ftp://ckuehnel.ch/IPCAM/ --user www865:ckszsz

# Delete old images(s)
rm -r /home/pi/IPCAM/$date/

echo "Done."
