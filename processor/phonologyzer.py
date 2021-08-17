#!/usr/bin/env python3
from itertools import product
from os.path import normpath

from commons.log import log, log_progress
from commons.util import (create_if_missing, directory, exists, read_json,
                          save_json)
from constant import PARTS
from extractor import PhonoExtactor
from reader import AsllvdSkeletonReader
from utils import create_filename

from .processor import Processor


class Phonologyzer(Processor):
    """
        Preprocessor for parsing phonological attributes
    """
    def __init__(self, args=None):
        super().__init__('phonology', args)

    def run(self, group, rows):
        if not rows.empty:
            self.process_attributes(rows, self.modes, self.input_dir,
                                    self.output_dir)

    def process_attributes(self, rows, modes, input_dir, output_dir):
        rows_modes = product(rows.itertuples(), modes)
        total = len(rows.index) * len(modes)

        for row_idx, (row, mode) in enumerate(rows_modes):
            src_path = create_filename(base=row.basename,
                                       dir=normpath(f"{input_dir}/{mode}"),
                                       ext="json")
            tgt_path = create_filename(base=row.basename,
                                       dir=normpath(f"{output_dir}/{mode}"),
                                       ext="json")

            log_progress(row_idx + 1, total, f"{row.basename} ({mode})")

            if not exists(src_path) or self.output_exists(tgt_path):
                self.log_skipped()
            else:
                log("    Processing attributes...")
                data = self.read_data(src_path)
                data = self.extract_attributes(data)

                # Write output:
                create_if_missing(directory(tgt_path))
                save_json(data, tgt_path)

    def read_data(self, path, person=0):
        content = read_json(path)
        reader = AsllvdSkeletonReader(content, PARTS)
        return reader.get_data(person)

    def extract_attributes(self, data):
        extractor = PhonoExtactor()
        frames = data["frames"]
        total_frames = len(frames)
        last_skeleton = None

        for cur_index, frame in enumerate(frames):
            skeleton = frame["skeleton"]
            frame["phonology"] = extractor.extract_attributes(
                data, skeleton, last_skeleton, cur_index, total_frames)
            last_skeleton = skeleton
            del frame["skeleton"]
        return data
