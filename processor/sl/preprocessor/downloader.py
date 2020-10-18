#!/usr/bin/env python3
import math
import os
import shutil
import subprocess
import tempfile
# from urllib import request

from .preprocessor import Preprocessor


class Downloader_Preprocessor(Preprocessor):
    """
        Preprocessor for splitting original videos
    """

    def __init__(self, argv=None):
        super().__init__('download', argv)
        self.url = self.arg.download['url']

    def start(self):
        self.start_download()

    def start_download(self):
        # Example: http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime/<session>/scene<scene#>-camera<camera#>.mov
        nrows = None

        if self.arg.debug:
            nrows = self.arg.debug_opts['download_items']

        # Load metadata:
        self.print_log("Loading metadata...")
        metadata = self.load_metadata(['Session', 'Scene'], nrows)

        if metadata.empty:
            self.print_log("Nothing to download.")
        else:
            # Download files:
            self.print_log("Source URL: '{}'".format(self.url))
            self.print_log("Downloading files to '{}'...".format(self.output_dir))
            self.ensure_dir_exists(self.output_dir)
            self.download_files_in_metadata(metadata, self.url, self.output_dir)
            self.print_log("Download complete.")

    def download_files_in_metadata(self, metadata, url, output_dir):
        for row in metadata.itertuples():
            if row.Session and row.Scene:
                src_filename = self.format_filename(row.Session, row.Scene)
                tgt_filename = src_filename.replace('/', '_')
                tgt_file = '{}/{}'.format(output_dir, tgt_filename)

                if not os.path.isfile(tgt_file):
                    src_url = '{}/{}'.format(url, src_filename)
                    tmp_file = '{}/{}'.format(tempfile.gettempdir(),
                                            tgt_filename)
                    # Download file:
                    self.print_log("* {} ...".format(src_filename))
                    success = self.download_file(src_url, tmp_file)

                    if success:
                        # Save file to directory:
                        shutil.move(tmp_file, tgt_file)

