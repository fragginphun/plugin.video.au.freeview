import os
from urllib import urlencode

from . import config
from .view import View
from .models import Settings, Cache
from .exceptions import ViewError, LoginError, InputError, GeoError
from .api import API

class Controller(object):
    def __init__(self):
        self.view = View()
        self.settings = Settings()
        self.cache = Cache(self.settings)
        self.api = API(self.settings, self.cache)

        self.routes = {
            'home': self.home,
            'toggle_ia': self.toggle_ia,
            'clear': self.clear,
        }

    def do_route(self, params):
        default_route = 'home'

        self.route = params.pop('_route', default_route).lower()
        if self.route not in self.routes:
            self.view.dialog("Could not find that route.", "ERROR")
            route = default_route

        try:
            self.routes[self.route](params)
        except GeoError:
            self.view.dialog("GEO Restricted", "ERROR")
        except ViewError as e:
            self.view.dialog(e, "ERROR")
        except InputError:
            pass
        except Exception as e:
            if config.DEBUG: raise
            else: self.view.dialog(str(e), "ERROR")
        finally:
            self.close()

    def get_route(self, route, params=None, live=False):
        if route not in self.routes:
            raise Exception("Route not in routes")

        if not params: params = {}
        params['_route'] = route

        _params = []
        for k in sorted(params):
            try: _params.append((k, unicode(params[k]).encode('utf-8')))
            except: _params.append((k,params[k]))

        url = "{0}?{1}".format(config.BASE_URL, urlencode(_params))
        if live: url += "&_l=.pvr"

        return url

    def home(self, params):
        channels = self._get_channels()

        if params.get('play'):
            channel = channels[params['play']]
            channel['url'] = channel['play_url']
            return self.view.play(channel)
        
        slugs = sorted(channels, key=lambda k: channels[k].get('channel', channels[k]['title']))
        items = [channels[slug] for slug in slugs]

        self.view.items(items, cache=False)

    def toggle_ia(self, params):
        slug = params.get('slug')

        channels = self._get_channels()
        channel = channels[slug]

        ia_enabled = self.settings.get('ia_enabled', [])

        if slug in ia_enabled:
            ia_enabled.remove(slug)
            self.view.notification('Inputstream Disabled', heading=channel['title'], icon=channel['images']['thumb'])
        else:
            ia_enabled.append(slug)
            self.view.notification('Inputstream Enabled', heading=channel['title'], icon=channel['images']['thumb'])

        self.settings.set('ia_enabled', ia_enabled)
        self.view.refresh()

    def _get_channels(self):
        channels = {}
        
        data = self.api.make_request('GET', config.M3U8_FILE, cache=True, cache_use_file=False)
        ia_enabled = self.settings.get('ia_enabled', [])

        for slug in data:
            channel = data[slug]

            info = {
                'title': channel['name'],
                'plot': channel.get('description',''),
                'mediatype': 'video',
            }

            context = []
            use_ia = False

            if channel['url'].startswith('http'):
                use_ia = slug in ia_enabled

                if use_ia:
                    context.append(["Disable Inputstream", "XBMC.RunPlugin({0})".format(
                        self.get_route('toggle_ia', {'slug': slug}))])
                else:
                    context.append(["Enable Inputstream", "XBMC.RunPlugin({0})".format(
                        self.get_route('toggle_ia', {'slug': slug}))])

            item = {
                'title': channel['name'],
                'images': {'thumb': channel.get('logo', None)},
                'url': self.get_route('home', {'play': slug}, live=True),
                'play_url': channel['url'],
                'playable': True,
                'use_ia': use_ia,
                'info': info,
                'video': channel.get('video',{}),
                'audio': channel.get('audio',{}),
                'context': context,
            }

            if channel.get('channel'):
                item['channel'] = channel['channel']

            channels[slug] = item

        return channels

    def close(self):
        self.api.close()
        self.settings.save()

    def clear(self, params):
        self.cache.clear()
        self.settings.clear()
        self.close()
        self.view.notification('Data cleared')