# -*- coding: utf-8 -*-

'''
    Tulip routine libraries, based on lambda's lamlib
    Author Twilight0

        License summary below, for more details please read license.txt file

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 2 of the License, or
        (at your option) any later version.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from __future__ import absolute_import, division, unicode_literals

from tulip.compat import urlencode, quote_plus, iteritems, basestring
from tulip import control
from tulip.init import sysaddon, syshandle


def add(items, cacheToDisc=True, content=None, mediatype=None, infotype='video'):

    """
    Creates a directory of items

    :param items: A list of dictionaries of items, each item must have at least two keys, action and title
    :param cacheToDisc: Deprecated in Krypton, no effect there
    :param content: String
    :param mediatype: String
    :param infotype: String
    :return: None
    """

    if items is None or len(items) == 0:
        return

    # sysicon = control.join(control.addonInfo('path'), 'resources', 'media')
    sysimage = control.addonInfo('icon')
    sysfanart = control.addonInfo('fanart')

    for i in items:

        try:

            try:
                label = control.lang(i['title']).encode('utf-8')
            except BaseException:
                label = i['title']

            if 'label' in i and not i['label'] == '0':
                label = i['label']

            if 'image' in i and not i['image'] == '0':
                image = i['image']
            elif 'poster' in i and not i['poster'] == '0':
                image = i['poster']
            elif 'icon' in i and not i['icon'] == '0':
                image = control.addonmedia(i['icon'])
            else:
                image = sysimage

            if 'banner' in i and not i['banner'] == '0':
                banner = i['banner']
            elif 'fanart' in i and not i['fanart'] == '0':
                banner = i['fanart']
            else:
                banner = image

            fanart = i['fanart'] if 'fanart' in i and not i['fanart'] == '0' else sysfanart

            isFolder = False if 'isFolder' in i and not i['isFolder'] == '0' else True

            try:
                is_play_boolean = i.get('isPlayable') in ['True', 'true', '1', 'yes', 'Yes']
            except Exception:
                is_play_boolean = False

            isPlayable = True if not isFolder and 'isPlayable' not in i else is_play_boolean

            if isPlayable:

                isFolder = False

            url = '%s?action=%s' % (sysaddon, i['action'])

            try:
                url += '&url=%s' % quote_plus(i['url'])
            except BaseException:
                pass
            try:
                url += '&title=%s' % quote_plus(i['title'])
            except KeyError:
                try:
                    url += '&title=%s' % quote_plus(i['title'].encode('utf-8'))
                except KeyError:
                    pass
            except BaseException:
                pass

            try:
                url += '&image=%s' % quote_plus(i['image'])
            except KeyError:
                try:
                    url += '&image=%s' % quote_plus(i['image'].encode('utf-8'))
                except KeyError:
                    pass
            except BaseException:
                pass
            try:
                url += '&name=%s' % quote_plus(i['name'])
            except KeyError:
                try:
                    url += '&name=%s' % quote_plus(i['name'].encode('utf-8'))
                except KeyError:
                    pass
            except BaseException:
                pass
            try:
                url += '&year=%s' % quote_plus(i['year'])
            except BaseException:
                pass
            try:
                url += '&plot=%s' % quote_plus(i['plot'])
            except KeyError:
                try:
                    url += '&plot=%s' % quote_plus(i['plot'].encode('utf-8'))
                except KeyError:
                    pass
            except BaseException:
                pass
            try:
                url += '&genre=%s' % quote_plus(i['genre'])
            except KeyError:
                try:
                    url += '&genre=%s' % quote_plus(i['genre'].encode('utf-8'))
                except KeyError:
                    pass
            except BaseException:
                pass
            try:
                url += '&dash=%s' % quote_plus(i['dash'])
            except BaseException:
                pass
            try:
                url += '&query=%s' % quote_plus(i['query'])
            except BaseException:
                pass

            cm = []
            menus = i['cm'] if 'cm' in i else []

            for menu in menus:
                try:
                    try:
                        tmenu = control.lang(menu['title']).encode('utf-8')
                    except BaseException:
                        tmenu = menu['title']
                    try:
                        qmenu = urlencode(menu['query'])
                    except Exception:
                        qmenu = urlencode(dict((k, v.encode('utf-8')) for k, v in menu['query'].items()))
                    cm.append((tmenu, 'RunPlugin(%s?%s)' % (sysaddon, qmenu)))
                except BaseException:
                    pass

            meta = dict((k, v) for k, v in iteritems(i) if not k == 'cm' and not v == '0')

            if mediatype is not None:
                meta['mediatype'] = mediatype

            item = control.item(label=label)

            item.setArt(
                {
                    'icon': image, 'thumb': image, 'poster': image, 'tvshow.poster': image, 'season.poster': image,
                    'banner': banner, 'tvshow.banner': banner, 'season.banner': banner, 'fanart': fanart
                }
            )

            item.addContextMenuItems(cm)
            item.setInfo(type=infotype, infoLabels=meta)

            if isPlayable:

                if not i['action'] == 'pvr_client':
                    item.setProperty('IsPlayable', 'true')
                else:
                    item.setProperty('IsPlayable', 'false')
                if not i['action'] == 'pvr_client' and infotype == 'video':
                    item.addStreamInfo('video', {'codec': 'h264'})

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder, totalItems=len(items))

        except BaseException as reason:
            from xbmc import log
            log('The reason of failure: ' + repr(reason))

    try:

        i = items[0]
        if i['next'] == '':
            raise Exception()

        url = '%s?action=%s&url=%s' % (sysaddon, i['nextaction'], quote_plus(i['next']))
        icon = i['nexticon'] if 'nexticon' in i else control.addonmedia('next.png')
        fanart = i['nextfanart'] if 'nextfanart' in i else sysfanart

        try:
            label = control.lang(i['nextlabel']).encode('utf-8')
        except Exception:
            label = 'Next'

        item = control.item(label=label)

        item.setArt(
            {
                'icon': icon, 'thumb': icon, 'poster': icon, 'tvshow.poster': icon, 'season.poster': icon,
                'banner': icon, 'tvshow.banner': icon, 'season.banner': icon, 'fanart': fanart
            }
        )

        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True, totalItems=len(items))

    except Exception:

        pass

    if content is not None:
        control.content(syshandle, content)

    control.directory(syshandle, cacheToDisc=cacheToDisc)


def m3u_maker(items=None):

    """
    Converts a list into an m3u playlist in string form, use builtin open method to save it somewhere
    :param items: list
    :return: str
    """

    if items is None:
        return

    m3u_list = []

    for i in items:

        try:
            url = '%s?action=%s' % (sysaddon, i['action'])
        except KeyError:
            return
        try:
            url += '&url=%s' % quote_plus(i['url'])
        except BaseException:
            pass
        try:
            url += '&title=%s' % quote_plus(i['title'])
        except KeyError:
            try:
                url += '&title=%s' % quote_plus(i['title'].encode('utf-8'))
            except KeyError:
                pass
        except BaseException:
            pass
        try:
            url += '&image=%s' % quote_plus(i['image'])
        except KeyError:
            try:
                url += '&image=%s' % quote_plus(i['image'].encode('utf-8'))
            except KeyError:
                pass
        except BaseException:
            pass
        try:
            url += '&name=%s' % quote_plus(i['name'])
        except KeyError:
            try:
                url += '&name=%s' % quote_plus(i['name'].encode('utf-8'))
            except KeyError:
                pass
        except BaseException:
            pass
        try:
            url += '&year=%s' % quote_plus(i['year'])
        except BaseException:
            pass
        try:
            url += '&plot=%s' % quote_plus(i['plot'])
        except KeyError:
            try:
                url += '&plot=%s' % quote_plus(i['plot'].encode('utf-8'))
            except KeyError:
                pass
        except BaseException:
            pass

        m3u_list.append(u'#EXTINF:0,{0}\n'.format(i['title']) + url + '\n')

    m3u = [u'#EXTM3U\n'] + m3u_list

    return ''.join(m3u)


def resolve(
        url, meta=None, icon=None, dash=False, manifest_type=None, inputstream_type='adaptive', headers=None,
        mimetype=None
):

    """
    Prepares a resolved url into a listitem for playback

    :param url: Requires a string or unicode, append required urlencoded headers with pipe |
    :param meta: a dictionary with listitem keys: values
    :param icon: String
    :param dash: Boolean
    :param manifest_type: String
    :param inputstream_type: String 99.9% of the time it is adaptive
    :param headers: dictionary or urlencoded string
    :param mimetype: String
    :return: None
    """

    # Fail gracefully instead of make Kodi complain.
    if url is None:
        from xbmc import log, LOGDEBUG
        log('URL was not provided, failure to resolve stream', LOGDEBUG)
        return

    if not headers and '|' in url:
        url = url.rpartition('|')[0]
        headers = url.rpartition('|')[2]
    elif headers:
        if isinstance(headers, basestring):
            if headers.startswith('|'):
                headers = headers[1:]
        elif isinstance(headers, dict):
            headers = urlencode(headers)

    if not dash and headers:
        url = '|'.join([url, headers])

    item = control.item(path=url)

    if icon is not None:
        item.setArt({'icon': icon, 'thumb': icon})

    if meta is not None:
        item.setInfo(type='Video', infoLabels=meta)

    krypton_plus = int(control.infoLabel('System.AddonVersion(xbmc.python)').replace('.', '')) >= 2250

    try:
        isa_enabled = control.addon_details('inputstream.adaptive').get('enabled')
    except KeyError:
        isa_enabled = False

    if dash and krypton_plus and isa_enabled:
        if not manifest_type:
            manifest_type = 'mpd'
        if not mimetype:
            mimetype = 'application/xml+dash'
        item.setContentLookup(False)
        item.setMimeType('{0}'.format(mimetype))
        item.setProperty('inputstreamaddon', 'inputstream.{}'.format(inputstream_type))
        item.setProperty('inputstream.{}.manifest_type'.format(inputstream_type), manifest_type)
        if headers:
            item.setProperty("inputstream.{}.stream_headers".format(inputstream_type), headers)
    elif mimetype:
        item.setContentLookup(False)
        item.setMimeType('{0}'.format(mimetype))

    control.resolve(syshandle, True, item)


__all__ = ["add", "resolve", "m3u_maker"]
