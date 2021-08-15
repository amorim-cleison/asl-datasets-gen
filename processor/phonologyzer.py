#!/usr/bin/env python3
from itertools import product
from os.path import normpath

import reader
from commons.log import log, log_progress
from commons.util import (create_if_missing, directory, exists, read_json,
                          save_json)
from extractor import PhonoExtactor
from utils import create_filename

from .processor import Processor


class Phonologyzer(Processor):
    """
        Preprocessor for parsing phonological attributes
    """
    def __init__(self, args=None):
        super().__init__('phonology', args)
        input_model = self.get_arg("input_model")
        self.model = input_model["model"]
        self.data_reader = getattr(reader, input_model["reader"])

    def run(self, group, rows):
        if not rows.empty:
            self.process_attributes(rows, self.modes, self.input_dir,
                                    self.output_dir, self.model,
                                    self.data_reader)

    def process_attributes(self, rows, modes, input_dir, output_dir, model,
                           data_reader):
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
                data = self.read_data(src_path, model, data_reader)
                data = self.extract_attributes(data, model)

                # Write output:
                create_if_missing(directory(tgt_path))
                save_json(data, tgt_path)

    def read_data(self, path, model, data_reader):
        person = 0
        content = read_json(path)
        reader = data_reader(content, model)
        return reader.get_data(person)

    def extract_attributes(self, data, model):
        extractor = PhonoExtactor(model)
        frames = data["frames"]
        last_frame = None

        for idx_frame, frame in enumerate(frames):
            frame["phono_attributes"] = extractor.extract_attributes(
                data, frame, idx_frame, len(frames), last_frame)
            del frame["skeleton"]
        return data
