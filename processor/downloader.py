#!/usr/bin/env python3
import shutil
import tempfile
from itertools import product

from commons.log import log, log_progress
from commons.util import download_file, extension, filename, is_downloadable
from utils import create_filename

from .processor import Processor


class Downloader(Processor):
    """
        Preprocessor for splitting original videos
    """

    FORMAT_PRIORITIES = ["mov", "vid"]

    def __init__(self, args=None):
        super().__init__('download', args)
        self.url = self.get_arg("url")

    def run(self, group, rows):
        """
        Example: http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime/
        <session>/scene<scene#>-camera<camera#>.mov
        """
        if group:
            self.download_files_in_metadata(group, self.url,
                                            self.get_cameras(),
                                            self.output_dir)

    def download_files_in_metadata(self, group, urls, cameras, output_dir):
        tempdir = tempfile.gettempdir()
        total = len(cameras)

        for idx, (session, scene) in enumerate([group]):
            if session and scene:
                fmt, cam_urls = self.select_format_to_download(
                    session, scene, urls, cameras)

                for cam, url in cam_urls.items():
                    tgt_file = create_filename(session_or_sign=session,
                                               scene=scene,
                                               camera=cam,
                                               dir=output_dir,
                                               ext=fmt)
                    log_progress(idx + 1, total, filename(tgt_file))

                    if self.output_exists(tgt_file):
                        self.log_skipped()
                    else:
                        # Download file:
                        tmp_file = create_filename(session_or_sign=session,
                                                   scene=scene,
                                                   camera=cam,
                                                   dir=tempdir,
                                                   ext=fmt)

                        log(f"    Downloading '{url}'...", 2)
                        success, e = download_file(url, tmp_file, True)

                        if success:
                            # Save file to directory:
                            shutil.move(tmp_file, tgt_file)
                        else:
                            self.log_failed(e)

    def create_source_url(self, url, session, scene, camera):
        return url.format(session=session, scene=int(scene), camera=camera)

    def select_format_to_download(self, session, scene, urls, cameras):
        for fmt in self.FORMAT_PRIORITIES:
            cam_urls = {cam: self.create_source_url(urls[fmt],
                                                    session=session,
                                                    scene=scene,
                                                    camera=cam) for cam in cameras}
            if all([is_downloadable(url) for url in cam_urls.values()]):
                return fmt, cam_urls
        return None
