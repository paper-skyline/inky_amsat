# inky_amsat
![inky amsat visual](https://nanoloop.io/inky_amsat.jpg "Inky Amsat")

## Simple Satellite Next Pass Information
First attempt at writing a tiny satellite pass program to fetch telemetry data via a [public API](http://satellites.calum.org/) and pass formatted text to a [Pimoroni Inky PHAT](https://shop.pimoroni.com/products/inky-phat) on a [Raspberry Pi](https://raspberrypi.org)

## Installation
After cloning the github repository, move to the directory in a terminal and run: `pipenv install`

If you don't have *pipenv* installed, from your terminal run: `pip install pipenv`

## Usage
`python3 inky_amsat.py`

_Don't forget to change your Latitude, Longitude, and Altitude to match your location_

When prompted, type in the 5-digit NORAD ID of the satellite that you want to pull telemetry data for (i.e. 40967 for AO-85 or 25545 for the ISS)

## Author
* Ben Cook on [Twitter](https://twitter.com/bpcook)

## Notes
* Without a Raspberry Pi and a Pimoroni InkyPHAT, this won't run
* I built this on Python3 but it may also run on Python2
* At the request of the API owner, I have utilized caching for the web calls. Please don't modify that to something less than a minute.

### Future Expansion Ideas
* Option to attempt to automatically pull gps data for location if one is available on the system
* Possibly a second program to evaluate a list of satellites and tell you the best choice based off pass length or max elevation