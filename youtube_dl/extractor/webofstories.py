# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import int_or_none


class WebOfStoriesIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?webofstories\.com/play/(?:[^/]+/)?(?P<id>[0-9]+)'
    _VIDEO_DOMAIN = 'http://eu-mobile.webofstories.com/'
    _GREAT_LIFE_STREAMER = 'rtmp://eu-cdn1.webofstories.com/cfx/st/'
    _USER_STREAMER = 'rtmp://eu-users.webofstories.com/cfx/st/'
    _TESTS = [
        {
            'url': 'http://www.webofstories.com/play/hans.bethe/71',
            'md5': '373e4dd915f60cfe3116322642ddf364',
            'info_dict': {
                'id': '4536',
                'ext': 'mp4',
                'title': 'The temperature of the sun',
                'thumbnail': 're:^https?://.*\.jpg$',
                'description': 'Hans Bethe talks about calculating the temperature of the sun',
                'duration': 238,
            }
        },
        {
            'url': 'http://www.webofstories.com/play/55908',
            'md5': '2985a698e1fe3211022422c4b5ed962c',
            'info_dict': {
                'id': '55908',
                'ext': 'mp4',
                'title': 'The story of Gemmata obscuriglobus',
                'thumbnail': 're:^https?://.*\.jpg$',
                'description': 'Planctomycete talks about The story of Gemmata obscuriglobus',
                'duration': 169,
            }
        },
    ]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)
        description = self._html_search_meta('description', webpage)
        thumbnail = self._og_search_thumbnail(webpage)

        embed_params = [s.strip(" \r\n\t'") for s in self._search_regex(
            r'(?s)\$\("#embedCode"\).html\(getEmbedCode\((.*?)\)',
            webpage, 'embed params').split(',')]

        (
            _, speaker_id, story_id, story_duration,
            speaker_type, great_life, _thumbnail, _has_subtitles,
            story_filename, _story_order) = embed_params

        is_great_life_series = great_life == 'true'
        duration = int_or_none(story_duration)

        # URL building, see: http://www.webofstories.com/scripts/player.js
        ms_prefix = ''
        if speaker_type.lower() == 'ms':
            ms_prefix = 'mini_sites/'

        if is_great_life_series:
            mp4_url = '{0:}lives/{1:}/{2:}.mp4'.format(
                self._VIDEO_DOMAIN, speaker_id, story_filename)
            rtmp_ext = 'flv'
            streamer = self._GREAT_LIFE_STREAMER
            play_path = 'stories/{0:}/{1:}'.format(
                speaker_id, story_filename)
        else:
            mp4_url = '{0:}{1:}{2:}/{3:}.mp4'.format(
                self._VIDEO_DOMAIN, ms_prefix, speaker_id, story_filename)
            rtmp_ext = 'mp4'
            streamer = self._USER_STREAMER
            play_path = 'mp4:{0:}{1:}/{2}.mp4'.format(
                ms_prefix, speaker_id, story_filename)

        formats = [{
            'format_id': 'mp4_sd',
            'url': mp4_url,
        }, {
            'format_id': 'rtmp_sd',
            'page_url': url,
            'url': streamer,
            'ext': rtmp_ext,
            'play_path': play_path,
        }]

        self._sort_formats(formats)

        return {
            'id': story_id,
            'title': title,
            'formats': formats,
            'thumbnail': thumbnail,
            'description': description,
            'duration': duration,
        }


class WebOfStoriesPlaylistIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?webofstories\.com/playAll/(?P<id>[^/]+)'
    _TESTS = []

    def _real_extract(self, url):
        playlist_id = self._match_id(url)

        webpage = self._download_webpage(url, playlist_id)

        entries = [
            self.url_result('http://www.webofstories.com/play/%s' % video_number, 'WebOfStories')
            for video_number in set(re.findall('href="/playAll/%s\?sId=(\d+)"' % playlist_id, webpage))
        ]

        title = self._html_search_regex(
            r'<title>([^<]+)\s*-\s*Web\sof\sStories</title>', webpage, 'title')

        description = self._html_search_meta(
            'description', webpage, 'description')

        return self.playlist_result(entries, playlist_id, title, description)
