import os, requests

from . import config

class TextView(object):
    def reinstall(self):
        print("Reinstall")
        return True

    def refresh(self):
        print("Refresh")

    def notification(self, message, heading=None, icon=None, time=3000):
        print("NOTIFCATION: {0}".format(message))

    def get_input(self, message, default='', hidden=False):
        return raw_input('{0} ({1}): '.format(message, default)).strip() or default

    def dialog(self, message, heading=None):
        print(message)

    def dialog_yes_no(self, message, heading=None, yeslabel=None, nolabel=None):
        print(message)
        return True

    def play(self, data):
        text = ''

        headers = ''
        if '|' in data['url']:
            data['url'], headers = data['url'].split('|')

        # temporary work-around for inpustream issue
        if data.get('use_ia'):
            r = requests.head(data['url'])
            data['url'] = r.headers['location']
        ###########################################

        if data['url'].startswith('http') and headers:
            data['url'] += '|' + headers

        if data.get('use_ia'):
            text += '#KODIPROP:inputstreamaddon=inputstream.adaptive\n'
            text += '#KODIPROP:inputstream.adaptive.manifest_type=hls\n'
            if headers:
                text += '#KODIPROP:inputstream.adaptive.stream_headers={0}\n'.format(headers)
                text += '#KODIPROP:inputstream.adaptive.license_key={0}\n'.format('|' + headers)

        if data.get('type') == 'widevine':
            text += '#KODIPROP:inputstreamaddon=inputstream.adaptive\n'
            text += '#KODIPROP:inputstream.adaptive.manifest_type=mpd\n'
            text += '#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha\n'
            if headers: text += '#KODIPROP:inputstream.adaptive.stream_headers={0}\n'.format(headers)
            text += '#KODIPROP:inputstream.adaptive.license_key={0}\n'.format('{0}|{1}|R{{SSM}}|'.format(data['key'], headers))

        text += data['url']

        print(text)
        with open(os.path.join(config.DATA_DIR, 'out.strm'), "w") as f:
            f.write(text)

    def items(self, items, content='videos', title=None, history=True, cache=True):
        for item in items:
            print(item)

class KodiView(TextView):
    def reinstall(self):
        dialog = xbmcgui.Dialog()
        if dialog.yesno('Reinstall DRM?', 'This will delete the current Widevine DRM and reinstall it.'):
            return wvhelper.has_widevine(reinstall=True)

    def refresh(self):
        xbmc.executebuiltin('Container.Refresh')

    def notification(self, message, heading=None, icon=None, time=3000):
        if not heading: heading = config.ADDON_NAME
        if not icon: icon = os.path.join(config.ADDON_PATH, 'icon.png')

        dialog = xbmcgui.Dialog()
        dialog.notification(heading, message, icon, time)

    def get_input(self, message, default='', hidden=False):
        kb = xbmc.Keyboard(default, message, hidden)
        kb.doModal()
        if (kb.isConfirmed()):
            return kb.getText()
        return ''

    def dialog(self, message, heading=None):
        if not heading: heading = config.ADDON_NAME

        lines = list()
        for line in str(message).split('\n'):
            lines.append(line.strip())

        dialog = xbmcgui.Dialog()
        dialog.ok(heading, *lines)

    def dialog_yes_no(self, message, heading=None, yeslabel=None, nolabel=None):
        if not heading: heading = config.ADDON_NAME

        lines = list()
        for line in str(message).split('\n'):
            lines.append(line.strip())

        dialog = xbmcgui.Dialog()
        return dialog.yesno(heading, *lines, yeslabel=yeslabel, nolabel=nolabel)

    def play(self, data):
        headers = ''
        if '|' in data['url']:
            data['url'], headers = data['url'].split('|')

        # temporary work-around for inpustream issue
        if data.get('use_ia') and wvhelper.has_hls():
            r = requests.head(data['url'])
            data['url'] = r.headers['location']
        ###########################################

        if data['url'].startswith('http') and headers:
            data['url'] += '|' + headers

        li = self._create_list_item(data)

        if data.get('use_ia') and wvhelper.has_hls():
            li.setProperty('inputstreamaddon', 'inputstream.adaptive')
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
            if headers: 
                li.setProperty('inputstream.adaptive.stream_headers', headers)
                li.setProperty('inputstream.adaptive.license_key', '|' + headers)

        if data.get('type') == 'widevine' and wvhelper.has_widevine():
            li.setProperty('inputstreamaddon', 'inputstream.adaptive')
            li.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            if headers: li.setProperty('inputstream.adaptive.stream_headers', headers)
            li.setProperty('inputstream.adaptive.license_key', '{0}|{1}|R{{SSM}}|'.format(data['key'], headers))

        xbmcplugin.setResolvedUrl(config.ADDON_HANDLE, True, li)

    def _create_list_item(self, data):
        li = xbmcgui.ListItem(data.get('title'))
        if data.get('url'):
            li.setPath(data.get('url'))

        if data.get('playable', False):
            li.setProperty('IsPlayable', 'true')

        images = data.get('images', {})
        if not images.get('banner'):
            images['banner'] = images.get('fanart')
        if not images.get('fanart'):
            images['fanart'] = os.path.join(config.ADDON_PATH, 'fanart.jpg')
        if not images.get('thumb'):
            images['thumb'] = os.path.join(config.ADDON_PATH, 'icon.png')

        info =  data.get('info',{})
        if not info.get('title'):
            info['title'] = data.get('title')
        if not info.get('plot'):
            info['plot'] = info['title']

        li.setArt(images)
        li.setInfo('video', info)
        li.addStreamInfo('video', data.get('video',{}))
        li.addStreamInfo('audio', data.get('audio',{}))

        contexts = []
        for context in data.get('context', []):
            contexts.append((context[0], context[1]))

        li.addContextMenuItems(contexts)
        return li

    def items(self, items, content='videos', title=None, history=True, cache=True):
        listings = []
        for item in items:
            li = self._create_list_item(item)
            is_folder = item.get('is_folder', True) and not item.get('playable', False)
            xbmcplugin.addDirectoryItem(config.ADDON_HANDLE, item.get('url'), li, is_folder)

        if content: xbmcplugin.setContent(config.ADDON_HANDLE, content)
        if title: xbmcplugin.setPluginCategory(config.ADDON_HANDLE, title)

        xbmcplugin.endOfDirectory(config.ADDON_HANDLE, updateListing=not history, cacheToDisc=cache)

if config.KODI:
    import xbmc, xbmcgui, xbmcplugin, wvhelper
    View = KodiView
else:
    View = TextView