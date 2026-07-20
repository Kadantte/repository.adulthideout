#!/usr/bin/env python


import json
import re
import sys
import time
import urllib.parse
import urllib.request
import html
import http.cookiejar
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
from resources.lib.base_website import BaseWebsite

class MotherlessWebsite(BaseWebsite):
    LIVE_SNAPSHOT_TTL = 7200

    def __init__(self, addon_handle):
        super().__init__(
            name="motherless",
            base_url="https://motherless.xxx",
            search_url="https://motherless.xxx/term/videos/{}",
            addon_handle=addon_handle
        )
        self.sort_options = ["Newest", "Being Watched Now", "Favorites", "Most Viewed", "Most Commented", "Popular", "Archived", "Random Video"]
        self.sort_paths = {
            "Newest": "/videos/recent",
            "Being Watched Now": "/live/videos",
            "Favorites": "/videos/favorited",
            "Most Viewed": "/videos/viewed",
            "Most Commented": "/videos/commented",
            "Popular": "/videos/popular",
            "Archived": "/videos/archives",
            "Random Video": "/random/video"
        }
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))

    def _snapshot_path(self):
        profile = self.addon.getAddonInfo('profile') or 'special://profile/addon_data/plugin.video.adulthideout/'
        profile = xbmcvfs.translatePath(profile)
        xbmcvfs.mkdirs(profile)
        return profile.rstrip('/\\') + '/motherless_live_snapshot.json'

    @staticmethod
    def _new_generation():
        return str(int(time.time() * 1000000))

    def _split_live_url(self, url):
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        generation = query.pop('ah_generation', ['legacy'])[0]
        request_url = urllib.parse.urlunparse((
            parsed.scheme, parsed.netloc, parsed.path, parsed.params,
            urllib.parse.urlencode(query, doseq=True), parsed.fragment
        ))
        return request_url, generation

    def _with_generation(self, url, generation=None):
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        query['ah_generation'] = [generation or self._new_generation()]
        return urllib.parse.urlunparse((
            parsed.scheme, parsed.netloc, parsed.path, parsed.params,
            urllib.parse.urlencode(query, doseq=True), parsed.fragment
        ))

    def _load_live_snapshot(self, generation):
        path = self._snapshot_path()
        if not xbmcvfs.exists(path):
            return None
        try:
            handle = xbmcvfs.File(path)
            payload = json.loads(handle.read())
            handle.close()
            if payload.get('generation') != generation:
                return None
            if time.time() - float(payload.get('created', 0)) > self.LIVE_SNAPSHOT_TTL:
                return None
            items = payload.get('items')
            return payload if isinstance(items, list) and items else None
        except Exception:
            return None

    def _save_live_snapshot(self, generation, items, next_url=None):
        payload = {
            'generation': generation,
            'created': time.time(),
            'items': items,
            'next_url': next_url or '',
        }
        try:
            handle = xbmcvfs.File(self._snapshot_path(), 'w')
            handle.write(json.dumps(payload, ensure_ascii=True, separators=(',', ':')))
            handle.close()
        except Exception:
            pass

    def get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Referer': self.base_url
        }

    def make_request(self, url):
        try:
            headers = self.get_headers()
            req = urllib.request.Request(url, headers=headers)
            with self.opener.open(req, timeout=20) as response:
                final_url = response.geturl()
                if "/random/video" in url and self.base_url in final_url and "/random/video" not in final_url:
                    self.play_video(final_url)
                    return None
                return response.read().decode('utf-8', errors='ignore')
        except Exception:
            return None

    def process_content(self, url):
        if not url or url == "BOOTSTRAP":
            url = self.base_url + "/videos/recent"

        self.add_basic_dirs(url)
        path = urllib.parse.urlparse(url).path
        is_live = path == '/live/videos'
        generation = None
        request_url = url
        if is_live:
            request_url, generation = self._split_live_url(url)
            snapshot = self._load_live_snapshot(generation)
            if snapshot:
                self._render_video_items(
                    snapshot['items'],
                    request_url,
                    generation,
                    snapshot.get('next_url')
                )
                self.end_directory()
                return

        content = self.make_request(request_url)
        if not content:
            self.end_directory()
            return

        if path.startswith('/groups'):
            self.process_groups(content, request_url)
        elif path.startswith('/galleries'):
            self.process_galleries(content, request_url)
        elif path.startswith(('/shouts', '/orientation/')):
            self.process_categories(content, request_url)
        else:
            items, next_url = self._parse_video_items(content)
            if is_live and items:
                self._save_live_snapshot(generation, items, next_url)
            self._render_video_items(items, request_url, generation if is_live else None, next_url)
            
        self.end_directory()

    def add_basic_dirs(self, current_url):
        self.add_dir('[COLOR blue]Search[/COLOR]', '', 5, self.icons['search'], self.fanart)
        self.add_dir('Categories', f'{self.base_url}/orientation/straight', 2, self.icons['categories'], self.fanart)
        self.add_dir('Groups', f'{self.base_url}/groups', 2, self.icons['groups'], self.fanart)
        self.add_dir('Galleries', f'{self.base_url}/galleries/updated', 2, self.icons['galleries'], self.fanart)

    def _parse_video_items(self, content):
        pattern = re.compile(r'<a href="([^\"]+)" class="img-container"[^>]*>.+?<span class="size">([:\d]+)</span>.+?<img class="static" src="([^\"]+)"[^>]*alt="([^\"]+)"', re.DOTALL)
        matches = re.findall(pattern, content)
        items = []
        for href, duration, thumb, name in matches:
            title = f"{html.unescape(name.strip())} [COLOR yellow]({duration})[/COLOR]"
            video_url = urllib.parse.urljoin(self.base_url, href)
            items.append({'title': title, 'url': video_url, 'thumb': thumb})
        match = re.search(r'<link rel="next" href="(.+?)"', content)
        next_url = html.unescape(match.group(1)) if match else ''
        return items, next_url

    def _render_video_items(self, items, current_url, generation=None, next_url=None):
        if generation is not None:
            action_url = (
                f'{sys.argv[0]}?mode=7&action=reload_live&website={self.name}'
                f'&original_url={urllib.parse.quote_plus(current_url)}'
            )
            item = xbmcgui.ListItem('[COLOR blue]Reload List[/COLOR]')
            item.setArt({'thumb': self.icons['default'], 'icon': self.icons['default'], 'fanart': self.fanart})
            xbmcplugin.addDirectoryItem(self.addon_handle, action_url, item, isFolder=False)
        for item in items:
            self.add_link(item['title'], item['url'], 4, item['thumb'], self.fanart)
        if next_url:
            self.add_dir('[COLOR blue]Next Page >>>>[/COLOR]', next_url, 2, self.icons['default'], self.fanart)

    def process_video_list(self, content, current_url):
        items, next_url = self._parse_video_items(content)
        self._render_video_items(items, current_url, next_url=next_url)

    def reload_live(self, original_url=None):
        request_url, _ = self._split_live_url(original_url or self.base_url + '/live/videos')
        new_url = self._with_generation(request_url)
        target = (
            f'{sys.argv[0]}?mode=2&url={urllib.parse.quote_plus(new_url)}'
            f'&website={self.name}'
        )
        xbmc.executebuiltin(f'Container.Update({target},replace)')

    def process_groups(self, content, current_url):
        pattern = re.compile(r'<h1 class="group-bio-name">.+?<a href="/g/([^\"]*)">\s*(.+?)\s*</a>.+?src="https://([^\"]*)"', re.DOTALL)
        matches = re.findall(pattern, content)
        
        for part, name, thumb_host in matches:
            video_list_url = f"{self.base_url}/g/{part}/videos"
            thumb_url = f"https://{thumb_host}"
            self.add_dir(html.unescape(name.strip()), video_list_url, 2, thumb_url, self.fanart)
        self.add_next_button(content)

    def process_galleries(self, content, current_url):
        pattern = re.compile(r'<img class="static" src="(https://[^\"]*)".*?<a href="/G([^\"]*)"[^>]*title="([^\"]*)".*?<span>\s*(\d+)\s*Videos', re.DOTALL)
        matches = re.findall(pattern, content)

        for thumb, gid, name, count in matches:
            if int(count) > 0:
                self.add_dir(f"{html.unescape(name)} ({count} Videos)", f"{self.base_url}/GV{gid}", 2, thumb, self.fanart)
        self.add_next_button(content)

    def process_categories(self, content, current_url):
        orientations = {'Straight': 'straight', 'Gay': 'gay', 'Transsexual': 'transsexual', 'Extreme': 'extreme', 'Funny & Misc.': 'funny'}
        
        current_orientation_path = None
        if '/orientation/' in current_url:
            current_orientation_path = current_url.split('/orientation/')[-1].strip('/')

        if current_orientation_path and current_orientation_path in orientations.values():
            pattern = re.compile(r'<a href="(/porn/[^/"]+/videos)" class="pop plain">([^<]+)</a>', re.DOTALL)
            all_cats = list(set(pattern.findall(content)))
            
            known_prefixes = {p + '-' for p in orientations.values() if p != 'straight'}
            for path, name in sorted(all_cats, key=lambda x: x[1].strip()):
                clean_path = path.split('/')[2]
                is_straight = not any(clean_path.startswith(p) for p in known_prefixes)
                if (current_orientation_path == 'straight' and is_straight) or \
                   (current_orientation_path != 'straight' and clean_path.startswith(current_orientation_path + '-')):
                    cat_url = urllib.parse.urljoin(self.base_url, path)
                    self.add_dir(html.unescape(name.strip()), cat_url, 2, self.icons['categories'], self.fanart)
        else:
            for name, path_part in orientations.items():
                self.add_dir(f"[COLOR yellow]{name}[/COLOR]", f'{self.base_url}/orientation/{path_part}', 2, self.icons['categories'], self.fanart)

    def add_next_button(self, content):
        match = re.search(r'<link rel="next" href="(.+?)"', content)
        if match:
            self.add_dir('[COLOR blue]Next Page >>>>[/COLOR]', html.unescape(match.group(1)), 2, self.icons['default'], self.fanart)

    def play_video(self, url):
        content = self.make_request(url)
        if content:
            m = re.search(r"__fileurl = '(.+?)';", content)
            if m:
                path = m.group(1)
                li = xbmcgui.ListItem(path=path)
                li.setProperty('IsPlayable', 'true')
                li.setMimeType('video/mp4')
                xbmcplugin.setResolvedUrl(self.addon_handle, True, li)
                return
        self.notify_error("Failed to find media URL")

    def select_sort(self, original_url=None):
        if not original_url: return self.notify_error("Cannot sort, original URL not provided.")
        
        if original_url.startswith('plugin://'):
             try:
                 params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(original_url).query))
                 if 'url' in params and params['url'] != 'BOOTSTRAP':
                     original_url = params['url']
                 elif params.get('url') == 'BOOTSTRAP':
                     original_url = self.base_url + "/videos/recent"
             except:
                 pass

        dialog = xbmcgui.Dialog()
        preselect = -1
        
        for i, option in enumerate(self.sort_options):
             if self.sort_paths[option] in original_url:
                 preselect = i
                 break
        
        idx = dialog.select("Sort by...", self.sort_options, preselect=preselect)
        if idx != -1:
            sort_key = self.sort_options[idx]
            self.addon.setSetting('motherless_sort_by', str(idx))
            path = self.sort_paths[sort_key]
            new_url = urllib.parse.urljoin(self.base_url, path)
            if sort_key == "Being Watched Now":
                new_url = self._with_generation(new_url)
            xbmc.executebuiltin(f'Container.Update({sys.argv[0]}?mode=2&url={urllib.parse.quote_plus(new_url)}&website={self.name},replace)')
