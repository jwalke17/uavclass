#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

file = open("coordinates.txt", "r")
dump = file.readlines()
file.close()
for line in dump:
    print line
    lat = re.match(r'.*lat=(.*),lon.*', line)
    lon = re.match(r".*lon=(.*),.*", line)
    print "lat ", lat.group(1)
    print "lon ", lon.group(1)


