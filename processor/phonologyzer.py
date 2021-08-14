#!/usr/bin/env python3
from .processor import Processor

import json
from os.path import normpath
import commons.util as u
from commons.log import log, log_progress, init_logger
from commons.util import Argument, load_args
import reader


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
            # self.split_videos(rows, self.input_dir, self.get_cameras(),
            #                   self.output_dir)
            pass

    def process_files(self, input_dir, output_dir, video_dir, model,
                      data_reader, debug):
        from copy import deepcopy

        files = u.filter_files(input_dir, ext="json")
        files = files[:100] if debug else files
        total = len(files)

        for idx, path in enumerate(files):
            log_progress(idx + 1, total, f"{path}...")

            raise Exception(
                "must include 'frame_index' property, changing the 'json_reader'"
            )

            data = self.read_data(path, model, data_reader)

            # Create target name:
            filename = u.filename(path, False)
            tgt_file = normpath(f"{output_dir}/{filename}.json")

            if not u.exists(tgt_file):
                # Extract attributes:
                attributes = self.extract_attributes(data, model)

                # Preview frames:
                if debug:
                    self.preview(video_dir, data["file"], attributes)

                # Write output:
                output_data = deepcopy(data)
                del output_data["coordinates"]
                output_data["phono_attributes"] = attributes

                u.create_if_missing(output_dir)
                u.save_json(output_data, tgt_file)

    def read_data(self, path, model, data_reader):
        person = 0

        with open(path) as file:
            content = json.load(file)
            reader = data_reader(content, model)
            return reader.get_data(person)

    def extract_attributes(self, data, model):
        from extractor import FeatureExtactor
        extractor = FeatureExtactor(model)
        all_attributes = list()
        coordinates = data["coordinates"]

        for frame_idx in range(len(coordinates)):
            attributes = extractor.extract_attributes(data, frame_idx)
            attributes["index"] = frame_idx
            all_attributes.append(attributes)
            # log(f" {frame_idx:>3}: {attributes}", 2)
            # orientation_dh: {attributes['orientation_dh']}, orientation_ndh: {attributes['orientation_ndh']},
        return all_attributes

    def preview(self, video_dir, video_name, attributes):
        def log_attributes(x):
            [log(f" {key:<20} {value}") for key, value in x.items()]
            log("------------------------------")

        import cv2
        idx_attributes = {x["frame_index"]: x for x in attributes}
        idx = 0
        path = normpath(f"{video_dir}/{video_name}")
        capture = cv2.VideoCapture(path)
        success, image = capture.read()

        log("========================================")
        log(f" PREVIEW '{video_name}'")
        log("========================================")

        while success:
            log_attributes(idx_attributes[idx])
            idx += 1
            cv2.imshow("Preview", image)
            cv2.waitKey()
            success, image = capture.read()

        cv2.destroyAllWindows()
        capture.release()
        log("")
