import os, requests, hashlib

from . import config
from .exceptions import ComsError, LoginError, GeoError

class API(object):
    def __init__(self, settings, cache):
        self.settings = settings
        self.cache = cache
        self.session = requests.Session()

    def make_request(self, _type, url, cache=False, cache_time=config.CACHE_TIME, cache_use_file=None, **kwargs):
        if not url.startswith('http'):
            url = config.API_BASE_URL + url

        data = None
        if cache:
            cache_key = hashlib.md5("{0}{1}{2}".format(_type, url, kwargs)).hexdigest()
            data = self.cache.get(cache_key)
            if data: 
                if config.DEBUG: print("[CACHE HIT]")
                return data

        if config.DEBUG:
            print(_type + ' ' + url)
            if kwargs: print(kwargs)

        try:
            resp = self.session.request(_type, url, **kwargs)
            if config.DEBUG:
                print(resp.status_code)
            data = resp.json()
            if not data:
                raise
        except:
            raise ComsError('Request for data failed.'.format(url))

        if type(data) == dict and data.get('code','') == 'failedgeo':
            raise GeoError()

        if config.DEBUG:
            print(resp.headers)
            string = resp.text
            max_len = 200
            length = len(resp.text)
            if length > max_len:
                string = '{0}....{1}'.format(string[0:max_len], length)

            with open(os.path.join(config.DATA_DIR, 'out.json'), 'w') as f:
                f.write(resp.text.encode('utf-8'))

            print(string)

        if cache:
            self.cache.set(cache_key, data, cache_time, cache_use_file)

        return data

    def close(self):
        return