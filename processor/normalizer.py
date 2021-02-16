#!/usr/bin/env python3
from itertools import product

from commons.log import log, log_progress
from commons.util import exists
from commons.util.io_util import (create_if_missing, delete_file, directory,
                                  normpath, read_json, save_json)
from constant import PARTS_OPENPOSE_MAPPING
from utils import create_filename

from .processor import Processor


class Normalizer(Processor):
    """
        Preprocessor for normalizing skeleton coordinates
    """
    COORDS_MODE = {
        "2d": ["x", "y"],
        "3d": ["x", "y", "z"]
    }

    def __init__(self, args=None):
        super().__init__('normalize', args)
        self.mode = self.get_arg("mode")

    def run(self, group, rows):
        if not rows.empty:
            self.process_normalization(
                rows, self.mode, self.input_dir, self.output_dir)

    def process_normalization(self, rows, modes, input_dir, output_dir):
        rows_modes = product(rows.itertuples(), modes)
        total = len(rows.index) * len(modes)

        for row_idx, (row, mode) in enumerate(rows_modes):
            src_path = create_filename(base=row.basename,
                                       dir=normpath(f"{input_dir}/{mode}"),
                                       ext="json")
            tgt_path = create_filename(base=row.basename,
                                       dir=normpath(
                                           f"{output_dir}/{mode}"),
                                       ext="json")

            log_progress(row_idx + 1, total, f"{row.basename} ({mode})")

            if not exists(src_path) or self.output_exists(tgt_path):
                self.log_skipped()
            else:
                log("    Normalizing...")
                data = read_json(src_path)

                try:
                    # Normalize and save data:
                    data["frames"] = [self.normalize_frame(
                        frame, mode) for frame in data["frames"]]
                    create_if_missing(directory(tgt_path))
                    save_json(data, tgt_path)
                except Exception as e:
                    self.log_failed(e)
                    delete_file(tgt_path)

    def normalize_frame(self, frame, mode):
        ref_distance = self.get_ref_distance(frame, mode)

        for part in PARTS_OPENPOSE_MAPPING.values():
            if isinstance(frame[part], dict):
                for coord in self.COORDS_MODE[mode]:
                    if coord in frame[part]:
                        frame[part][coord] = list(
                            frame[part][coord] / ref_distance)
        return frame

    def get_ref_distance(self, frame, mode):
        """
        Calculate distance of reference, based on the distance between
        shoulders.
        """
        from commons.model import Coordinate

        def get_coordinate(part, mode, idx, name):
            coords = self.COORDS_MODE[mode]
            x = part["x"][idx] if ("x" in coords) else 0
            y = part["y"][idx] if ("y" in coords) else 0
            z = part["z"][idx] if ("z" in coords) else 0
            return Coordinate(x, y, z, part["score"][idx], name=name)

        # Find indexes:
        body = frame["body"]
        idx_neck = body["name"].index("neck")
        idx_left_shoulder = body["name"].index("shoulder_left")
        idx_right_shoulder = body["name"].index("shoulder_right")

        # Find neck:
        neck = get_coordinate(body, mode, idx_neck, "neck")
        if neck.is_zero():
            raise Exception("Could not find `neck` for normalizing skeleton.")

        # Find a valid shoulder:
        left_shoulder = get_coordinate(
            body, mode, idx_left_shoulder, "left_shoulder")
        right_shoulder = get_coordinate(
            body, mode, idx_right_shoulder, "right_shoulder")

        if not left_shoulder.is_zero():
            shoulder = left_shoulder
        elif not right_shoulder.is_zero():
            shoulder = right_shoulder
        else:
            raise Exception(
                "Could not find a `shoulder` for normalizing skeleton.")

        # Calculate distance:
        return neck.dist_to(shoulder)
