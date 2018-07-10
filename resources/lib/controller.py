import requests

from matthuisman.controller import Controller as BaseController

from . import config

class Controller(BaseController):
    def home(self, params):
        channels = self._get_channels()

        if params.get('play'):
            channel = channels[params['play']]
            channel['url'] = channel['_play_url']
            return self._view.play(channel)
        
        slugs = sorted(channels, key=lambda k: channels[k].get('channel', channels[k]['title']))
        items = [channels[slug] for slug in slugs]

        self._view.items(items, cache=False, title=self._addon['region'])

    def toggle_ia(self, params):
        slug = params.get('slug')

        channels = self._get_channels()
        channel = channels[slug]

        ia_enabled = self._addon.cache.get('ia_enabled', [])

        if slug in ia_enabled:
            ia_enabled.remove(slug)
            self._view.notification('Inputstream Disabled', heading=channel['title'], icon=channel['images']['thumb'])
        else:
            ia_enabled.append(slug)
            self._view.notification('Inputstream Enabled', heading=channel['title'], icon=channel['images']['thumb'])

        self._addon.cache['ia_enabled'] = ia_enabled
        self._view.refresh()

    def _get_channels(self):
        channels = {}

        url = config.M3U8_FILE.format(self._addon['region'])
        func = lambda: requests.get(url).json()
        data = self._addon.cache.function(url, func, expires=config.CACHE_TIME)

        ia_enabled = self._addon.cache.get('ia_enabled', [])

        for slug in data:
            channel = data[slug]

            info = {
                'title': channel['name'],
                'plot': channel.get('description',''),
                'mediatype': 'video',
            }

            context = []
            use_ia = False

            url = channel['mjh_sub']
            if url.startswith('http'):
                use_ia = slug in ia_enabled

                if use_ia:
                    url = channel['mjh_master']
                    context.append(["Disable Inputstream", "XBMC.RunPlugin({0})".format(
                        self._router.get(self.toggle_ia, {'slug': slug}))])
                else:
                    context.append(["Enable Inputstream", "XBMC.RunPlugin({0})".format(
                        self._router.get(self.toggle_ia, {'slug': slug}))])

            item = {
                'title': channel['name'],
                'images': {'thumb': channel.get('logo', None)},
                'url': self._router.get(self.home, {'play': slug}, live=True),
                '_play_url': url,
                'playable': True,
                'info': info,
                'video': channel.get('video',{}),
                'audio': channel.get('audio',{}),
                'context': context,
                'vid_type': 'hls',
                'options': {'use_ia': use_ia, 'get_location': use_ia, 'headers': channel.get('headers', {})},
            }

            if channel.get('channel'):
                item['channel'] = channel['channel']

            channels[slug] = item

        return channels