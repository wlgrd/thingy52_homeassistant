# Thingy:52 Sensor for Home Assistant

This sensor lets you connect several [Nordic Thingy:52's](https://www.nordicsemi.com/eng/Products/Nordic-Thingy-52) to your Home Assistant installation. How many you connect is dependent on the Bluetooth hardware you are using. 

Your hardware needs to support Bluetooth 4.0 or higher.

## Usage

1. Install [bluepy](https://github.com/IanHarvey/bluepy)

        $ sudo apt-get install libglib2.0-dev
        $ sudo pip install bluepy

2. Find the mac address for the thingy

        hcitool lescan

3. Setup up the sensor in `configuration.yaml`, and replace the mac-address with what `lescan` gave you in this format `##:##:##:##:##:##`

### Configuration Variables
| Name | Type | Default | Since | Options | Description |
|------|------|---------|-------|---------|-------------|
| mac | string | **required** | v0.0.0 | N/A | MAC address of the Thingy52 to be connected.
| sensors | list | **required** | v0.0.2 | `temperature`, `humidity`, `co2`, `tvoc`, `pressure`, `battery` | Sensors to be monitored.
| friendly_name | string | `Thingy:` | v0.0.0 | N/A | Set a custom name.
| refresh_interval | time | 60 seconds | v0.0.2 | N/A | Time between refreshing the data set.
| gas_interval | number | `3` | v0.0.0 | `1` for 1s, `2` for 10s, `3` for 60s | The polling interval between reading gas sensors.

## Example Config
```
# First thingy
- platform: thingy52
  friendly_name: Kitchen
  refresh_interval: 
    seconds: 60
  gas_interval: 3
  mac: "f6:7d:66:5f:b9:e4"
  sensors:
    - temperature
    - humidity
    - co2
    - tvoc
    - pressure
    - battery
# Second thingy
- platform: thingy52
  friendly_name: Bathroom
  refresh_interval: 
    minutes: 1
  gas_interval: 2
  mac: "fe:42:28:a3:4f:d5"
  sensors:
    - temperature
    - humidity
    - pressure
    - battery
```

Clone or download this folder into your configurations directory, so that you have `<configfolder>/custom_components/sensor/thingy52.py`

Tips: When testing things, you might want to lower the `refresh_interval` and `gas_interval` so you get data more often.
The default 60 seconds is to preserve power. To saven even more power, connect to the Thingy:52 from the Thingy-app 
[google play](https://play.google.com/store/apps/details?id=no.nordicsemi.android.nrfthingy) and decrease the connection interval. 
Will try and support this from this sensor in the future.

## Coverage

The sensor has only been testet on a [OSMC](https://osmc.tv/) image for the Raspberry Pi 2, using Home Assistant 0.57dev.\
This sensor also works with Hass.io installed as Hass.OS on a Raspberry Pi 3B+, using Home Assistant 0.99.3

## Known issues
* Will not handle automatic reconnections

### Pull requests are very welcome!
