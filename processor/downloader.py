#!/usr/bin/env python3
import os
import shutil
import tempfile

from commons.log import log

from .processor import Processor
from tools.utils.utils import create_filename, load_metadata
from commons.util import download_file, exists


class Downloader(Processor):
    """
        Preprocessor for splitting original videos
    """
    def __init__(self, argv=None):
        super().__init__('download', argv)
        self.metadata_file = self.args.metadata_file
        self.metadata_url = self.args.download['metadata_url']
        self.url = self.args.download['url']
        self.file_pattern = self.args.download['file_pattern']

    def start(self):
        self.start_download()

    def start_download(self):
        # Example: http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime/<session>/scene<scene#>-camera<camera#>.mov
        nrows = None

        if self.args.debug:
            nrows = self.args.debug_opts['download_items']

        # Load metadata:
        log("Loading metadata...", 1)  # FIXME: print_log
        metadata = load_metadata(self.metadata_file, self.metadata_url,
                                 ['Session', 'Scene'], nrows)

        if metadata.empty:
            log("Nothing to download.", 1)  # FIXME: print_log
        else:
            # Download files:
            log(f"Source URL: '{self.url}'")  # FIXME: print_log
            log(f"Downloading files to '{self.output_dir}'..."
                )  # FIXME: print_log
            self.download_files_in_metadata(
                metadata, self.url, self.output_dir)  # FIXME: print_log
            log("Download complete.", 1)  # FIXME: print_log

    def download_files_in_metadata(self, metadata, url, output_dir):
        for row in metadata.itertuples():
            if row.Session and row.Scene:
                # Download 'camera 1' (front) view:
                src_filename = create_filename(self.file_pattern, row.Session,
                                               row.Scene, 1)

                # TODO: Download 'camera 2' (side) view:
                # src_filename = create_filename(self.file_pattern, row.Session,
                #                                row.Scene, 2)

                tgt_filename = src_filename.replace('/', '_')
                tgt_file = f"{output_dir}/{tgt_filename}"

                if not exists(tgt_file):
                    src_url = f"{url}/{src_filename}"
                    tmp_file = f"{tempfile.gettempdir()}/{tgt_filename}"
                    # Download file:
                    log(f"* {src_filename} ...", 1)
                    success = download_file(src_url, tmp_file)

                    if success:
                        # Save file to directory:
                        shutil.move(tmp_file, tgt_file)
