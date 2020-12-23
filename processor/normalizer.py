#!/usr/bin/env python3
from commons.log import log, log_err, log_progress
from commons.util import exists, filename
from commons.util.io_util import (delete_file, filter_files,
                                  read_json, save_json)
from constant import PARTS_OPENPOSE_MAPPING
from utils import create_json_name

from .processor import Processor


class Normalizer(Processor):
    """
        Preprocessor for normalizing skeleton coordinates
    """

    def __init__(self, args=None):
        super().__init__('normalize', args)

    def start(self):
        skeleton_files = filter_files(self.input_dir, ext="json")

        if not skeleton_files:
            log("Nothing to normalize.", 1)
        else:
            # video processing:
            log(f"Source directory: '{self.input_dir}'", 1)
            log(f"Normalizing skeletons to '{self.output_dir}'...", 1)
            total = len(skeleton_files)

            for idx, file in enumerate(skeleton_files):
                log_progress(idx + 1, total, filename(file))
                data = read_json(file)
                tgt_filepath = create_json_name(session_or_sign=data["label"],
                                                person=data["consultant"],
                                                scene=data["scene"],
                                                dir=self.output_dir)

                if not exists(tgt_filepath):
                    try:
                        # Normalize and save data:
                        data = self.normalize_data(data)
                        save_json(data, tgt_filepath)
                    except Exception as e:
                        log_err(f"   FAILED ({str(e)})", ex=e)
                        delete_file(tgt_filepath)

            log("Normalization complete.", 1)

    def normalize_data(self, data):
        # Normalize frames:
        data["frames"] = [self.normalize_frame(
            frame) for frame in data["frames"]]
        return data

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
        Calculate distance of reference, based on the distance between shoulders.
        """
        from commons.model import Coordinate

        # Find shoulders:
        body = frame["body"]
        idx_left_shoulder = body["name"].index("shoulder_left")
        idx_right_shoulder = body["name"].index("shoulder_right")

        assert (idx_left_shoulder >= 0) and (idx_right_shoulder >=
                                             0), "Could not find shoulders for normalizing skeleton."
        # Create the related coordinates:
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

        # Calculate distance:
        return left_shoulder.dist_to(right_shoulder)
