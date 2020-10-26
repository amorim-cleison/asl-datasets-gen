#!/usr/bin/env python3
import shutil
import tempfile

from commons.log import log, log_progress

from .processor import Processor
from tools.utils.utils import create_video_name
from commons.util import download_file, exists, filename
from itertools import product


class Downloader(Processor):
    """
        Preprocessor for splitting original videos
    """
    def __init__(self, args=None):
        super().__init__('download', args)
        self.url = self.get_phase_arg("url")

    def start(self):
        self.start_download()

    def start_download(self):
        """
        Example: http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime/
        <session>/scene<scene#>-camera<camera#>.mov
        """
        nrows = self.get_debug_arg(
            "download_items") if self.is_debug() else None

        # Load metadata:
        log("Loading metadata...", 1)
        metadata_rows = self.load_metadata(['Session', 'Scene'], nrows)

        if metadata_rows.empty:
            log("Nothing to download.", 1)
        else:
            # Download files:
            log(f"Saving files to folder '{self.output_dir}'...")

            self.download_files_in_metadata(metadata_rows, self.url,
                                            self.get_cameras(),
                                            self.output_dir)
            log("Download complete.", 1)

    def download_files_in_metadata(self, metadata, url, cameras, output_dir):
        tempdir = tempfile.gettempdir()
        files = product(metadata.itertuples(), cameras)
        total = len(metadata.index) * len(cameras)

        for idx, (row, cam) in enumerate(files):
            if row.Session and row.Scene:
                tgt_file = create_video_name(row.Session,
                                             scene=row.Scene,
                                             camera=cam,
                                             dir=output_dir)
                log_progress(idx + 1, total, filename(tgt_file, True))

                if not exists(tgt_file):
                    # Download file:
                    src_url = self.create_source_url(url,
                                                     session=row.Session,
                                                     scene=row.Scene,
                                                     camera=cam)
                    tmp_file = create_video_name(row.Session,
                                                 scene=row.Scene,
                                                 camera=cam,
                                                 dir=tempdir)

                    log(f"    Downloading from '{src_url}'...", 2)
                    success, err = download_file(src_url, tmp_file)

                    if success:
                        # Save file to directory:
                        shutil.move(tmp_file, tgt_file)
                    else:
                        log(f"    FAILED ({err})", 2)

    def create_source_url(self, url, session, scene, camera):
        return url.format(session=session, scene=int(scene), camera=camera)
