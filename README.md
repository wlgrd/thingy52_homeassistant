# Thingy:52 Sensor for Home Assistant

1. Install [bluepy](https://github.com/IanHarvey/bluepy)

        $ sudo apt-get install libglib2.0-dev
        $ sudo pip install bluepy

2. Find the mac address for the thingy

        hcitool lescan

3. Setup up the sensor like this in `configuration.yaml`, and replace the mac-address with what lescan gave you (lower case):

        sensor:
          - platform: thingy52
            scan_interval: 60
            # 1 = 1 s interval
            # 2 = 10 s interval
            # 3 = 60 s interval
            gas_interval: 3
            mac: "d0:c0:1d:b9:45:e1"
            sensors:
              temperature:
              humidity:
              co2:
              tvoc:
              pressure:
              battery:

Clone or download this folder into your configurations directory, so that you have `<configfolder>/custom_components/sensor/thingy52.py`

## Known issues
* Will not handle automatic reconnections
* Untested with several units

Pull requests are very welcome!