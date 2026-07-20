# -*- coding: utf-8 -*-
import html
import os
import re
import urllib.parse

import requests

from resources.lib.base_website import BaseWebsite
from resources.lib.resolvers import resolver
from resources.lib.wordpress_api_tube import WordPressApiTube


class CzechVideo(BaseWebsite):
    def __init__(self, addon_handle, addon=None):
        super().__init__(
            "czechvideo", "https://czechvideo.ac/",
            "https://czechvideo.ac/index.php?do=search&subaction=search&story={}",
            addon_handle, addon,
        )
        self.label = "CzechVideo"
        self.session = requests.Session()
        self.ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        self.icon = os.path.join(self.addon.getAddonInfo("path"), "resources", "logos", "czechvideo.png")
        self.icons["default"] = self.icon

    def _headers(self, referer=None, accept=None):
        return {
            "User-Agent": self.ua,
            "Referer": referer or self.base_url,
            "Accept": accept or "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
        }

    def _get(self, url, referer=None):
        try:
            response = self.session.get(url, headers=self._headers(referer), timeout=20)
            if response.status_code == 200:
                return response.text
            self.logger.warning("[czechvideo] HTTP %s for %s", response.status_code, url)
        except Exception as exc:
            self.logger.warning("[czechvideo] Request failed for %s: %s", url, exc)
        return ""

    def _clean(self, value):
        value = re.sub(r"<[^>]+>", " ", value or "")
        return re.sub(r"\s+", " ", html.unescape(value)).strip()

    def _absolute(self, value, base=None):
        return urllib.parse.urljoin(base or self.base_url, html.unescape(value or "").strip())

    def _thumbnail(self, value):
        thumb = self._absolute(value)
        if not thumb:
            return self.icon
        return "{}|{}".format(
            thumb,
            urllib.parse.urlencode({"User-Agent": self.ua, "Referer": self.base_url}),
        )

    def get_start_url_and_label(self):
        return self.base_url, self.label

    def _page_url(self, url, page):
        if page <= 1:
            return url
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(parsed.query)
        if query.get("do") == ["search"]:
            query["search_start"] = [str(page)]
            return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))
        path = re.sub(r"/page/\d+/?$", "/", parsed.path or "/")
        path = path.rstrip("/") + "/page/{}/".format(page) if path.rstrip("/") else "/page/{}/".format(page)
        return urllib.parse.urlunparse(parsed._replace(path=path))

    def _videos(self, page_html):
        items = []
        for block in re.findall(r'<div\b[^>]+class=["\']short-story["\'][^>]*>([\s\S]*?)<div\b[^>]+class=["\']clear["\']', page_html or "", re.IGNORECASE):
            link = re.search(r'<a\b[^>]+href=["\']([^"\']+)["\'][^>]+title=["\']([^"\']+)', block, re.IGNORECASE)
            image = re.search(r'<img\b[^>]+(?:data-src|src)=["\']([^"\']+)', block, re.IGNORECASE)
            duration = re.search(r'class=["\']short-time["\'][^>]*>([^<]+)', block, re.IGNORECASE)
            if not link:
                continue
            title = self._clean(link.group(2))
            if not title:
                continue
            info = {"title": title, "plot": title}
            duration_text = self._clean(duration.group(1)) if duration else ""
            if duration_text:
                info["duration"] = self.convert_duration(duration_text)
            items.append({
                "title": title + (" [COLOR lime]({})[/COLOR]".format(duration_text) if duration_text else ""),
                "url": self._absolute(link.group(1)),
                "thumb": self._thumbnail(image.group(1)) if image else self.icon,
                "info": info,
            })
        return items

    def process_content(self, url, page=1):
        url = self.base_url if not url or url == "BOOTSTRAP" else url
        page_html = self._get(self._page_url(url, page), referer=self.base_url)
        if not page_html:
            self.notify_error("Could not load CzechVideo content")
            self.end_directory("videos")
            return
        if page == 1:
            self.add_dir("Search", "", 5, self.icons.get("search", self.icon))
            self.add_dir("Categories", "CZECH_CATEGORIES", 8, self.icons.get("categories", self.icon))
        items = self._videos(page_html)
        for item in items:
            self.add_link(item["title"], item["url"], 4, item["thumb"], self.fanart, info_labels=item["info"])
        nav = re.search(r'<div\b[^>]+class=["\']navigation["\'][^>]*>([\s\S]*?)</div>', page_html, re.IGNORECASE)
        if nav and re.search(r'(?:list_submit\({}\)|/page/{}/)'.format(page + 1, page + 1), nav.group(1), re.IGNORECASE):
            self.add_dir("Next Page", url, 2, self.icons.get("default", self.icon), page=page + 1)
        self.end_directory("videos")

    def process_categories(self, url):
        page_html = self._get(self.base_url)
        aside = re.search(r'<aside\b[^>]+class=["\'][^"\']*aside-1[^"\']*["\'][^>]*>([\s\S]*?)</aside>', page_html or "", re.IGNORECASE)
        seen = set()
        for target, label in re.findall(r'<a\b[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', aside.group(1) if aside else "", re.IGNORECASE):
            target = self._absolute(target)
            label = self._clean(label)
            if target not in seen and label and target != self.base_url:
                seen.add(target)
                self.add_dir(label, target, 2, self.icons.get("categories", self.icon))
        self.end_directory("videos")

    def search(self, query):
        if query:
            self.process_content(self.search_url.format(urllib.parse.quote_plus(query.strip())))

    def resolve_recording_stream(self, url):
        page_html = self._get(url, referer=self.base_url)
        links = [
            self._absolute(link, url) for link in re.findall(r'<iframe\b[^>]+src=["\']([^"\']+)', page_html or "", re.IGNORECASE)
            if any(host in link.lower() for host in ("playmogo", "dood", "myvidplay", "dsvplay"))
        ]
        for link in links:
            stream_url, headers = resolver.resolve(link, referer=url, headers={"User-Agent": self.ua})
            if stream_url:
                return {"url": stream_url, "headers": headers or {}, "extension": "mp4"}
        return None

    def play_video(self, url):
        WordPressApiTube._play_resolved(self, self.resolve_recording_stream(url))
