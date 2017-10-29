from btle import UUID, Peripheral, DefaultDelegate
import struct
import math

def _TI_UUID(val):
    return UUID("%08X-0451-4000-b000-000000000000" % (0xF0000000+val))

class SensorBase:
    # Derived classes should set: svcUUID, ctrlUUID, dataUUID
    sensorOn  = struct.pack("B", 0x01)
    sensorOff = struct.pack("B", 0x00)

    def __init__(self, periph):
        self.periph = periph
        self.service = None
        self.ctrl = None
        self.data = None

    def enable(self):
        if self.service is None:
            self.service = self.periph.getServiceByUUID(self.svcUUID)
        if self.ctrl is None:
            self.ctrl = self.service.getCharacteristics(self.ctrlUUID) [0]
        if self.data is None:
            self.data = self.service.getCharacteristics(self.dataUUID) [0]
        if self.sensorOn is not None:
            self.ctrl.write(self.sensorOn,withResponse=True)

    def read(self):
        return self.data.read()

    def disable(self):
        if self.ctrl is not None:
            self.ctrl.write(self.sensorOff)

    # Derived class should implement _formatData()

def calcPoly(coeffs, x):
    return coeffs[0] + (coeffs[1]*x) + (coeffs[2]*x*x)

class IRTemperatureSensor(SensorBase):
    svcUUID  = _TI_UUID(0xAA00)
    dataUUID = _TI_UUID(0xAA01)
    ctrlUUID = _TI_UUID(0xAA02)

    zeroC = 273.15 # Kelvin
    tRef  = 298.15
    Apoly = [1.0,      1.75e-3, -1.678e-5]
    Bpoly = [-2.94e-5, -5.7e-7,  4.63e-9]
    Cpoly = [0.0,      1.0,      13.4]

    def __init__(self, periph):
        SensorBase.__init__(self, periph)
        self.S0 = 6.4e-14
    def read(self):
        '''Returns (ambient_temp, target_temp) in degC'''

        # See http://processors.wiki.ti.com/index.php/SensorTag_User_Guide#IR_Temperature_Sensor
        (rawVobj, rawTamb) = struct.unpack('<hh', self.data.read())
        tAmb = rawTamb / 128.0
        Vobj = 1.5625e-7 * rawVobj

        tDie = tAmb + self.zeroC
        S   = self.S0 * calcPoly(self.Apoly, tDie-self.tRef)
        Vos = calcPoly(self.Bpoly, tDie-self.tRef)
        fObj = calcPoly(self.Cpoly, Vobj-Vos)

        tObj = math.pow( math.pow(tDie,4.0) + (fObj/S), 0.25 )
        return (tAmb, tObj - self.zeroC)
	return(rawVobj, rawTamb)

class AccelerometerSensor(SensorBase):
    svcUUID  = _TI_UUID(0xAA10)
    dataUUID = _TI_UUID(0xAA11)
    ctrlUUID = _TI_UUID(0xAA12)

    def __init__(self, periph):
        SensorBase.__init__(self, periph)

    def read(self):
        '''Returns (x_accel, y_accel, z_accel) in units of g'''
        x_y_z = struct.unpack('<hhh', self.data.read())
        return tuple([ (val/64.0) for val in x_y_z ])
	#return tuple(x_y_z)

class HumiditySensor(SensorBase):
    svcUUID  = _TI_UUID(0xAA20)
    dataUUID = _TI_UUID(0xAA21)
    ctrlUUID = _TI_UUID(0xAA22)

    def __init__(self, periph):
        SensorBase.__init__(self, periph)

    def read(self):
        '''Returns (ambient_temp, rel_humidity)'''
        (rawT, rawH) = struct.unpack('<HH', self.data.read())
        temp = -46.85 + 175.72 * (rawT / 65536.0)
        RH = -6.0 + 125.0 * ((rawH & 0xFFFC)/65536.0)
        return (temp, RH)


class MagnetometerSensor(SensorBase):
    svcUUID  = _TI_UUID(0xAA30)
    dataUUID = _TI_UUID(0xAA31)
    ctrlUUID = _TI_UUID(0xAA32)

    def __init__(self, periph):
        SensorBase.__init__(self, periph)

    def read(self):
        '''Returns (x, y, z) in uT units'''
        x_y_z = struct.unpack('<hhh', self.data.read())
        return tuple([ 1000.0 * (v/32768.0) for v in x_y_z ])
        

