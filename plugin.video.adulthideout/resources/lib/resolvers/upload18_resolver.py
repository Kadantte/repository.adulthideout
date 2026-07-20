# -*- coding: utf-8 -*-
import html
import re

import requests
import xbmc

from resources.lib.resolvers import resolver_utils


def resolve(url, referer=None, headers=None):
    request_headers = dict(headers or {})
    request_headers.update({
        "User-Agent": request_headers.get("User-Agent") or resolver_utils.get_ua(),
        "Referer": referer or url,
        "Accept-Encoding": "identity",
    })
    try:
        response = requests.get(url, headers=request_headers, timeout=20)
        response.raise_for_status()
        match = re.search(r'\bm3u8\s*:\s*["\']([^"\']+)', response.text, re.I)
        if not match:
            return None, {}
        stream = html.unescape(match.group(1)).replace("\\/", "/")
        xbmc.log("[AdultHideout][upload18] HLS stream resolved", xbmc.LOGINFO)
        return stream, {
            "User-Agent": request_headers["User-Agent"],
            "Referer": url,
        }
    except Exception as exc:
        xbmc.log("[AdultHideout][upload18] Resolve failed: {}".format(exc), xbmc.LOGERROR)
        return None, {}
