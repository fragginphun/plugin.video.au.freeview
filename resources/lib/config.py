import os, sys

try:
  import xbmc, xbmcaddon
  KODI = True
except:
  KODI = False

ADDON = None
ADDON_NAME = ""
ADDON_PATH = '.'
ADDON_HANDLE = 1
BASE_URL = ''
DATA_DIR = './tmp'
REGION = 'Sydney'
DEBUG = True

if KODI:
  ADDON = xbmcaddon.Addon()
  ADDON_NAME = ADDON.getAddonInfo('name')
  ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('path')).decode("utf-8")
  ADDON_HANDLE = int(sys.argv[1])
  BASE_URL = sys.argv[0]
  DATA_DIR = xbmc.translatePath(ADDON.getAddonInfo('profile'))
  REGION = ADDON.getSetting('region').strip()
  DEBUG = ADDON.getAddonInfo('version').lower().endswith('x')

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
M3U8_FILE = 'http://iptv.matthuisman.nz/au/{0}/tv.json'.format(REGION)
CACHE_TIME = (60*60*24) #24 hours