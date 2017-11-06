"""
    HomeAssistant: Thingy52 temperature sensor
    Author: @chriswils

    This sensor device is taking data from the Nordic Thingy:52 IoT Sensor Platform.
    It is derived from HA example sensor; https://home-assistant.io/developers/platform_example_sensor/
    and uses bluepy's Thingy:52 implementation. More docs on this and snippets used in this file is 
    found at Nordic Semiconductor's devzone blog:
    https://devzone.nordicsemi.com/blogs/1162/nordic-thingy52-raspberry-pi-python-interface/
    
"""

from homeassistant.const import TEMP_CELSIUS, CONF_MAC, CONF_SCAN_INTERVAL, CONF_SENSORS
from homeassistant.helpers.entity import Entity
from bluepy import btle, thingy52
import binascii

# DEPENDENCIES = ['libglib2.0-dev']
# REQUIREMENTS = ['bluepy']

# Definition of all UUID used by Thingy
CCCD_UUID = 0x2902

CONF_GAS_INT = 'gas_interval'

SENSOR_UNITS = {
    "humidity": '%',
    "temperature" : TEMP_CELSIUS,
    "co2": 'ppm',
    "tvoc": 'ppb',
    "pressure": 'hPA',
    "battery": '%'
}


""" Custom delegate class to handle notifications from the Thingy:52 """
class NotificationDelegate(btle.DefaultDelegate):
    def __init__(self, sensors):
        self.thingysensors = {}
        for s in sensors:
            self.thingysensors[s._name] = s

    # print("# [THINGYSENSOR]: Delegate class called")
    def handleNotification(self, hnd, data):
        print("# [THINGYSENSOR]: Got notification")
        if (hnd == thingy52.e_temperature_handle):
            teptep = binascii.b2a_hex(data)
            tempinteg = self._str_to_int(teptep[:-2])
            tempdec = int(teptep[-2:], 16)

            div = 100 if((int(teptep[-2:], 16) / 10) > 1.0) else 10
            self.thingysensors["temperature"]._state = (tempinteg + (tempdec / div))   
        
        elif (hnd == thingy52.e_humidity_handle):
            teptep = binascii.b2a_hex(data)
            self.thingysensors["humidity"]._state = self._str_to_int(teptep)

        elif (hnd == thingy52.e_pressure_handle):
            pressure_int, pressure_dec = self._extract_pressure_data(data)
            div = 100 if( (pressure_dec / 10) > 1.0) else 10
            self.thingysensors["pressure"]._state = pressure_int + (pressure_dec/div)

        elif (hnd == thingy52.e_gas_handle):
            eco2, tvoc = self._extract_gas_data(data)
            if ("co2" in self.thingysensors):
                if(eco2 != 0):
                    self.thingysensors["co2"]._state = eco2
            if ("tvoc" in self.thingysensors):
                self.thingysensors["tvoc"]._state = tvoc

        
        elif (hnd == e_battery_handle):
            teptep = binascii.b2a_hex(data)
            self.thingysensors["battery"]._state = int(teptep, 16)
    
    def _extract_pressure_data(self, data):
        """ Extract pressure data from data string. """
        teptep = binascii.b2a_hex(data)
        pressure_int = 0
        for i in range(0, 4):
                pressure_int += (int(teptep[i*2:(i*2)+2], 16) << 8*i)
        pressure_dec = int(teptep[-2:], 16)
        return (pressure_int, pressure_dec)

    def _extract_gas_data(self, data):
        """ Extract gas data from data string. """
        teptep = binascii.b2a_hex(data)
        eco2 = int(teptep[:2], 16) + (int(teptep[2:4], 16) << 8)
        tvoc = int(teptep[4:6], 16) + (int(teptep[6:8], 16) << 8)
        return eco2, tvoc

    def _str_to_int(self, s):
        """ Transform hex str into int. """
        i = int(s, 16)
        if i >= 2**7:
            i -= 2**8
        return i 

def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Set up the Thingy 52 temperature sensor"""
    global e_battery_handle
    mac_address = config.get(CONF_MAC)
    conf_sensors = config.get(CONF_SENSORS)
    print(conf_sensors)
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    gas_interval = config.get(CONF_GAS_INT)
    print (scan_interval)
    print(type(scan_interval))
    scan_interval = scan_interval.total_seconds()
    print (scan_interval)
    notification_interval = int(scan_interval) * 1000
    sensors = []
    print("#[THINGYSENSOR]: Connecting to Thingy with address {}...".format(mac_address))
    thingy = thingy52.Thingy52(mac_address)


    print("#[THINGYSENSOR]: Configuring and enabling environment notifications...")
    thingy.environment.enable()

    # Enable notifications for enabled services
    # Update interval 1000ms = 1s
    if "temperature" in conf_sensors:
        print("Enabling notification for temperature")
        thingy.environment.set_temperature_notification(True)
        thingy.environment.configure(temp_int=notification_interval)
    if "humidity" in conf_sensors:
        print("Enabling notification for humidity")
        thingy.environment.set_humidity_notification(True)
        thingy.environment.configure(humid_int=notification_interval)
    if ( ("co2" in conf_sensors) or ("tvoc" in conf_sensors) ):
        thingy.environment.set_gas_notification(True)
        thingy.environment.configure(gas_mode_int=gas_interval)
    if "pressure" in conf_sensors:
        thingy.environment.set_pressure_notification(True)
        thingy.environment.configure(press_int=notification_interval)
    if "battery" in conf_sensors:
        thingy.battery.enable()
        # Battery notification not included in bluepy.thingy52
        e_battery_handle = thingy.battery.data.getHandle() # Is this needed?
        battery_ccd = thingy.battery.data.getDescriptors(forUUID=CCCD_UUID)[0]
        battery_ccd.write(b"\x01\x00", True)


    for sensorname in conf_sensors:
        print("Adding sensor: {}".format(sensorname))
        sensors.append(Thingy52Sensor(thingy, sensorname, SENSOR_UNITS[sensorname]))
    
    add_devices(sensors)
    thingy.setDelegate(NotificationDelegate(sensors))

class Thingy52Sensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, thingy, name, unit_measurement=TEMP_CELSIUS):
        """Initialize the sensor."""
        self._thingy = thingy
        self._name = name
        self._state = None
        self._unit_measurement = unit_measurement
        


    @property
    def name(self):
        """Return the name of the sensor."""
        return ("Thingy52: " + self._name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_measurement

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        # For some reason, without this, nothing gets updated and no 
        # notifications are read
        # if(self._name == "battery"):
        #         self._state = self._thingy.battery.read()

        # or we do it loke this, but then we wont get battery readings
        # all the time. Maybe that is for the best
        self._thingy.waitForNotifications(timeout=5)
        print("# [{}]: method update, state is {}".format(self._name, self._state))

if (__name__ == "__main__"):
    setup_platform()
