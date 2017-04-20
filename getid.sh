#!/bin/bash

echo "Build Ident from MAC ID"
ID=`ifconfig | grep wlan`
#echo $ID
echo -n "MAC ID = "
ID=`echo ${ID#*HWaddr }` # see https://goo.gl/WLR79p
echo $ID
ID=`echo $ID | /bin/sed 's/://g'`
#echo $ID
echo -n "Ident  = "
ID=`echo $((16#$ID))`
echo $ID


