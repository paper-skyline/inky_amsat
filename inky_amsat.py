#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys

try:
    from inky import InkyPHAT
except ImportError:
    print(
        "InkyPHAT dependency not met.\n" +
        "Please install with sudo pip install einky")
    sys.exit(1)
else:
    inky_display = InkyPHAT("red")
    inky_display.set_border(inky_display.WHITE)

try:
    import requests
except ImportError:
    print(
        "Requests dependency not met.\n" +
        "Please install with sudo pip install requests")
    sys.exit(1)
else:
    try:
        import requests_cache
        requests_cache.install_cache('cache_api', expire_after=60)
    except ImportError:
        print("Requests-Cache dependency not met. Not caching API calls.")

import maya
from PIL import Image, ImageFont, ImageDraw

"""
Set latitude and longtitude based on your location
Future: try to import based off GPS if exists, else prompt, else default to
Houston, TX USA
"""

lat = "29.27371"
lon = "-95.35739"
alt = "0"

# Prompt the user for input, have a selection menu, take input as function
while True:
    try:
        norad = input("Please enter a 5-digit NORAD ID: ")
    except ValueError:
        print("That's not a valid entry. Please try again.")
        continue
    if 1 > len(norad) or len(norad) > 99999:
        print("That's not a valid NORAD ID. Please try again.")
        continue
    else:
        break

# Call to public API at satellite.calum.org
try:
    s_url = (
        "http://api.satellites.calum.org/rest/v1/" +
        norad + "/next-pass?lat=" + lat +
        "&lon=" + lon + "&alt=" + alt
    )
    response = requests.get(s_url)
    data = response.json()
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    print("API Unreachable")
    requests_cache.uninstall_cache('cache_api')
    sys.exit(1)

"""
Parse API response and calculate time from ISO8601 to US/Central
Future: Prompt user to specify or choose a timezone
"""

start_local = maya.parse(data['start']).datetime(to_timezone='US/Central')
start_time = start_local.strftime("%H:%M:%S")
peak_local = maya.parse(data['tca']).datetime(to_timezone='US/Central')
peak_time = peak_local.strftime('%H:%M:%S')
los_local = maya.parse(data['end']).datetime(to_timezone='US/Central')
los_time = los_local.strftime('%H:%M:%S')
pass_time = los_local - start_local

# Initial InkyPHAT display positioning
inky_top = 0
inky_left = 0
inky_left_offset = 0

img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

# Lines of data to display
l1 = data['name']
l2 = 'AOS:  ' + start_time + ' @ ' + str(data['aosazimuth']) + chr(176)
l3 = 'Peak: ' + peak_time + ' @ ' + str(data['maxel']) + chr(176) + 'E'
l4 = 'LOS:  ' + los_time + ' @ ' + str(data['losazimuth']) + chr(176)
l5 = 'Pass: ' + str(pass_time)

# Adjust font size down to either fit the display or print error
for item in (l1, l2, l3, l4, l5):
    f_size = 20
    font = ImageFont.truetype('./fonts/SourceCodePro-Semibold.ttf', f_size)
    width, height = font.getsize(item)
    # print("line " + item + ": ", width, height)
    while width > InkyPHAT.WIDTH:
        # print(item + ' current width is:', width)
        f_size -= 2
        font = ImageFont.truetype('./fonts/SourceCodePro-Semibold.ttf', f_size)
        width, height = font.getsize(item)
        if f_size == 0:
            print('line too long')
            break
        else:
            continue
    draw.text((0, inky_top), item, inky_display.BLACK, font)
    inky_top += height + 1
    inky_left = max(inky_left, inky_left_offset + width)

inky_display.set_image(img)
inky_display.show()
