from matthuisman import plugin, settings, inputstream
from matthuisman.session import Session

from .constants import M3U8_URL, REGIONS, PLAYLIST_URL, EPG_URL
from .language import _

@plugin.route('')
def home(**kwargs):
    region  = get_region()
    channels = get_channels(region)

    folder = plugin.Folder(title=_(_.REGIONS[region]))

    for slug in sorted(channels, key=lambda k: channels[k].get('channel', channels[k]['name'])):
        channel = channels[slug]

        folder.add_item(
            label = channel['name'],
            path  = plugin.url_for(play, slug=slug, _is_live=True),
            info  = {'plot': channel.get('description')},
            video = channel.get('video', {}),
            audio = channel.get('audio', {}),
            art   = {'thumb': channel.get('logo')},
            playable = True,
        )

    folder.add_item(label=_.SETTINGS,  path=plugin.url_for(plugin.ROUTE_SETTINGS))

    return folder

@plugin.route()
def play(slug, **kwargs):
    region  = get_region()
    channel = get_channels(region)[slug]

    item = plugin.Item(
        path = channel['mjh_master'],
        headers = channel['headers'],
        art = False,
    )
    
    if settings.getBool('use_substreams', True):
        item.path = channel['mjh_sub']
    elif channel.get('hls', False) and settings.getBool('use_ia_hls', False):
        item.inputstream = inputstream.HLS()

    return item

def get_channels(region):
    return Session().get(M3U8_URL.format(region=region)).json()

def get_region():
    return REGIONS[settings.getInt('region_index')]

@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    Session().chunked_dl(PLAYLIST_URL.format(region=get_region()), output)

@plugin.route()
@plugin.merge()
def epg(output, **kwargs):
    Session().chunked_dl(EPG_URL.format(region=get_region()), output)