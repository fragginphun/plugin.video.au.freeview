#!/usr/bin/env python2.7
import sys
from urlparse import parse_qsl
from resources.lib.controller import Controller

if __name__ == '__main__':
    params = dict(parse_qsl(sys.argv[2][1:]))
    controller = Controller()
    controller.do_route(params)