class BarometerSensor(SensorBase):
    svcUUID  = _TI_UUID(0xAA40)
    dataUUID = _TI_UUID(0xAA41)
    ctrlUUID = _TI_UUID(0xAA42)
    calUUID  = _TI_UUID(0xAA43)
    sensorOn = None

    def __init__(self, periph):
        SensorBase.__init__(self, periph)

    def enable(self):
        SensorBase.enable(self)
        self.ctrl.write( struct.pack("B", 0x01), True )

    def read(self):
	'''Returns (ambient_temp, pressure_mullibars)'''
	(x,y,z) = struct.unpack('<hhh', self.data.read())
        tempP = ((x << 16)+y)
 	tempT = z
	return (tempP/64 , tempT/256)  
       
class DiodeledSensor(SensorBase):
    svcUUID  = _TI_UUID(0xAA64)
    dataUUID = _TI_UUID(0xAA65)
    ctrlUUID = _TI_UUID(0xAA66)
    sensorOn = None

    def __init__(self, periph):
        SensorBase.__init__(self, periph)

    def enable(self,val):
        SensorBase.enable(self)
        if(val==1):         
         self.ctrl.write( struct.pack("B", 0x01), True )
         print("RED led ON")
	if(val==2):
	 self.ctrl.write( struct.pack("B", 0x02), True ) 
         print("Green led ON")
	if(val==3):
	 self.ctrl.write( struct.pack("B", 0x03), True ) 
         print("Yellow led ON")
 	if(val==4):
         self.ctrl.write( struct.pack("B", 0x04), True )
         print("Blue led ON")
	if(val==5):
         self.ctrl.write( struct.pack("B", 0x05), True )
         print("Magenta led ON")
        if(val==6):
         self.ctrl.write( struct.pack("B", 0x06), True )
         print("Cyan led ON")
        if(val==7):
         self.ctrl.write( struct.pack("B", 0x07), True )
         print("White led ON")

class ColorSensor(SensorBase):
    svcUUID  = _TI_UUID(0XAA90)
    dataUUID = _TI_UUID(0XAA91)
    ctrlUUID = _TI_UUID(0XAA92)
    calUUID  = _TI_UUID(0XAA93)
    sensorOn = None

    def __init__(self, periph):
        SensorBase.__init__(self, periph)

    def enable(self):
        SensorBase.enable(self)
        self.ctrl.write( struct.pack("B", 0x01), True )
 
    def read(self):
        (w,r,g,b) = struct.unpack('<HHHH', self.data.read())
        return (w , r , g , b)

class KeypressSensor(SensorBase):
    svcUUID = UUID(0xFFE0)
    dataUUID = UUID(0xFFE1)

    def __init__(self, periph):
        SensorBase.__init__(self, periph)
 
    def enable(self):
        self.periph.writeCharacteristic(0x5d, struct.pack('<bb', 0x01, 0x00))

    def disable(self):
        self.periph.writeCharacteristic(0x5d, struct.pack('<bb', 0x00, 0x00))

class SensorTag(Peripheral):
    def __init__(self,addr):
        Peripheral.__init__(self,addr)
        #r ne 344, in getServiceByUUID
    	self.discoverServices()
        self.IRtemperature = IRTemperatureSensor(self)
        self.accelerometer = AccelerometerSensor(self)
        self.humidity = HumiditySensor(self)
        self.magnetometer = MagnetometerSensor(self)
        self.barometer = BarometerSensor(self)
 	self.diodeled = DiodeledSensor(self)
        self.color = ColorSensor(self)
        self.keypress = KeypressSensor(self)


class KeypressDelegate(DefaultDelegate):
    BUTTON_L = 0x02
    BUTTON_R = 0x01
    ALL_BUTTONS = (BUTTON_L | BUTTON_R)

    _button_desc = { 
        BUTTON_L : " button",
        BUTTON_R : "Key press",
        ALL_BUTTONS : "Both buttons"
    } 

    def __init__(self):
        DefaultDelegate.__init__(self)
        self.lastVal = 0

    def handleNotification(self, hnd, data):
	# NB: only one source of notifications at present
        # so we can ignore 'hnd'.
        val = struct.unpack("B", data)[0]
        down = (val & ~self.lastVal) & self.ALL_BUTTONS
        if down != 0:
            self.onButtonDown(down)
        up = (~val & self.lastVal) & self.ALL_BUTTONS
        if up != 0:
            self.onButtonUp(up)
        self.lastVal = val

    def onButtonUp(self, but):
        print ( "** " + self._button_desc[but] + " UP")

    def onButtonDown(self, but):
        print ( "** " + self._button_desc[but] + " DOWN")

