# -*- coding: utf-8 -*-

from resources.lib.playtube_website import PlayTubeWebsite


class HQFap(PlayTubeWebsite):
    skip_directory_titles = {"3d"}

    def __init__(self, addon_handle, addon=None):
        super().__init__("hqfap", "HQFap", "https://hqfap.com/", addon_handle, addon)
