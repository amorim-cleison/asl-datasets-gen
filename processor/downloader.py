#!/usr/bin/env python3
import shutil
import tempfile

from commons.log import log, log_progress
from commons.util import download_file, is_downloadable
from utils import create_filename, get_valid_cam_mode_mapping

from .processor import Processor


class Downloader(Processor):
    """
        Preprocessor for splitting original videos
    """

    def __init__(self, args=None):
        super().__init__('download', args)
        self.url = self.get_arg("url")
        self.formats = self.get_arg("format")

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

        for (session, scene) in [group]:
            if session and scene:
                cam_urls = self.select_format_to_download(
                    session, scene, urls, cameras)

                for idx, (cam, fmt_url) in enumerate(cam_urls.items()):
                    fmt = fmt_url["fmt"]
                    url = fmt_url["url"]
                    tgt_file = create_filename(session_or_sign=session,
                                               scene=scene,
                                               camera=cam,
                                               dir=output_dir,
                                               ext=fmt)
                    log_progress(idx + 1, total, f"...{url[-50:]}")

                    if self.output_exists(tgt_file):
                        self.log_skipped()
                    else:
                        # Download file:
                        tmp_file = create_filename(session_or_sign=session,
                                                   scene=scene,
                                                   camera=cam,
                                                   dir=tempdir,
                                                   ext=fmt)

                        log("    Downloading...", 2)
                        success, e = download_file(url, tmp_file, True)

                        if success:
                            # Save file to directory:
                            shutil.move(tmp_file, tgt_file)
                        else:
                            self.log_failed(e)

    def create_source_url(self, url, session, scene, camera):
        return url.format(session=session, scene=int(scene), camera=camera)

    def select_format_to_download(self, session, scene, urls, cameras):
        cam_urls = dict()

        for cam in cameras:
            for fmt in self.formats:
                url = self.create_source_url(urls[fmt],
                                             session=session,
                                             scene=scene,
                                             camera=cam)
                if is_downloadable(url):
                    cam_urls[cam] = {"fmt": fmt, "url": url}
                    break
        return get_valid_cam_mode_mapping(cam_urls, self.modes)
