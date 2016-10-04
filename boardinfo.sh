#!/bin/bash

echo "========================================================================"
echo "Board Information"
echo "========================================================================"
echo

file="board.sh"
if [ -f "$file" ]
then
  source $file
else
  echo "No board description avaliable"
fi

echo
echo "--- CPU Info -----------------------------------------------------------"
cat /proc/cpuinfo
echo
echo "--- Linux Version ------------------------------------------------------"
uname -a
echo
echo "--- Uptime -------------------------------------------------------------"
uptime
echo
echo "--- IP Address ---------------------------------------------------------"
ip addr show | grep -w "inet 192"
echo
echo "--- Memory Usage -------------------------------------------------------"
free -
echo
df -h
echo
echo "--- USB ----------------------------------------------------------------"
lsusb -tv
echo
