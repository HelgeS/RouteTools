#!/usr/bin/env python
import math
import srtm
import gpxpy
import requests
import sys

if len(sys.argv) < 2:
    print("Provide a .gpx file to convert")
    exit(1)

gpx = gpxpy.parse(open(sys.argv[1]))
elevation_data = srtm.get_data()
elevation_data.add_elevations(gpx) #, smooth=True)
lastPoint = gpx.tracks[0].segments[0].points[0]
distance = 0

with open(sys.argv[1][:-4] + '.csv', 'w') as f:
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                distance += math.sqrt(math.pow(point.latitude-lastPoint.latitude, 2)+math.pow(point.longitude-lastPoint.longitude, 2))
                lastPoint = point
                f.write("%d;%f\n" % (distance*100000, point.elevation))

