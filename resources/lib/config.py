from matthuisman import globs as g
from matthuisman.config import Config as BaseConfig

class Config(BaseConfig):
    def __init__(self, addon_id=''):
        super(Config, self).__init__(addon_id)

        if self.KODI:
            self.REGION = self.ADDON.getSetting('region').strip()
        else:
            self.REGION = 'Sydney'

        self.M3U8_FILE = 'http://iptv.matthuisman.nz/au/{0}/tv.json'.format(self.REGION)

g.config = Config()