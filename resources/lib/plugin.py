import codecs

from .matthuisman import plugin, settings, inputstream
from .matthuisman.session import Session

from .constants import M3U8_URL, REGIONS, EPG_URL
from .language import _

@plugin.route('')
def home(**kwargs):
    region  = get_region()
    channels = get_channels(region)

    folder = plugin.Folder(_(_.REGIONS[region]), cacheToDisc=False)

    for slug in sorted(channels, key=lambda k: (channels[k].get('network', ''), channels[k].get('name', ''))):
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
        path     = channel['mjh_master'],
        headers  = channel['headers'],
        info     = {'plot': channel.get('description')},
        video    = channel.get('video', {}),
        audio    = channel.get('audio', {}),
        art      = {'thumb': channel.get('logo')},
    )

    if channel.get('hls', False):
        item.inputstream = inputstream.HLS()

    return item

def get_channels(region):
    return Session().get(M3U8_URL.format(region=region)).json()

def get_region():
    return REGIONS[settings.getInt('region_index')]

@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    region   = get_region()
    channels = get_channels(region)

    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U\n')

        for slug in sorted(channels, key=lambda k: (channels[k].get('network', ''), channels[k].get('name', ''))):
            channel = channels[slug]

            f.write(u'#EXTINF:-1 tvg-id="{id}" tvg-chno="{chno}" tvg-logo="{logo}",{name}\n{path}\n'.format(
                id=slug, logo=channel.get('logo', ''), name=channel['name'], chno=channel.get('channel', ''), 
                    path=plugin.url_for(play, slug=slug, _is_live=True)))

@plugin.route()
@plugin.merge()
def epg(output, **kwargs):
    Session().chunked_dl(EPG_URL.format(region=get_region()), output)