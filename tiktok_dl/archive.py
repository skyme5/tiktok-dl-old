import os


class ArchiveManager:
    def __init__(self, download_archive=None):
        self.download_archive = download_archive
        self.is_init = False
        self.archive = self._read_archive()

    def _read_archive(self):
        if os.path.isfile(self.download_archive):
            with open(self.download_archive) as f:
                data = f.read()
            return data.split("\n")
        return list()

    def _write_archive(self, items: list):
        with open(self.download_archive, "a", encoding="utf-8") as f:
            for video_id in items:
                f.write("%s\n" % video_id)

    def exist(self, video_id: str):
        return video_id in self.archive

    def append(self, video_id):
        self._write_archive(list(video_id))