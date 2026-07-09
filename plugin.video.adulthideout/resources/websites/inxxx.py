#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib.parse

from resources.lib.kvs_tube import KVSTubeWebsite


class InXXX(KVSTubeWebsite):
    label = "InXXX"
    sort_options = ["Most Viewed", "Top Rated"]
    sort_paths = {
        "Most Viewed": "/",
        "Top Rated": "/top-rated/",
    }
    search_path = "/s/{}/"
    categories_path = "/categories/"
    models_path = None
    video_path_markers = ("/v/",)
    category_path_markers = ("/categories/", "/tags/")
    next_page_full_count = 40
    use_playback_proxy = True
    # Only the 480p video_url is freely playable; the HD video_alt_url redirects to
    # a login wall, so prefer the default stream instead of the highest alt url.
    prefer_default_stream = True

    def __init__(self, addon_handle, addon=None):
        super().__init__(
            name="inxxx",
            base_url="https://www.inxxx.com/",
            search_url="https://www.inxxx.com/s/{}/",
            addon_handle=addon_handle,
            addon=addon,
        )
        self.icon = os.path.join(self.addon.getAddonInfo("path"), "resources", "logos", "inxxx.png")
        self.icons["default"] = self.icon

    def _is_top_listing(self, url):
        parsed = urllib.parse.urlparse(url or self.base_url)
        return parsed.path.rstrip("/") in ("", "/top-rated")

    def get_page_url(self, base_url, page_num):
        parsed = urllib.parse.urlparse(base_url or self.base_url)
        if page_num > 1 and not parsed.path.strip("/"):
            return urllib.parse.urljoin(self.base_url, "best/{}/".format(page_num))
        return super().get_page_url(base_url, page_num)

    def _pick_thumb(self, img_tag):
        # InXXX exposes a real JPEG in src but a webp (disguised as .jpg) in
        # data-webp, which Kodi's texture loader cannot decode. Prefer src.
        src_match = re.search(r'\ssrc=["\']([^"\']+)["\']', img_tag, re.IGNORECASE)
        if src_match:
            thumb = self._absolute(src_match.group(1))
            if not thumb.startswith("data:image/"):
                return self._thumb_with_headers(thumb)
        return self._thumb_with_headers(super()._pick_thumb(img_tag))

    def _thumb_with_headers(self, thumb):
        if not thumb or not thumb.startswith("http") or "|" in thumb:
            return thumb
        return "{}|User-Agent={}&Referer={}".format(
            thumb,
            urllib.parse.quote(self.ua),
            urllib.parse.quote(self.base_url),
        )
