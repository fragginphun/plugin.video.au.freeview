import os
import json
import io
import uuid
from time import time

from . import config

class Settings(object):
    def __init__(self):
        try:
            with io.open(config.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                self._settings = json.loads(f.read())
            self._remove_legacy()
        except:
            self._settings = {}

    def _remove_legacy(self):
        self._settings.pop('token', None)
        self._settings.pop('isLoggedIn', None)
        self._settings.pop('alerts', None)

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def clear(self):
        self._settings = {}

    def set(self, key, value):
        self._settings[key] = value

    def save(self):
        with io.open(config.SETTINGS_FILE, 'w', encoding='utf8') as f:
            f.write(unicode(json.dumps(self._settings, separators=(',',':'), ensure_ascii=False)))

class Cache(object):
    def __init__(self, settings):
        self._settings = settings
        self._cache = self._settings.get('cache', {})
        self._settings.set('cache', self._cache)

        _time = time()
        for key in self._cache.keys():
            if self._cache[key]['expires'] and self._cache[key]['expires'] < _time:
                self.rm(key)

    def rm(self, key):
        cached = self._cache.pop(key, None)
        try: os.remove(cached['path'])
        except: pass

    def get(self, key, default=None):
        try:
            cached = self._cache.get(key)
            if not cached:
                return default

            if cached.get('path'):
                with io.open(cached['path'], 'r', encoding='utf-8') as f:
                    return json.loads(f.read())
            else:
                return cached['value']
        except:
            self.rm(key)
            return default

    def set(self, key, value, expiry=None, use_file=None):
        try:
            if use_file == None: use_file = len(json.dumps(value)) > 200

            expires = int(time() + expiry) if expiry else None
            if not use_file:
                self._cache[key] = {'value': value, 'expires': expires}
                return

            file_path = os.path.join(config.DATA_DIR, "{0}.cache".format(uuid.uuid4()))
            with io.open(file_path, 'w', encoding='utf8') as f:
                f.write(unicode(json.dumps(value, ensure_ascii=False)))

            self._cache[key] = {'path': file_path, 'expires': expires}
        except:
            pass

    def clear(self):
        self._cache = {}

        for file in os.listdir(config.DATA_DIR):
            if file.endswith('.cache'):
                try: os.remove(os.path.join(config.DATA_DIR, file))
                except: pass