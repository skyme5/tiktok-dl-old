usage: tiktok-dl [-h] [-a ARCHIVE_LOCATION] [-f FILENAME] [-o OUTPUT_TEMPLATE]
                 [-P DIRECTORY-PREFIX] [--no-metadata-json NO_METADATA_JSON]
                 [URL [URL ...]]

TikTok Video downloader

positional arguments:
  URL                   URL of the video

optional arguments:
  -h, --help            show this help message and exit
  -a ARCHIVE_LOCATION, --archive-location ARCHIVE_LOCATION
                        Download only videos not listed in the archive file.
                        Record the IDs of all downloaded videos in it.
  -f FILENAME, --filename FILENAME
                        Path to a file containing a list of urls to download
  -o OUTPUT_TEMPLATE, --output OUTPUT_TEMPLATE
                        Output filename template, see the "OUTPUT TEMPLATE"
                        for all the info.
  -P DIRECTORY-PREFIX, --directory-prefix DIRECTORY-PREFIX
                        Prefix path to filenames.
  --no-metadata-json NO_METADATA_JSON
                        Do not create a JSON file containing the metadata of
                        each video.
