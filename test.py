#!/usr/bin/env python2.7
import os
import sys
sys.path.append(os.path.realpath('../script.module.matthuisman/lib'))

from matthuisman.test import run_test
from resources.lib.controller import Controller

ROUTES = [
    '',
    '?_route=home',
    '?_route=home&play=tv.redbull.tv&_l=.pvr',
    '?_route=toggle_ia&slug=tv.redbull.tv',
    '?_route=home&play=tv.redbull.tv&_l=.pvr',
   # '?_route=clear',
]

run_test(Controller, ROUTES)