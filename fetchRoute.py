#!/usr/bin/env python
import xml.etree.ElementTree
import csv
import json
import sys
import requests
from math import radians, cos, sin, asin, sqrt

MAPQUEST_KEY = 'AD0IOzjhmAByUsyArJxvfjd2ne1KUs7y'


# TODO: Filter railways, select only actual roads (if possible)
# TODO: Fetch all way data at once or at least in chunks

def create_route(gpx_file):
    e = xml.etree.ElementTree.parse(gpx_file).getroot()
    points = [(float(pt.get('lat')), float(pt.get('lon'))) for pt in e.iter('{http://www.topografix.com/GPX/1/1}trkpt')]


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6.367 * c
    return km * 1000


def maxspeedAll(points):
    overpassUrl = 'http://overpass-api.de/api/interpreter?data=%s'
    overpassQl = '[out:json];'

    for i in range(0, len(points)/2-1):
        lat1, lon1 = points[2*i:2*i + 2]
        lat2, lon2 = points[2*i + 2:2*i + 4]
        s = min(lat1, lat2)
        w = min(lon1, lon2)
        n = max(lat1, lat2)
        e = max(lon1, lon2)
        overpassQl += 'way(%f,%f,%f,%f)["maxspeed"]["highway"];' % (s, w, n, e)

    overpassQl += "out;"
    print(overpassQl)

def maxspeed(lon1, lat1, lon2, lat2):
    s = min(lat1, lat2)
    w = min(lon1, lon2)
    n = max(lat1, lat2)
    e = max(lon1, lon2)
    overpassUrl = 'http://overpass-api.de/api/interpreter?data=%s'
    # overpassQl = '[out:json];way(51.648197,8.328058,51.6486399,8.3287396)["maxspeed"];out;' % (e, n, s, w)
    overpassQl = '[out:json];way(%f,%f,%f,%f)["maxspeed"]["highway"];out;' % (s, w, n, e)
    print(overpassQl)
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
    locationFrom = sys.argv[1]
    locationTo = sys.argv[2]
    dirUrl = 'http://open.mapquestapi.com/directions/v2/route?key=%s&unit=k&from=%s&to=%s' % (
    MAPQUEST_KEY, locationFrom, locationTo)
    r = requests.get(dirUrl)

    if r.status_code != 200:
        print("Fehler bei Routenermittlung")
        print(r.text)
        sys.exit(1)

    route = r.json()['route']
    print('Start: %s, %s' % (route['locations'][0]['street'], route['locations'][0]['adminArea5']))
    print('End: %s, %s' % (route['locations'][-1]['street'], route['locations'][-1]['adminArea5']))
    print('Distance: ' + str(route['distance']) + "km")
    print('Session-ID: ' + route['sessionId'])

    elUrl = 'http://open.mapquestapi.com/elevation/v1/profile?key=%s&inFormat=kvp&outFormat=json&sessionId=%s&unit=k&shapeFormat=raw' % (
    MAPQUEST_KEY, route['sessionId'])
    r2 = requests.get(elUrl)

    if r2.status_code != 200:
        print("Fehler bei Hoehenermittlung")
        print(r2.text)
        sys.exit(1)

    routeName = '' # TODO: Generate from start and end
    json.dump(r.json(), open('%s_route.json' % routeName, 'w'))
    json.dump(r2.json(), open('%s_elevation.json' % routeName, 'w'))
    elResp = r2.json()

    distances = []
    height = []
    speedlimits = []

    maxspeedAll(elResp['shapePoints'])

    for i in range(0, len(elResp['elevationProfile']) - 1):
        p = elResp['elevationProfile'][i]
        distances.append(round(p['distance'] * 1000))
        height.append(p['height'])
        lat1, lon1 = elResp['shapePoints'][2*i:2*i + 2]
        lat2, lon2 = elResp['shapePoints'][2*i + 2:2*i + 4]
        curSpeed = maxspeed(lon1, lat1, lon2, lat2)

        if curSpeed >= 0:
            speedlimits.append(curSpeed)
        elif i >= 1:
            print('No maxspeed information')
            speedlimits.append(speedlimits[i - 1])
        else:
            print('No maxspeed information')
            speedlimits.append(0)

    with open('route.csv', 'w') as f:
        writer = csv.writer(f, delimiter=';')

        for i in range(0, len(distances)):
            writer.writerow([distances[i], height[i], speedlimits[i]])
