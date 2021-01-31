#!/usr/bin/env python3
from commons.log import log, log_err, log_progress
from commons.util import exists, filename
from commons.util.io_util import (delete_file,
                                  read_json, save_json)
from constant import PARTS_OPENPOSE_MAPPING
from utils import create_filename

from .processor import Processor


class Normalizer(Processor):
    """
        Preprocessor for normalizing skeleton coordinates
    """

    def __init__(self, args=None):
        super().__init__('normalize', args)

    def run(self, metadata):
        if not metadata.empty:
            self.process_normalization(
                metadata, self.input_dir, self.output_dir)

    def process_normalization(self, metadata, input_dir, output_dir):
        total = len(metadata.index)

        for row_idx, row in enumerate(metadata.itertuples()):
            src_path = create_filename(session_or_sign=row.label,
                                       person=row.consultant,
                                       scene=row.scene,
                                       dir=input_dir,
                                       ext="json")
            tgt_path = create_filename(session_or_sign=row.label,
                                       person=row.consultant,
                                       scene=row.scene,
                                       dir=output_dir,
                                       ext="json")

            log_progress(row_idx + 1, total, filename(src_path))

            if not exists(src_path) or self.output_exists(tgt_path):
                self.log_skipped()
            else:
                data = read_json(src_path)

                try:
                    # Normalize and save data:
                    data["frames"] = [self.normalize_frame(
                        frame) for frame in data["frames"]]
                    save_json(data, tgt_path)
                except Exception as e:
                    self.log_failed(e)
                    delete_file(tgt_path)

    def normalize_frame(self, frame):
        ref_distance = self.get_ref_distance(frame)

        for part in PARTS_OPENPOSE_MAPPING.values():
            if isinstance(frame[part], dict):
                for coord in ["x", "y", "z"]:
                    if coord in frame[part]:
                        frame[part][coord] = list(
                            frame[part][coord] / ref_distance)
        return frame

    def get_ref_distance(self, frame):
        """
        Calculate distance of reference, based on the distance between
        shoulders.
        """
        from commons.model import Coordinate

        # Find indexes:
        body = frame["body"]
        idx_neck = body["name"].index("neck")
        idx_left_shoulder = body["name"].index("shoulder_left")
        idx_right_shoulder = body["name"].index("shoulder_right")

        # Find neck:
        neck = Coordinate(
            body["x"][idx_neck],
            body["y"][idx_neck],
            body["z"][idx_neck],
            body["score"][idx_neck],
            name="neck")
        if neck.is_zero():
            raise Exception("Could not find `neck` for normalizing skeleton.")

        # Find a valid shoulder:
        left_shoulder = Coordinate(
            body["x"][idx_left_shoulder],
            body["y"][idx_left_shoulder],
            body["z"][idx_left_shoulder],
            body["score"][idx_left_shoulder],
            name="left_shoulder")
        right_shoulder = Coordinate(
            body["x"][idx_right_shoulder],
            body["y"][idx_right_shoulder],
            body["z"][idx_right_shoulder],
            body["score"][idx_right_shoulder],
            name="right_shoulder")
        if not left_shoulder.is_zero():
            shoulder = left_shoulder
        elif not right_shoulder.is_zero():
            shoulder = right_shoulder
        else:
            raise Exception(
                "Could not find a `shoulder` for normalizing skeleton.")

        # Calculate distance:
        return neck.dist_to(shoulder)
