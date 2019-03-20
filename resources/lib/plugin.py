from matthuisman import plugin, settings, inputstream
from matthuisman.session import Session

from .constants import M3U8_URL, REGIONS
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

    item = plugin.Item(
        path = channel['mjh_master'],
        headers = channel['headers'],
        art = False,
    )
    
    if settings.getBool('use_substreams', True):
        item.path = channel['mjh_sub']
    elif settings.getBool('use_ia_hls', False) and channel.get('hls', False):
        item.inputstream = inputstream.HLS()

    return item

def get_channels(region):
    return Session().get(M3U8_URL.format(region)).json()