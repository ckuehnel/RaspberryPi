#!/bin/bash

DEVICE=/dev/ttyUSB0

#MQTT
BROKER="m20.cloudmqtt.com"
BRUSER="rawyjpid"
BRPASSW="ah52k3gjd8JS"
BRPORT=12394
TEMPTOP="DHT11/ASH2200/temperature"
HUMITOP="DHT11/ASH2200/humidity"

#Thingspeak
api_key='LTEMZXC99DQGCNMR'

# USB-WED1-2 connected?
if [ "$(ls $DEVICE)" ]; then
    stty -F $DEVICE 9600
    echo -n RESET > /dev/ttyUSB0 
    sleep 2
    echo -n INIT > /dev/ttyUSB0
    sleep 2
    echo -n "USB-WED1-2 connected - "
    stty -F $DEVICE | grep speed | cut -d ";" -f1
    echo "Read Data from USB-WED1-2 - stop by Ctrl-C"
    echo "Measuring periode about 3 minutes"
    while read line
    do
#       echo $line
       if [ "$(echo $line | grep '$1')" ]; then
          TEMP="$(echo $line | grep '$1' | cut -d ";" -f4)"
          HUMI="$(echo $line | grep '$1' | cut -d ";" -f12)"
          DATE="$(date +"%d-%m-%Y")"
          HOUR="$(date +"%T")"
          echo "$DATE $HOUR $TEMP $HUMI" > usb-wed1-2.dat
          cat usb-wed1-2.dat
          curl --data \
          "api_key=$api_key&field1=$TEMP&field2=$HUMI&field3=$DATE" \
          https://api.thingspeak.com/update > log 2>&1
          mosquitto_pub -h $BROKER -u $BRUSER -P $BRPASSW -p $BRPORT -t $TEMPTOP -m $TEMP
          mosquitto_pub -h $BROKER -u $BRUSER -P $BRPASSW -p $BRPORT -t $HUMITOP -m $HUMI
       fi
    done < $DEVICE
else
    echo "No USB-WED1-2 connected"
fi

