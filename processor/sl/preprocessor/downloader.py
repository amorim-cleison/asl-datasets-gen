#!/usr/bin/env python3
import os
import shutil
import tempfile

from commons.log import log

from .preprocessor import Preprocessor
from tools.utils.utils import create_filename

class Downloader(Preprocessor):
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
        metadata = self.load_metadata(self.metadata_file, self.metadata_url,
                                      ['Session', 'Scene'], nrows)

        if metadata.empty:
            log("Nothing to download.", 1)  # FIXME: print_log
        else:
            # Download files:
            log("Source URL: '{}'".format(self.url))  # FIXME: print_log
            log("Downloading files to '{}'...".format(
                self.output_dir))  # FIXME: print_log
            self.download_files_in_metadata(
                metadata, self.url, self.output_dir)  # FIXME: print_log
            log("Download complete.", 1)  # FIXME: print_log

    def download_files_in_metadata(self, metadata, url, output_dir):
        for row in metadata.itertuples():
            if row.Session and row.Scene:
                src_filename = create_filename(self.file_pattern, row.Session, row.Scene)
                tgt_filename = src_filename.replace('/', '_')
                tgt_file = '{}/{}'.format(output_dir, tgt_filename)

                if not os.path.isfile(tgt_file):
                    src_url = '{}/{}'.format(url, src_filename)
                    tmp_file = '{}/{}'.format(tempfile.gettempdir(),
                                              tgt_filename)
                    # Download file:
                    log("* {} ...".format(src_filename), 1)
                    success = self.download_file(src_url, tmp_file)

                    if success:
                        # Save file to directory:
                        shutil.move(tmp_file, tgt_file)
