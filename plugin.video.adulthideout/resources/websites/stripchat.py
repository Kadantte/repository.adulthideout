# -*- coding: utf-8 -*-
import base64
import html
import json
import os
import urllib.parse

import requests
import xbmcgui
import xbmcplugin

from resources.lib.base_website import BaseWebsite


class StripchatWebsite(BaseWebsite):
    API_URL = "https://stripchat.com/api/external/v4/widget"
    LIST_PREFIX = "STRIPCHAT_LIST:"
    PLAY_PREFIX = "STRIPCHAT_PLAY:"
    PAGE_SIZE = 40

    def __init__(self, addon_handle, addon=None):
        super().__init__(
            name="stripchat",
            base_url="https://stripchat.com/",
            search_url="STRIPCHAT_SEARCH:{}",
            addon_handle=addon_handle,
            addon=addon,
        )
        self.session = requests.Session()
        self.ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
        self.icon = os.path.join(self.addon.getAddonInfo("path"), "resources", "logos", "stripchat.png")
        self.icons["default"] = self.icon

    def _headers(self, referer=None, accept="application/json, text/plain, */*"):
        return {
            "User-Agent": self.ua,
            "Accept": accept,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
            "Referer": referer or self.base_url,
            "Origin": "https://stripchat.com",
        }

    def _request_models(self, limit, offset=0):
        try:
            response = self.session.get(
                self.API_URL,
                params={"limit": int(limit), "offset": int(offset)},
                headers=self._headers(),
                timeout=20,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("models") or [], int(data.get("total") or 0)
            self.logger.warning("[Stripchat] API HTTP %s", response.status_code)
        except (ValueError, TypeError, requests.RequestException) as exc:
            self.logger.warning("[Stripchat] API request failed: %s", exc)
        return [], 0

    @staticmethod
    def _matches_filter(model, filter_name):
        if filter_name == "all":
            return True
        gender = str(model.get("gender") or "").lower()
        broadcast = str(model.get("broadcastGender") or "").lower()
        if filter_name == "female":
            return broadcast == "female" and "tranny" not in gender
        if filter_name == "couples":
            return broadcast == "group" and "tranny" not in gender
        if filter_name == "trans":
            return broadcast == "trans" or "tranny" in gender or "trans" in gender
        if filter_name == "german":
            return "de" in (model.get("languages") or [])
        if filter_name == "hd":
            return bool(model.get("broadcastHD"))
        return True

    def _filtered_models(self, filter_name, page):
        if filter_name == "all":
            return self._request_models(self.PAGE_SIZE, (page - 1) * self.PAGE_SIZE)

        # The public widget API exposes a mixed feed. Fetch a bounded window and
        # apply its documented model metadata locally for deterministic filters.
        models = []
        total = 0
        for offset in range(0, 1000, 200):
            batch, total = self._request_models(200, offset)
            models.extend(model for model in batch if self._matches_filter(model, filter_name))
            if len(batch) < 200:
                break
        start = (page - 1) * self.PAGE_SIZE
        return models[start : start + self.PAGE_SIZE], len(models)

    def _stream_url(self, model):
        stream = model.get("stream") or {}
        urls = stream.get("urls") or {}
        return urls.get("original") or urls.get("720p") or urls.get("480p") or stream.get("url") or ""

    def _thumbnail(self, model):
        thumb = (
            model.get("previewUrlThumbBig")
            or model.get("popularSnapshotUrl")
            or model.get("snapshotUrl")
            or model.get("avatarUrl")
            or self.icon
        )
        if thumb.startswith("//"):
            thumb = "https:" + thumb
        if thumb.startswith("http"):
            return "{}|User-Agent={}&Referer={}".format(
                thumb,
                urllib.parse.quote(self.ua),
                urllib.parse.quote(self.base_url),
            )
        return thumb

    def _play_token(self, model):
        payload = {
            "username": model.get("username") or "",
            "url": self._stream_url(model),
        }
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return self.PLAY_PREFIX + base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    def _add_model(self, model):
        username = html.unescape(str(model.get("username") or "")).strip()
        stream_url = self._stream_url(model)
        if not username or not stream_url or model.get("status") not in (None, "public"):
            return False
        viewers = int(model.get("viewersCount") or 0)
        languages = ", ".join((model.get("languages") or [])[:4])
        topic = html.unescape(str(model.get("topic") or "")).strip()
        label = username
        if viewers:
            label += " [COLOR lime]({} viewers)[/COLOR]".format(viewers)
        plot = topic or username
        if languages:
            plot += "\nLanguages: {}".format(languages)
        self.add_link(
            label,
            self._play_token(model),
            4,
            self._thumbnail(model),
            self.fanart,
            info_labels={"title": username, "plot": plot, "genre": "Live Cam"},
        )
        return True

    def get_start_url_and_label(self):
        return self.LIST_PREFIX + "all", "Stripchat"

    def process_content(self, url, page=1):
        if not url or url == "BOOTSTRAP":
            url = self.LIST_PREFIX + "all"
        filter_name = url.split(":", 1)[1] if url.startswith(self.LIST_PREFIX) else "all"

        if page == 1:
            self.add_dir("Search", "", 5, self.icons.get("search", self.icon))
            self.add_dir("Categories", self.name, 8, self.icons.get("categories", self.icon))

        models, total = self._filtered_models(filter_name, page)
        added = sum(1 for model in models if self._add_model(model))
        if page * self.PAGE_SIZE < total:
            self.add_dir("Next Page", url, 2, self.icon, page=page + 1)
        if not added:
            self.notify_error("No public Stripchat rooms found")
        self.end_directory("videos")

    def process_categories(self, url):
        for label, filter_name in (
            ("All Public Rooms", "all"),
            ("Female", "female"),
            ("Couples and Groups", "couples"),
            ("Trans", "trans"),
            ("German Speaking", "german"),
            ("HD Rooms", "hd"),
        ):
            self.add_dir(label, self.LIST_PREFIX + filter_name, 2, self.icon)
        self.end_directory("videos")

    def search(self, query):
        query = (query or "").strip().lower()
        if not query:
            return
        matches = []
        for offset in range(0, 1000, 200):
            batch, _ = self._request_models(200, offset)
            for model in batch:
                haystack = " ".join((
                    str(model.get("username") or ""),
                    str(model.get("topic") or ""),
                    " ".join(model.get("languages") or []),
                )).lower()
                if query in haystack:
                    matches.append(model)
            if len(batch) < 200:
                break
        for model in matches[:100]:
            self._add_model(model)
        if not matches:
            self.notify_error("No matching public Stripchat rooms found")
        self.end_directory("videos")

    def _decode_play_token(self, value):
        token = value[len(self.PLAY_PREFIX) :]
        token += "=" * (-len(token) % 4)
        try:
            return json.loads(base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8"))
        except (ValueError, TypeError):
            return {}

    def play_video(self, url):
        payload = self._decode_play_token(url) if url.startswith(self.PLAY_PREFIX) else {}
        stream_url = payload.get("url") or ""
        username = payload.get("username") or ""
        if not stream_url:
            self.notify_error("Stripchat room is no longer public")
            xbmcplugin.setResolvedUrl(self.addon_handle, False, xbmcgui.ListItem())
            return

        headers = self._headers(self.base_url + urllib.parse.quote(username), accept="*/*")
        encoded_headers = urllib.parse.urlencode(headers)
        item = xbmcgui.ListItem(path=stream_url + "|" + encoded_headers)
        item.setProperty("IsPlayable", "true")
        item.setMimeType("application/vnd.apple.mpegurl")
        item.setContentLookup(False)
        item.setProperty("inputstream", "inputstream.adaptive")
        item.setProperty("inputstream.adaptive.manifest_type", "hls")
        item.setProperty("inputstream.adaptive.manifest_headers", encoded_headers)
        item.setProperty("inputstream.adaptive.stream_headers", encoded_headers)
        xbmcplugin.setResolvedUrl(self.addon_handle, True, item)
