#!/usr/bin/env python
import math
import srtm
import gpxpy
import requests
import sys
from common import maxspeed

if len(sys.argv) < 2:
    print("Provide a .gpx file to convert")
    exit(1)

gpx = gpxpy.parse(open(sys.argv[1]))
elevation_data = srtm.get_data()
elevation_data.add_elevations(gpx) #, smooth=True)
lastPoint = gpx.tracks[0].segments[0].points[0]
distance = 0
i = 0

with open(sys.argv[1][:-4] + '.csv', 'w') as f:
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                distance += math.sqrt(math.pow(point.latitude-lastPoint.latitude, 2)+math.pow(point.longitude-lastPoint.longitude, 2))
                speed = maxspeed(point.longitude, point.latitude, lastPoint.longitude, lastPoint.latitude)
                lastPoint = point

                f.write("%d;%f;%f\n" % (distance*100000, point.elevation, speed))
                progress = i/len(segment.points)
                print '\r[{0}] {1}%'.format('#'*(progress/10), progress),
                i += 1

