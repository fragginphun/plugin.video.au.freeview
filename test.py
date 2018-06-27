#!/usr/bin/env python2.7
import os, time

test_routes = [
  '',
  '?_route=toggle_ia&slug=tv.101002210220',
  '?_route=home&play=tv.101002210220&_l=.pvr',
  '?_route=clear',
  '?_route=home&play=tv.101002210220&_l=.pvr',
]

if __name__ == '__main__':
    try:
      for route in test_routes:
          print("Testing route: {0}\n".format(route))
          os.system('default.py "" "{0}"'.format(route))
          print("*"*100)
    except:
        pass