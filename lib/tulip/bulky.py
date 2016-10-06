# -*- coding: utf-8 -*-

'''
    Bulky IPTV 2.0 Addon
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


import re, json, base64, sys
import bookmarks, client, control, directory, cache


class Indexer:

    def __init__(self):

        self.list = [] ; self.list_no_adults = []
        self.base_link = 'http://bulkyiptv.com'
        self.port = '5750'  # might change
        self.enigma = 'enigma2.php'  # php param
        self.panel_api = 'panel_api.php'  # php param
        self.timeshift = 'timeshift.php' # php param
        self.get_live_cat = '&type=get_live_categories'  # type
        self.get_live_streams = '&type=get_live_streams'  # type
        self.get_vod_cat = '&type=get_vod_categories'  # type
        self.get_vod_scat = '&type=get_vod_scategories'  # type
        self.get_vod_streams = '&type=get_vod_streams'  # type
        self.action = '&action=get_epg'  # type
        self.cat_id = '&cat_id='  # cat or scat or stream_id
        self.scat_id = '&scat_id='  # cat or scat or stream_id
        self.stream_id = '&stream_id='  # cat or scat or stream_id
        self.username = control.setting('username')
        self.password = control.setting('password')

    def url_generator(self, php_param, username, password, _type_='', cat=''):

        url = self.base_link + ':' + self.port + '/' + php_param + '?' + 'username=' + username + '&' + 'password=' + password + _type_ + cat

        return url

    def root(self):

        self.list = [
            {
                'title': 'Live TV',
                'action': 'live_tv',
                'icon': 'live.png'
            }
            ,
            {
                'title': 'Video On Demand',
                'action': 'vod',
                'icon': 'movies.png'
            }
            ,
            {
                'title': 'TV Shows',
                'action': 'tv_shows',
                'icon': 'tv-shows.png'
            }
            ,
            {
                'title': 'TV Catchup',
                'action': 'tv_catch_up',
                'icon': 'tv-catchup.png'
            }
            ,
            {
                'title': 'TV Guide',
                'action': 'tv_guide',
                'icon': 'tv-guide.png'
            }
            ,
            {
                'title': 'Bookmarks',
                'action': 'bookmarks',
                'icon': 'bookmarks.png'
            }
            ,
            {
                'title': 'Search',
                'action': 'search',
                'icon': 'search.png'
            }
            ,
            {
                'title': 'My Account',
                'action': 'my_account',
                'icon': 'user.png'
            }
            ,
            {
                'title': 'Settings',
                'action': 'settings',
                'icon': 'settings.png'
            }
        ]

        for item in self.list:
            item.update({'fanart': control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')})


        if control.setting('prompt') == 'true':
            control.okDialog(heading=control.addonInfo('name'), line1='Please input your username/password in order to use ' + control.addonInfo('name'))
            if control.yesnoDialog(line1='Would you like to input your username/password now?', line2='', line3=''):
                username_input = control.inputDialog(heading='Please type your username:')
                control.setSetting('username', username_input.lower())
                password_input = control.inputDialog(heading='Please type your password:')
                control.setSetting('password', password_input.lower())

                link = self.url_generator(self.panel_api, username_input.lower(), password_input)

                try:
                    _json_ = client.request(link)

                    status = json.loads(_json_)['user_info'].values()[1]

                    if status == 'Active':
                        Tools().authorize()
                        control.set_view_mode('500')
                        directory.add(self.list)
                        control.setSetting('prompt', 'false')

                    elif status == 'Expired':
                        control.okDialog(heading=control.addonInfo('name'), line1='Your account has expired!')

                except IndexError:
                    control.okDialog(heading=control.addonInfo('name'), line1='Wrong username and/or password or not yet authorized')

                except ValueError:
                    control.okDialog(heading=control.addonInfo('name'), line1='Empty username/password fields or invalid network settings and/or host')

                except TypeError:
                    control.okDialog(heading=control.addonInfo('name'), line1='Unable to connect')

            else:
                control.okDialog(heading=control.addonInfo('name'), line1=control.addonInfo('name') + ' will not work without username & password')

        elif control.setting('prompt') == 'false' and control.condVisibility('Container.HasFolders'):

            try:
                link = self.url_generator(self.panel_api, self.username, self.password)
                _json_ = client.request(link)
                status = json.loads(_json_)['user_info'].values()[1]

                if status == 'Active':
                    Tools().authorize()
                    control.set_view_mode('500')
                    directory.add(self.list)

                elif status == 'Expired':
                    control.okDialog(heading=control.addonInfo('name'), line1='Your account has expired!')
                    control.setSetting('prompt', 'true')

            except IndexError:
                control.okDialog(heading=control.addonInfo('name'), line1='Wrong username and/or password or not yet authorized')
                control.setSetting('prompt', 'true')

            except ValueError:
                control.okDialog(heading=control.addonInfo('name'), line1='Empty username/password fields or invalid network settings and/or host')
                control.setSetting('prompt', 'true')

            except TypeError:
                control.okDialog(heading=control.addonInfo('name'), line1='Unable to connect')

    def live_category_list_generator(self, link):

        _xml_ = client.request(link)

        items = re.findall('<channel>(.*?)</channel>', _xml_)

        for item in items:

            if control.setting('showadult') == 'false':

                if item.startswith('<title>QWR1bHQ='):
                    continue

            title = re.findall('<title>([a-z0-9=]*?)</title>', item, re.I)

            description = re.findall('<description>([a-z0-9=]*?)</description>', item, re.I)

            _id_ = re.findall('<category_id>(\d*?)</category_id>', item)

            playlist_url = re.findall('<playlist_url><!\[CDATA\[(.*?)\]\]></playlist_url>', item)

            icon = 'iptv.png'

            fanart = control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')

            self.list.append({'title': base64.b64decode(str(title).strip("[]")),
                              'plot': base64.b64decode(str(description).strip("[]")),
                              'action': 'livetv_category&_id_={0}'.format(str(_id_).strip("[]\'")),
                              'url': str(playlist_url).strip("[]\'"), 'icon': icon, 'fanart': fanart})

        return self.list

    def vod_category_list_generator(self, link):

        _xml_ = client.request(link)

        items = re.findall('<channel>(.*?)</channel>', _xml_)

        for item in items:

            if item.startswith('<title>VFYgU2hvd3M='):
                continue

            title = re.findall('<title>([a-z0-9=/]*?)</title>', item, re.I)

            description = re.findall('<description>([a-z0-9=/]*?)</description>', item, re.I)

            _id_ = re.findall('<category_id>(\d*?)</category_id>', item)

            playlist_url = re.findall('<playlist_url><!\[CDATA\[(.*?)\]\]></playlist_url>', item)

            # icon = re.findall('<desc_image><!\[CDATA\[(.*?)\]\]></desc_image>', item)

            icon = 'movies.png'

            fanart = control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')

            self.list.append(({'title': base64.b64decode(str(title).strip("[]")),
                               'plot': base64.b64decode(str(description).strip("[]")),
                               'action': 'vod_category&_id_={0}'.format(str(_id_).strip("[]\'").strip("\'")),
                               'url': str(playlist_url).strip("[]\'"), 'icon': icon, 'fanart': fanart}))

        return self.list

    def tv_shows_category_list_generator(self, link):

        _xml_ = client.request(link)

        items = re.findall('<channel>(.*?)</channel>', _xml_)

        for item in items:

            title = re.findall('<title>([a-z0-9=/]*?)</title>', item, re.I)

            description = re.findall('<description>([a-z0-9=/]*?)</description>', item, re.I)

            _id_ = re.findall('<category_id>(\d*?)</category_id>', item)

            playlist_url = re.findall('<playlist_url><!\[CDATA\[(.*?)\]\]></playlist_url>', item)

            # icon = re.findall('<desc_image><!\[CDATA\[(.*?)\]\]></desc_image>', item)

            icon = 'tv-shows.png'

            fanart = control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')

            self.list.append(({'title': base64.b64decode(str(title).strip("[]")),
                               'plot': base64.b64decode(str(description).strip("[]")),
                               'action': 'tv_show_list&_id_={0}'.format(str(_id_).strip("[]").strip("\'")),
                               'url': str(playlist_url).strip("[]\'"), 'icon': icon, 'fanart': fanart}))

        return self.list

    def live_stream_list_generator(self, link):

        _xml_ = client.request(link)

        items = re.findall('<channel>(.*?)</channel>', _xml_)

        for item in items:

            title = re.findall('<title>([a-z0-9=/]*?)</title>', item, re.I)
            title = base64.b64decode(str(title).strip('[]'))

            description = re.findall('<description>([a-z0-9=/]*?)</description>', item, re.I)
            plot = base64.b64decode(str(description).strip("[]\'"))

            icon = re.findall('<desc_image><!\[CDATA\[(.*?)\]\]></desc_image>', item)

            if icon == ['']:
                icon = control.join(control.addonPath, 'resources', 'media', 'iptv.png')

            fanart = control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')

            url = re.findall('<stream_url><!\[CDATA\[(.*?)\]\]></stream_url>', item)
            url = str(url).strip("[]\'")

            if control.setting('usehls') == 'true':

                self.list.append({'title': title.replace('18 :', '18: ').lstrip("! "), 'plot': plot, 'url': url.replace('.ts', '.m3u8'),
                                  'image': str(icon).strip("[]\'"), 'fanart': fanart})

            elif control.setting('usehls') == 'false':

                self.list.append({'title': title.replace('18 :', '18: '), 'plot': plot, 'url': url, 'image': str(icon).strip("[]\'"),
                                  'fanart': fanart})

        return self.list

    def vod_stream_list_generator(self, link):

        _xml_ = client.request(link, limit=str(10240))

        items = re.findall('<channel>(.*?)</channel>', _xml_)

        for item in items:
            title = re.findall('<title>([a-z0-9=/]*?)</title>', item, re.I)

            description = re.findall('<description>([a-z0-9=/]*?)</description>', item, re.I)

            icon = re.findall('<desc_image><!\[CDATA\[(.*?)\]\]></desc_image>', item)

            if icon == ['']:
                icon = control.join(control.addonPath, 'resources', 'media', 'tv_shows.png')

            fanart = control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')

            url = re.findall('<stream_url><!\[CDATA\[(.*?)\]\]></stream_url>', item)

            self.list.append({'title': base64.b64decode(str(title).strip('[]')),
                              'plot': base64.b64decode(str(description).strip("[]\'")),
                              'url': str(url).strip("[]\'"), 'image': str(icon).strip("[]\'"),
                              'action': 'play', 'isFolder': 'False', 'fanart': fanart})

        return self.list

    def bookmarks(self):

        self.list = bookmarks.get()

        if self.list is None:
            return

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['delbookmark'] = item['url']
            item.update({'cm': [{'title': 'Remove from bookmarks', 'query': {'action': 'deleteBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)

    def live_tv(self):

        self.list = cache.get(self.live_category_list_generator, 24, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_live_cat))

        if self.list is None:
            return

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)

    def livetv_category(self, _id_):

        self.list = cache.get(self.live_stream_list_generator, 1,
                              self.url_generator(self.enigma, self.username, self.password, _type_=self.get_live_streams, cat=self.cat_id) + _id_)

        if self.list is None:
            return

        for item in self.list:
            item.update({'action': 'play', 'isFolder': 'False'})

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        if not _id_ == '0':
            self.list = sorted(self.list, key=lambda k: k['title'].lower())

        else:
            pass

        if _id_ == '0':

            if control.setting('showadult') == 'false':

                bad_strings = ['ADULT', 'Adult', 'XXX', 'PORN', 'Hustler', '18:', 'LO:', 'Playboy TV', 'Babenation']

                self.list_no_adults = [item for item in self.list if not any(bad in item['title'] for bad in bad_strings)]

                control.set_view_mode('503')
                directory.add(self.list_no_adults, content='episodes')

            elif control.setting('showadult') == 'true':

                control.set_view_mode('503')
                directory.add(self.list, content='episodes')

        else:
            control.set_view_mode('503')
            directory.add(self.list, content='episodes')

    def vod(self):
        self.list = cache.get(self.vod_category_list_generator, 24, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_vod_cat))

        if self.list is None:
            return

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)

    def vod_category(self, _id_):

        self.list = cache.get(self.vod_stream_list_generator, 12, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_vod_streams, cat=self.cat_id) + _id_)

        if self.list is None:
            return

        for item in self.list:
            item.update({'action': 'play', 'isFolder': 'False'})

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        # self.list = sorted(self.list, key=lambda k: k['title'].lower())

        control.set_view_mode('515')
        directory.add(self.list, content='movies')

    def tv_shows(self):

        self.list = cache.get(self.tv_shows_category_list_generator, 24, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_vod_scat,  cat=self.scat_id) + '43')

        if self.list is None:
            return

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)

    def tv_show_list(self, _id_):

        self.list = cache.get(self.vod_stream_list_generator, 12, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_vod_streams,  cat=self.cat_id) + _id_)

        if self.list is None:
            return

        for item in self.list:
            item.update({'action': 'play', 'isFolder': 'False'})

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        # self.list = sorted(self.list, key=lambda k: k['title'].lower())

        control.set_view_mode('503')
        directory.add(self.list, content='episodes')

    def catchup(self, link):

        _json_ = client.request(link, limit=str(10240))

        available_channels = json.loads(_json_)['available_channels']

        for item in available_channels.values():

            tv_archive = item['tv_archive']

            if tv_archive == 1:

                title = item['name']
                _id_ = item['stream_id']
                image = item['stream_icon']

                if image == '':
                    image = control.join(control.addonPath, 'resources', 'media', 'iptv.png')

                self.list.append({'title': title.replace('ITV2', 'ITV 2').replace('ITV4', 'ITV 4'), 'action': 'tv_catch_up_list&_id_={0}'.format(_id_),  'image': image, 'fanart': control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')})

        return self.list

    def tv_catch_up(self):

        self.list = cache.get(self.catchup, 24, self.base_link + ':' + self.port + '/' + self.panel_api + '?' + 'username=' + self.username + '&' + 'password=' + self.password)

        if self.list is None:
            return

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)

    def catch_up_b4cache(self, _id_):

        import datetime, calendar, time

        link = self.url_generator(self.panel_api, self.username, self.password, self.action, self.stream_id) + _id_

        listing = client.request(link)
        catchup = re.findall('"title":"([a-z0-9=]*?)","lang":"en","start":"(\d*?)","end":"(\d*?)","description":"([a-z0-9=]*?)"', listing, re.I)

        onedaybacktime = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        current_time_minus_1_day = calendar.timegm(onedaybacktime.timetuple())
        current_time = int(time.time())

        for title, start, end, description in catchup:

            if current_time_minus_1_day < int(start) < current_time:

                hourminute = datetime.datetime.fromtimestamp(int(start)).strftime('%H:%M')

                title = base64.b64decode(str(title))

                plot = base64.b64decode(str(description))

                duration = ((int(end) - int(start)) / int(60))

                start_time = datetime.datetime.fromtimestamp(int(start)).strftime('%Y-%m-%d:%H-%M')

                url = self.base_link + ':' + self.port + '/streaming/' + self.timeshift + '?username=' + self.username + '&password=' + self.password + '&stream=' + _id_ + '&duration={0}'.format(duration) + '&start=' + start_time

                self.list.append({'title': hourminute + ' - ' + title, 'plot': plot, 'url': url, 'fanart': control.join(control.addonPath, 'resources', 'media', 'hometheater.jpg')})

        return self.list

    def tv_catch_up_list(self, _id_, image):

        self.list = cache.get(self.catch_up_b4cache, 1, _id_)

        if self.list is None:
            return

        for item in self.list:
            item.update({'action': 'play', 'isFolder': 'False', 'image': image})

        control.set_view_mode('515')
        directory.add(self.list, content='movies')

    def tv_guide(self):
        control.execute('ActivateWindow(TVGuide)')

    def search(self):
        self.list = [
            {
                'title': 'Search TV Channel',
                'action': 'search_channel',
                'icon': 'live.png'
            }
            ,
            {
                'title': 'Search Movie',
                'action': 'search_movie',
                'icon': 'movies.png'
            }
            ,
            {
                'title': 'Search TV Show',
                'action': 'search_show',
                'icon': 'tv-shows.png'
            }
        ]

        directory.add(self.list)

    def search_channel(self):

        self.list = cache.get(self.live_stream_list_generator, 1, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_live_streams, cat=self.cat_id) + '0')

        if self.list is None:
            return

        search_str = control.inputDialog(heading='Search for a TV channel:')

        if search_str == '':
            return

        self.list = [item for item in self.list if search_str.lower() in item['title'].lower()]

        for item in self.list:
            item.update({'action': 'play', 'isFolder': 'False'})

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        control.set_view_mode('503')
        directory.add(self.list, content='episodes')

    def search_movie(self):

        self.list = cache.get(self.vod_stream_list_generator, 1, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_vod_streams, cat=self.cat_id) + '0')

        if self.list is None:
            return

        search_str = control.inputDialog(heading='Search for a Movie or a TV show:')

        if search_str == '':
            return

        self.list = [item for item in self.list if search_str.lower() in item['title'].lower()]

        for item in self.list:
            item.update({'action': 'play', 'isFolder': 'False'})

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)

    def search_show(self):

        self.list = cache.get(self.tv_shows_category_list_generator, 1, self.url_generator(self.enigma, self.username, self.password, _type_=self.get_vod_scat,  cat=self.scat_id) + '43')

        if self.list is None:
            return

        search_str = control.inputDialog(heading='Search for a TV show:')

        if search_str == '':
            return

        self.list = [item for item in self.list if search_str.lower() in item['title'].lower()]

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            item.update({'cm': [{'title': 'Add to bookmarks', 'query': {'action': 'addBookmark_category', 'url': json.dumps(bookmark)}}]})

        self.list = sorted(self.list, key=lambda k: k['title'].lower())

        directory.add(self.list)

    def play(self, url):
        directory.resolve(url)

    def my_account(self):

        link = self.url_generator(self.panel_api, self.username, self.password)

        _json_ = client.request(link)

        user_info = json.loads(_json_)['user_info']

        server_info = json.loads(_json_)['server_info']

        username = user_info.values()[0]

        status = user_info.values()[1]

        reg_str = user_info.values()[3]

        import datetime

        reg_date = datetime.datetime.fromtimestamp(int(reg_str)).strftime('%H:%M - %d.%m.%Y')

        exp_str = user_info.values()[6]

        exp_date = datetime.datetime.fromtimestamp(int(exp_str)).strftime('%H:%M - %d.%m.%Y')

        trial = user_info.values()[2]

        url = server_info.values()[0]

        port = server_info.values()[1]

        if trial == '0':
            trial = str('No')

        elif trial == '1':
            trial = str('Yes')

        connections = str(user_info.values()[7])

        _max_ = str(user_info.values()[9])

        self.list = [
            {
                'title': 'User: ' + username,
                'action': None,
                'icon': 'user.png',
                'plot': 'Your username is: ' + username,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Status: ' + status,
                'action': None,
                'icon': 'account.png',
                'plot': 'Account status is: ' + status,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Registered: ' + reg_date,
                'action': None,
                'icon': 'calendar.png',
                'plot': 'Registration date on: ' + reg_date,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Expires: ' + exp_date,
                'action': None,
                'icon': 'hourglass.png',
                'plot': 'Expiration date: ' + exp_date,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Trial: ' + trial,
                'action': None,
                'icon': 'gavel.png',
                'plot': 'Is this account a trial one? ' + trial,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Users connected: ' + connections,
                'action': None,
                'icon': 'connections.png',
                'plot': 'Number of users connected now: ' + connections,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Max allowed connections: ' + _max_,
                'action': None,
                'icon': 'max.png',
                'plot': 'Number of maximum allowed connections: ' + _max_,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Server address: ' + 'http://' + url,
                'action': None,
                'icon': 'http.png',
                'plot': 'Root server http address: ' + 'http://' + url,
                'isFolder': 'false'
            }
            ,
            {
                'title': 'Port: ' + port,
                'action': None,
                'icon': 'port.png',
                'plot': 'Port used for connecting: ' + port,
                'isFolder': 'false'
            }
        ]

        control.set_view_mode('503')
        directory.add(self.list, content='episodes')

    def settings(self):
        control.openSettings()


class Tools:

    def __init__(self):
        pass

    def authorize(self):

        import hashlib

        string_md5 = '6b717f04c10f39155ce543b8f6641c92'
        string_name = control.addonInfo('author')

        if string_md5 != hashlib.md5(string_name).hexdigest():
            control.okDialog(heading=base64.b64decode('T3VwcyEhIQ=='), line1=base64.b64decode('RG9uJ3QgY2hhbmdlIGF1dGhvcidzIG5hbWUhISENClR3aWxpZ2h0KDApIGRldmVsb3BlZCB0aGlzIGFkZG9uISENCmNvbnRhY3QgYWRkcmVzczogdHdpbGlnaHRAZnJlZW1haWwuZ3I='))
            sys.exit()
        else:
            control.infoDialog('Login successful')

    def clear_cache(self):

        cache_file = control.cacheFile

        if control.exists(cache_file):
            if control.yesnoDialog(line1='Do you want to clear addon\'s cache file?', line2='', line3=''):
                control.deleteFile(cache_file)
            else:
                control.okDialog(control.addonInfo('name'), 'Cancelled...')
        else:
            control.infoDialog('No cache file was found')

    def clear_bookmarks(self):

        bookmarks_file = control.bookmarksFile

        if control.exists(bookmarks_file):
            if control.yesnoDialog(line1='Do you want to purge your bookmarks?', line2='', line3=''):
                control.deleteFile(bookmarks_file)
            else:
                control.okDialog(control.addonInfo('name'), 'Cancelled...')
        else:
            control.infoDialog('No bookmarks were found')

    def activate_advanced_settings(self):

        import shutil

        advanced_file = control.join(control.transPath('special://home/userdata/'), 'advancedsettings.xml')

        if not control.exists(advanced_file):
            if control.yesnoDialog(line1='Do you want to apply suggested advanced settings to your Kodi setup?', line2='', line3=''):
                shutil.copy(control.join(control.addonInfo('path'), 'resources', 'advancedsettings.xml'), advanced_file)
            else:
                control.okDialog(control.addonInfo('name'), 'Cancelled...')
        elif control.exists(advanced_file):
            if control.yesnoDialog(line1='Do you want to apply suggested advanced settings to your Kodi setup?', line2='**This will overwrite current advanced settings**', line3='Proceed?'):
                shutil.copy(control.join(control.addonInfo('path'), 'resources', 'advancedsettings.xml'), advanced_file)
            else:
                control.okDialog(control.addonInfo('name'), 'Cancelled...')

    def iptv_setup(self):

        import shutil

        iptv_file = control.join(control.transPath('special://home/userdata/addon_data/pvr.iptvsimple'), 'settings.xml')

        if not control.exists(iptv_file):
            if control.yesnoDialog(line1='Do you want to apply suggested iptv settings for TV Guide use?', line2='', line3=''):
                shutil.copy(control.join(control.addonInfo('path'), 'resources', 'iptv_settings.xml'), iptv_file)
            else:
                control.okDialog(control.addonInfo('name'), 'Cancelled...')
        elif control.exists(iptv_file):
            if control.yesnoDialog(line1='Do you want to apply suggested iptv settings for TV Guide use?', line2='**Current settings will be overwritten**', line3='Proceed?'):
                shutil.copy(control.join(control.addonInfo('path'), 'resources', 'iptv_settings.xml'), iptv_file)
            else:
                control.okDialog(control.addonInfo('name'), 'Cancelled...')
