#!/bin/bash

echo "Set CPU frequency to 966 MHz"
for i in 0 1 2 3
do
   echo performance >  /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor
done

for i in 0 1 2 3

do
   echo -n "CPU$i Frequency = "
   cat /sys/devices/system/cpu/cpu$i/cpufreq/cpuinfo_cur_freq
done