#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys

try:
    from inky import InkyPHAT
except ImportError:
    print(
        "InkyPHAT dependency not met.\n" +
        "Please install with pip install einky")
    sys.exit(1)
else:
    inky_display = InkyPHAT("black")
    inky_display.set_border(inky_display.WHITE)

try:
    import requests
except ImportError:
    print(
        "Requests dependency not met.\n" +
        "Please install with pip install requests")
    sys.exit(1)
else:
    try:
        import requests_cache
        requests_cache.install_cache('cache_api', expire_after=60)
    except ImportError:
        print("Requests-Cache dependency not met. Not caching API calls.")

import maya

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    print(
        "Python Imaging Library dependency not met.\n"
        "Please install with pip install pillow")
    sys.exit(1)

"""
Set latitude and longtitude based on your location
Future: try to import based off GPS if exists, else prompt, else default to
Houston, TX USA
"""

lat = "29.27371"
lon = "-95.35739"
alt = "0"

# Dictionaries of amateur radio FM and transponder satellites
fm_sat = {
    "SO-50": 27607,
    "AO-85": 40967,
    "AO-91": 43017,
    "AO-92": 43147,
    "Funcube": 999999,
    "LilacSat-2": 40908,
    "IO-86": 40931,
    "PO-101": 43678
}
tran_sat = {
    "AO-7": 7530,
    "FO-29": 24278,
    "AO-73": 39444,
    "XW-2A": 40903,
    "XW-2B": 40911,
    "XW-2C": 40906,
    "XW-2D": 40907,
    "XW-2F": 40910,
    "LO-87": 999999,
    "EO-88": 42017,
    "CAS-4A": 999999,
    "CAS-4B": 999999,
    "JO-97": 43803,
    "FO-99": 999999,
    "QO-100": 43700,
}

# NORAD manual entry function


def norad_input(prompt):
    while True:
        try:
            norad = input(prompt)
        except ValueError:
            print("That's not a valid entry. Please try again.")
            continue
        if 1 > len(norad) or len(norad) > 99999:
            print("That's not a valid NORAD ID. Please try again.")
            continue
        else:
            break
    return norad


# Satellite selection menu
action = input(
    "1\tSelect an FM satellite\n" +
    "2\tSelect a transpoder satellite\n" +
    "3\tManually enter a 5-digit NORAD ID\n" +
    "Enter your selection: \n")

if int(action) == 1:
    print("\nFM Satellites:")
    for sat in sorted(fm_sat):
        print("\t" + sat)
    print("\n")
    fm_sat_key = input("Enter your selection: \n")
    norad = fm_sat[fm_sat_key]
elif int(action) == 2:
    print("\nTransponder Satellites:")
    for sat in sorted(tran_sat):
        print("\t" + sat)
    print("\n")
    tran_sat_key = input("Enter your selection: \n")
    norad = tran_sat[tran_sat_key]
elif int(action) == 3:
    norad = norad_input("Please enter a 5-digit NORAD ID: ")
else:
    print("No valid action selected. Exiting.")
    sys.exit(1)

# Call to public API at satellite.calum.org
while True:
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
    if response.status_code == 404:
        print("NORAD ID doesn't exist.\n")
        norad = norad_input("Please enter a 5-digit NORAD ID: ")
        continue
    else:
        break

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
