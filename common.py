#!/usr/bin/env python
import requests
import sys

def maxspeedAll(points):
    overpassUrl = 'http://overpass-api.de/api/interpreter?data=%s'
    overpassQl = '[out:json];'

    for i in range(0, len(points)-2, 2):
        lat1, lon1 = points[i:i + 2]
        lat2, lon2 = points[i + 2:i + 4]
        s = min(lat1, lat2)
        w = min(lon1, lon2)
        n = max(lat1, lat2)
        e = max(lon1, lon2)
        overpassQl += 'way(%f,%f,%f,%f)["maxspeed"]["highway"];' % (s, w, n, e)

    overpassQl += "out;"
    #print(overpassQl)

def maxspeed(lon1, lat1, lon2, lat2):
    s = min(lat1, lat2)
    w = min(lon1, lon2)
    n = max(lat1, lat2)
    e = max(lon1, lon2)
    overpassUrl = 'http://overpass-api.de/api/interpreter?data=%s'
    overpassQl = '[out:json];way(%f,%f,%f,%f)["maxspeed"]["highway"];out;' % (s, w, n, e)
    #print(overpassQl)
    r = requests.get(overpassUrl % overpassQl)

    if r.status_code != 200:
        return -1  # We don't know a limit

    resp = r.json()

    if len(resp['elements']) < 1:
        return -1

    speed = resp['elements'][0]['tags']['maxspeed'];

    try:
        if ' ' in speed:
            val, unit = speed.split(' ')
            limit = float(val)

            if unit == 'mph':
                limit *= 1.609
        else:
            limit = float(speed)
    except ValueError:
        # No numeric value, check some possible values
        if speed == 'none' or speed == 'signals': # TODO: Think about signals
            limit = 0  # There is no limit
        elif speed == 'walk':
            limit = 6
        else:
            print('Unhandled speed limit (%s,%s,%s,%s): %s' % (s, w, n, e, speed))
            limit = -1

    return limit

if __name__ == "__main__":
    sys.exit()
