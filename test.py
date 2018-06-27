#!/usr/bin/env python2.7
import os
import sys

sys.path.append(os.path.realpath('../script.module.matthuisman/lib'))

import resources.lib.config
from resources.lib.controller import Controller

SEPERATOR = "*"*50
ROUTES = [
    #'',
    '?_route=home',
]

print(SEPERATOR)
if len(sys.argv) > 1:
    print("TEST: '{0}'\n".format(sys.argv[1]))
    Controller().route(sys.argv[1])
    print(SEPERATOR)
    sys.exit()

for route in ROUTES:
    print("TEST: '{0}'\n".format(route))
    Controller().route(route)
    print(SEPERATOR)