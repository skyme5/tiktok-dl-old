import json
import os
import re
import time

import requests
import urllib3
from loguru import logger
from tiktok_dl.extractor import aweme_extractor
from tiktok_dl.schema import aweme_validate
from tiktok_dl.utils import (
    format_utctime,
    match_id,
    search_regex,
    try_get,
    valid_url_re,
)
from tiktok_dl.version import version


class URLExistsInArchive(Exception):
    pass


class Downloader:
    def __init__(
        self,
        directory_prefix=None,
        dump_json=False,
        get_url=False,
        max_sleep_interval=0,
        no_check_certificate=False,
        no_overwrite=False,
        no_warnings=False,
        no_write_json=False,
        output_template="{Y}-{d}-{m}_{H}-{M}-{S} {id}_{user_id}",
        print_json=False,
        quiet=False,
        simulate=False,
        skip_download=False,
        sleep_interval=0.2,
        verbose=True,
        write_description=False,
        write_thumbnail=True,
        urls=None,
    ):
        self.directory_prefix = directory_prefix
        self.dump_json = dump_json
        self.get_url = get_url
        self.max_sleep_interval = max_sleep_interval
        self.no_check_certificate = no_check_certificate
        self.no_overwrite = no_overwrite
        self.no_warnings = no_warnings
        self.no_write_json = no_write_json
        self.output_template = output_template
        self.print_json = print_json
        self.quiet = quiet
        self.simulate = simulate
        self.skip_download = skip_download
        self.sleep_interval = sleep_interval
        self.verbose = verbose
        self.write_description = write_description
        self.write_thumbnail = write_thumbnail
        self.urls = urls

        self.headers = {
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/83.0.4103.44 Safari/537.36"
            )
        }
        self.reaponse_ok = requests.codes.get("ok")
        # urllib3.disable_warnings()

    def _parse_json(self, json_string: str, video_id: str, fatal=True):
        try:
            return json.loads(json_string)
        except ValueError as ve:
            errmsg = "{}: Failed to parse JSON ".format(video_id)
            if fatal:
                raise Exception(errmsg, cause=ve)
            else:
                logger.error(errmsg + str(ve))

    def _download_webpage(self, url: str, video_id: str, note="Downloading webpage"):
        logger.debug("{} {}", note, video_id)
        r = requests.get(url, verify=False, headers=self.headers)
        return r.text

    def _fetch_data(self, url: str):
        video_id = match_id(url, valid_url_re)

        webpage = self._download_webpage(
            url, video_id, note="Downloading video webpage"
        )
        json_string = search_regex(
            r"id=\"__NEXT_DATA__\"\s+type=\"application\/json\"\s*[^>]+>\s*(?P<json_string_id>[^<]+)",
            webpage,
            "json_string",
            group="json_string_id",
        )
        json_data = self._parse_json(json_string, video_id)
        aweme_data = try_get(
            json_data, lambda x: x["props"]["pageProps"], expected_type=dict
        )

        if aweme_data.get("statusCode") != 0:
            raise FileNotFoundError("Video not available " + video_id)

        return {
            "video_data": aweme_extractor(video_data=aweme_data),
            "aweme_data": aweme_data,
            "tiktok-dl": version,
            "timestamp": int(time.time()),
        }

    def _expand_path(self, path):
        if self.directory_prefix is None:
            return path
        return os.path.join(self.directory_prefix, path)

    def _output_format(self, json_data: dict):
        def enhance_json_data(json_data):
            data = dict(json_data)
            timestamp = data.get("create_time")
            data["Y"] = format_utctime(time=timestamp, fmt="%Y")
            data["m"] = format_utctime(time=timestamp, fmt="%m")
            data["d"] = format_utctime(time=timestamp, fmt="%d")
            data["H"] = format_utctime(time=timestamp, fmt="%H")
            data["M"] = format_utctime(time=timestamp, fmt="%M")
            data["S"] = format_utctime(time=timestamp, fmt="%S")
            return data

        enhanced = enhance_json_data(json_data)
        return self.output_template.format(**enhanced)

    def _save_json(self, data: dict, dest: str):
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))

        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def _download_url(self, url: str, dest: str):
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest), exist_ok=True)

        try:
            if os.path.getsize(dest) == 0:
                os.remove(dest)
        except FileNotFoundError:
            pass

        try:
            with open(dest, "xb") as handle:
                response = requests.get(url, stream=True, timeout=160)
                if response.status_code != self.reaponse_ok:
                    response.raise_for_status()

                logger.debug("Downloading to {}".format(dest))
                for data in response.iter_content(chunk_size=4194304):
                    handle.write(data)
                handle.close()
        except FileExistsError:
            pass
        except requests.exceptions.RequestException:
            logger.error("File {} not found on Server {}".format(dest, url))
            pass

        if os.path.getsize(dest) == 0:
            os.remove(dest)

    def _download_media(self, video_data: dict, filepath: str):
        video_url = video_data["play_urls"][0]
        self._download_url(video_url, self._expand_path(filepath + ".mp4"))
        cover_url = video_data["thumbnails"][0]
        self._download_url(cover_url, self._expand_path(filepath + ".jpg"))

    def download(self, url: str):
        try:
            data = self._fetch_data(url)
            aweme_validate(data.get("video_data"))
            filepath = self._output_format(data.get("video_data"))
            self._download_media(data.get("video_data"), filepath)
            self._save_json(data, self._expand_path(filepath + ".json"))
        except requests.exceptions.InvalidURL as e:
            logger.error(e)
            pass
        except ConnectionError as e:
            logger.error(e)
            pass
        except re.error as e:
            logger.error(e)
            pass
        except FileNotFoundError as e:
            logger.warning(e)
            pass
