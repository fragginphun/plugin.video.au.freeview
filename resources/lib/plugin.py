from matthuisman import plugin, cache, settings, inputstream
from matthuisman.session import Session

from .constants import M3U8_URL, REGIONS, CACHE_TIME
from .language import _

@plugin.route('')
def home():
    region  = REGIONS[settings.getInt('region_index')]
    channels = get_channels(region)

    folder = plugin.Folder(title=_(_.REGIONS[region]))

    for slug in sorted(channels, key=lambda k: channels[k].get('channel', channels[k]['name'])):
        channel = channels[slug]

        folder.add_item(
            label = channel['name'],
            path  = plugin.url_for(play, slug=slug, is_live=True),
            info  = {'plot': channel.get('description')},
            video = channel.get('video', {}),
            audio = channel.get('audio', {}),
            art   = {'thumb': channel.get('logo')},
            playable = True,
        )

    folder.add_item(label=_.SETTINGS,  path=plugin.url_for(plugin.ROUTE_SETTINGS))

    return folder

@plugin.route()
def play(slug):
    region  = REGIONS[settings.getInt('region_index')]
    channel = get_channels(region)[slug]

    path = channel['mjh_master']
    hls = settings.getBool('use_ia_hls', False) and channel.get('hls', False)
    if not hls and settings.getBool('use_substreams', True):
        path = channel['mjh_sub']
    
    return plugin.Item(
        path = path,
        headers = channel['headers'],
        art = False,
        inputstream = inputstream.HLS() if hls else None,
    )

@cache.cached(expires=CACHE_TIME)
def get_channels(region):
    return Session().get(M3U8_URL.format(region)).json()