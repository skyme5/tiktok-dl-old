#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os

from loguru import logger
from tiktok_dl.downloader import Downloader
from tiktok_dl.utils import match_id, valid_url_re
from tiktok_dl.version import version


def main():
    parser = argparse.ArgumentParser(
        description="TikTok Video downloader",
        usage="Usage: tiktok-dl [options] URL [URL...]",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=version,
        help="Print program version and exit",
    )

    parser.add_argument(
        "urls", metavar="URL", nargs="*", type=str, help="URL of the video"
    )

    video_selection_group = parser.add_argument_group("Video Selection")
    video_selection_group.add_argument(
        "--download-archive",
        metavar="DOWNLOAD_ARCHIVE",
        type=str,
        dest="download_archive",
        default=None,
        help="Download only videos not listed in the archive file. "
        "Record the IDs of all downloaded videos in it.",
    )

    parallel_download_group = parser.add_argument_group("Parallel Download")
    parallel_download_group.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        dest="daemon",
        help="Run as daemon.",
    )
    parallel_download_group.add_argument(
        "-p",
        "--concurrent-count",
        metavar="CONCURRENT_COUNT",
        type=int,
        dest="concurrent_count",
        default=2,
        help="Download videos in parallel.",
    )

    filesystem_group = parser.add_argument_group("Filesystem Options")
    filesystem_group.add_argument(
        "-a",
        "--batch-file",
        metavar="FILENAME",
        type=str,
        dest="batch_file",
        default=None,
        help="File containing URLs to download ('-' for stdin), one URL per line. "
        "Lines starting with '#', ';' or ']' are considered as comments and ignored.",
    )
    filesystem_group.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT_TEMPLATE",
        type=str,
        dest="output_template",
        default="{Y}-{d}-{m}_{H}-{M}-{S} {id}_{user_id}",
        help='Output filename template, see the "OUTPUT TEMPLATE" for all the info.',
    )
    filesystem_group.add_argument(
        "-w",
        "--no-overwrites",
        action="store_true",
        dest="no_overwrite",
        default=False,
        help="Do not overwrite files",
    )
    filesystem_group.add_argument(
        "--write-description",
        action="store_true",
        dest="write_description",
        help="Write video description to a .description file.",
    )
    filesystem_group.add_argument(
        "--no-write-json",
        action="store_true",
        dest="no_write_json",
        default=False,
        help="Write video metadata to a .json file.",
    )
    filesystem_group.add_argument(
        "-P",
        "--directory-prefix",
        metavar="DIRECTORY_PREFIX",
        type=str,
        dest="directory_prefix",
        default=None,
        help="Directory prefix.",
    )

    thumbnail_group = parser.add_argument_group("Thumbnail images")
    thumbnail_group.add_argument(
        "--write-thumbnail",
        action="store_true",
        dest="write_thumbnail",
        default=True,
        help="Write thumbnail image to disk.",
    )

    simulation_group = parser.add_argument_group("Verbosity / Simulation Options:")
    simulation_group.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        default=False,
        help="Activate quiet mode.",
    )
    simulation_group.add_argument(
        "--no-warnings",
        action="store_true",
        dest="no_warnings",
        default=False,
        help="Ignore warnings.",
    )
    simulation_group.add_argument(
        "-s",
        "--simulate",
        action="store_true",
        dest="simulate",
        default=False,
        help="Do not download the video and do not write anything to disk.",
    )
    simulation_group.add_argument(
        "--skip-download",
        action="store_true",
        dest="skip_download",
        default=False,
        help="Do not download the video.",
    )
    simulation_group.add_argument(
        "-g",
        "--get-url",
        action="store_true",
        dest="get_url",
        default=False,
        help="Simulate, quiet but print URL.",
    )
    simulation_group.add_argument(
        "-j",
        "--dump-json",
        action="store_true",
        dest="dump_json",
        default=False,
        help="Simulate, quiet but print JSON information. "
        'See the "OUTPUT TEMPLATE" for a description of available keys.',
    )
    simulation_group.add_argument(
        "--print-json",
        action="store_true",
        dest="print_json",
        default=False,
        help="Be quiet and print the video information as JSON (video is still being downloaded).",
    )
    simulation_group.add_argument(
        "-v",
        "--verbose",
        action="store_false",
        dest="verbose",
        default=True,
        help="Print various debugging information.",
    )

    workarounds_group = parser.add_argument_group("Workarounds")
    workarounds_group.add_argument(
        "--no-check-certificate",
        action="store_true",
        dest="no_check_certificate",
        default=False,
        help="Suppress HTTPS certificate validation.",
    )
    workarounds_group.add_argument(
        "--sleep-interval",
        metavar="SLEEP_INTERVAL",
        type=float,
        dest="sleep_interval",
        default=0.2,
        help="Number of seconds to sleep before each download when used alone or "
        "a lower bound of a range for randomized sleep before each download "
        "(minimum possible number of seconds to sleep) when used along with "
        "--max-sleep-interval.",
    )
    workarounds_group.add_argument(
        "--max-sleep-interval",
        metavar="MAX_SLEEP_INTERVAL",
        type=float,
        dest="max_sleep_interval",
        default=0,
        help="Upper bound of a range for randomized sleep before each "
        "download (maximum possible number of seconds to sleep). "
        "Must only be used along with --min-sleep-interval.",
    )
    parser.set_defaults(
        batch_file=None,
        concurrent_count=1,
        daemon=False,
        directory_prefix=None,
        download_archive=None,
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
        urls=[],
        verbose=True,
        write_description=False,
        write_thumbnail=True,
    )

    args = parser.parse_args()

    if len(args.urls) == 0 and args.batch_file is None:
        parser.error("URL or file containing list of URLs (--batch-file) is required.")

    if args.batch_file is not None and os.path.isfile(args.batch_file):
        with open(args.batch_file, "r") as f:
            for url in f.read().split("\n"):
                if len(url.strip()) > 0:
                    args.urls.append(url.strip())

    logger.info('Downloading {} urls', len(args.urls))

    t = Downloader(
        directory_prefix=args.directory_prefix,
        dump_json=args.dump_json,
        get_url=args.get_url,
        max_sleep_interval=args.max_sleep_interval,
        no_check_certificate=args.no_check_certificate,
        no_overwrite=args.no_overwrite,
        no_warnings=args.no_warnings,
        no_write_json=args.no_write_json,
        output_template=args.output_template,
        print_json=args.print_json,
        quiet=args.quiet,
        simulate=args.simulate,
        skip_download=args.skip_download,
        sleep_interval=args.sleep_interval,
        verbose=args.verbose,
        write_description=args.write_description,
        write_thumbnail=args.write_thumbnail,
    )

    for url in args.urls:
        t.download(url)


if __name__ == "__main__":
    main()