if __name__ == "__main__":
    import time
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('host', action='store',help='MAC of BT device')
    parser.add_argument('-n', action='store', dest='count', default=0,
            type=int, help="Number of times to loop data")
    parser.add_argument('-t',action='store',type=float, default=3.0, help='time between polling')
    parser.add_argument('-T','--temperature', action="store_true",default=False)
    parser.add_argument('-A','--accelerometer', action='store_true',
            default=False)
    parser.add_argument('-H','--humidity', action='store_true', default=False)
    parser.add_argument('-O','--magnetometer', action='store_true',
            default=False)
    parser.add_argument('-P','--barometer', action='store_true', default=False)
    parser.add_argument('-R','--REDled', action='store_true', default=False)
    parser.add_argument('-G','--GREENled', action='store_true', default=False)
    parser.add_argument('-Y','--YELLOWled', action='store_true', default=False)
    parser.add_argument('-B','--BLUEled', action='store_true', default=False)
    parser.add_argument('-M','--MAGENTAled', action='store_true', default=False)
    parser.add_argument('-C','--CYANled', action='store_true', default=False)
    parser.add_argument('-W','--WHITEled', action='store_true', default=False)
    parser.add_argument('-L','--color', action='store_true', default=False)
    parser.add_argument('-K','--keypress', action='store_true', default=False)
    parser.add_argument('--all', action='store_true', default=False)

    arg = parser.parse_args(sys.argv[1:])

    print('Connecting to ' + arg.host)
    tag = SensorTag(arg.host)

    # Enabling selected sensors
    if arg.temperature or arg.all:
        tag.IRtemperature.enable()
    if arg.humidity or arg.all:
        tag.humidity.enable()
    if arg.barometer or arg.all:
        tag.barometer.enable()
    if arg.accelerometer or arg.all:
        tag.accelerometer.enable()
    if arg.magnetometer or arg.all:
        tag.magnetometer.enable()
    if arg.REDled or arg.all:
        tag.diodeled.enable(1)
    if arg.GREENled or arg.all:
        tag.diodeled.enable(2)
    if arg.YELLOWled or arg.all:
	tag.diodeled.enable(3)
    if arg.BLUEled or arg.all:
        tag.diodeled.enable(4)
    if arg.MAGENTAled or arg.all:
        tag.diodeled.enable(5)
    if arg.CYANled or arg.all:
        tag.diodeled.enable(6)
    if arg.WHITEled or arg.all:
        tag.diodeled.enable(7)
    if arg.color or arg.all:
        tag.color.enable()
    if arg.keypress or arg.all:
	tag.keypress.enable()
        tag.setDelegate(KeypressDelegate())

    # Some sensors (e.g., temperature, accelerometer) need some time for initialization.
    # Not waiting here after enabling a sensor, the first read value might be empty or incorrect.
    time.sleep(1.0)

    counter=1
    while True:
       if arg.temperature or arg.all:
           print('Temp: ', tag.IRtemperature.read())
	   f = open('TEMP','w')
	   f.write(str(tag.IRtemperature.read()))
	   f.close()
       if arg.humidity or arg.all:
           print("Humidity: ", tag.humidity.read())
           f = open('HUMI','w')
	   f.write(str(tag.humidity.read()))
	   f.close()
       if arg.barometer or arg.all:
           print("Barometer: ", tag.barometer.read())
           f = open('PRES','w')
	   f.write(str(tag.barometer.read()))
	   f.close()           
       if arg.accelerometer or arg.all:
           print("Accelerometer: ", tag.accelerometer.read())
       if arg.magnetometer or arg.all:
           print("Magnetometer: ", tag.magnetometer.read())
       if arg.color or arg.all:
           print("color: ",tag.color.read())
       if counter >= arg.count and arg.count != 0:
           break
       counter += 1
       tag.waitForNotifications(arg.t)

    tag.disconnect()
    del tag
