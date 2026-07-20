# -*- coding: utf-8 -*-

from resources.lib.playtube_website import PlayTubeWebsite


class EightKPorner(PlayTubeWebsite):
    def __init__(self, addon_handle, addon=None):
        super().__init__("8kporner", "8KPorner", "https://8kporner.com/", addon_handle, addon)
