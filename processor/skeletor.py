#!/usr/bin/env python3
import copy
import tempfile

from commons.log import log, log_progress
from commons.util import (create_if_missing, delete_dir, execute_command,
                          exists, filename, filter_files, normpath, read_json,
                          save_json)
from utils import (create_filename, get_camera_dirs_if_all_matched)
from constant import PARTS_OPENPOSE_MAPPING, KEYPOINTS_COCO

from .processor import Processor


class Skeletor(Processor):
    """
        Preprocessor form pose estimation with OpenPose
    """
    PARTS_MAPPING = PARTS_OPENPOSE_MAPPING
    KEYPOINTS = KEYPOINTS_COCO
    SKELETON_MODEL = "COCO"

    def __init__(self, argv=None):
        super().__init__('skeleton', argv)
        self.mode = self.get_arg("mode")

        # OpenPose executable file:
        self.openpose = self.get_arg("openpose_path")
        # assert exists(
        #     self.openpose), "Path to OpenPose executable is not valid."

        # OpenPose models directory:
        self.model_path = normpath(self.get_arg("models_dir"))
        assert exists(self.model_path), "Path to OpenPose models is not valid."

    def run(self, metadata):
        tempdir = tempfile.gettempdir()
        snippets_dir = normpath(f"{tempdir}/snippets")
        create_if_missing(snippets_dir)

        if not metadata.empty:
            self.process_videos(metadata, self.input_dir, snippets_dir,
                                self.output_dir,
                                self.get_cameras(), self.mode)

    def process_videos(self, metadata, input_dir, snippets_dir, output_dir,
                       cameras, mode):
        total = len(metadata.index)

        for row_idx, row in enumerate(metadata.itertuples()):
            tgt_path = create_filename(session_or_sign=row.gloss,
                                       person=row.consultant,
                                       scene=row.scene,
                                       dir=output_dir,
                                       ext="json")
            log_progress(row_idx + 1, total, f"{filename(tgt_path)} ")

            if self.output_exists(tgt_path):
                self.log_skipped()
            else:
                # Get valid camera files:
                camera_files = get_camera_dirs_if_all_matched(
                    session_or_sign=row.label,
                    person=row.consultant,
                    scene=row.scene,
                    cameras=cameras,
                    dir=input_dir)

                if camera_files:
                    # Get properties:
                    properties = self.get_properties(row, cameras)

                    try:
                        create_if_missing(snippets_dir)

                        # Estimate skeletons/snippets:
                        cam_snippets = self.estimate_snippets(
                            camera_files, snippets_dir)

                        # Pack snippets into single data:
                        data = self.pack_snippets(
                            cam_snippets, properties, mode)

                        # Save data:
                        save_json(data, tgt_path)
                    except Exception as e:
                        self.log_failed(e)
                    finally:
                        delete_dir(snippets_dir)

    def get_distinct_items(self, files_properties):
        from itertools import islice

        # Select disctinct items by label x consultant x scene:
        distinct_items = set([(prop["label"], prop["consultant"],
                               prop["scene"])
                              for prop in files_properties.values()])

        # Truncate items if debugging:
        nrows = min(
            self.get_debug_arg("skeleton_items"),
            len(distinct_items)) if self.is_debug() else len(distinct_items)
        return islice(distinct_items, nrows), nrows

    def get_properties(self, row, cameras):
        return {
            "label": row.label,
            "gloss": row.gloss,
            "consultant": row.consultant,
            "session": row.session,
            "scene": row.scene,
            "cameras": cameras,
            "frame_start": row.frame_start,
            "frame_end": row.frame_end,
            "handshape_dh_start": row.d_start_hs,
            "handshape_dh_end": row.d_end_hs,
            "handshape_ndh_start": row.nd_start_hs,
            "handshape_ndh_end": row.nd_end_hs,
            "passive_arm": row.passive_arm,
            "fps": self.get_arg("fps_out")
        }

    def estimate_snippets(self, camera_dirs, snippets_dir):
        cam_snippets = dict()

        # Estimate skeletons for all the cameras:
        for cam, dir in camera_dirs.items():
            log(f"   Estimating camera {cam}...")
            self.run_openpose(dir, snippets_dir)

            file_basename = filename(dir, False)
            file_snippets = sorted(
                filter_files(snippets_dir,
                             name=f"{file_basename}*",
                             ext="json"))
            cam_snippets[cam] = file_snippets
            assert (len(cam_snippets) >
                    0), "Could not locate estimated snippet files"
        return cam_snippets

    def run_openpose(self, dir, snippets_dir):
        command = self.openpose
        args = {
            '--image_dir': dir,
            '--write_json': snippets_dir,
            '--display': 0,
            '--render_pose': 0,
            '--model_pose': self.SKELETON_MODEL,
            '--model_folder': self.model_path
        }
        if not self.is_debug():
            args['--face'] = ''
            args['--hand'] = ''

        success, _, e = execute_command(command, args)
        if not success:
            raise e

    def pack_snippets(self, cams_snippets, properties, mode="2d"):
        assert (mode is not None), "`Mode` must be informed"

        def validate_mapping(cams_snippets, required_size, mode):
            assert (
                len(cams_snippets) == required_size
            ), f"Camera x snippets mapping size is not compatible with '{mode}' mode"

        if mode == "2d":
            validate_mapping(cams_snippets, 1, mode)
            frames = self.create_frames_from_snippets(cams_snippets[1])
        elif mode == "3d":
            validate_mapping(cams_snippets, 2, mode)
            frames_cam1 = self.create_frames_from_snippets(cams_snippets[1])
            frames_cam2 = self.create_frames_from_snippets(cams_snippets[2])
            frames = self.merge_frames_into_3d(frames_cam1, frames_cam2)
        else:
            frames = []

        packed_data = copy.deepcopy(properties)
        packed_data["frames"] = frames
        return packed_data

    def merge_frames_into_3d(self, frames_cam1, frames_cam2):
        assert (
            len(frames_cam1) == len(frames_cam2)
        ), "The length of the frames from camera 1 and 2 must be equal."
        merged_frames = list()

        for frame_cam1, frame_cam2 in zip(frames_cam1, frames_cam2):
            frame = copy.deepcopy(frame_cam1)

            for part in self.PARTS_MAPPING.values():
                frame[part]["z"] = frame_cam2[part]["x"]
                frame[part]["score"] = [
                    (score_cam1 + score_cam2) / 2
                    for (score_cam1, score_cam2) in zip(
                        frame_cam1[part]["score"], frame_cam2[part]["score"])
                ]
            merged_frames.append(frame)
        return merged_frames

    def create_frames_from_snippets(self, snippets):
        frames = list()

        def get_frame_index(path):
            return int(filename(path, False).split("_")[-2])

        for path in snippets:
            data = read_json(path)
            frame = {'frame_index': get_frame_index(path)}

            # Consider only first person:
            person = data['people'][0]

            for src_part, tgt_part in self.PARTS_MAPPING.items():
                frame[tgt_part] = self.create_coordinates(
                    tgt_part, person[src_part])
            frames.append(frame)
        return frames

    def create_coordinates(self, part, keypoints):
        x = list()
        y = list()
        score = list()
        name = list()

        # Read coordinates:
        for i in range(0, len(keypoints), 3):
            x.append(keypoints[i])
            y.append(keypoints[i + 1])
            score.append(keypoints[i + 2])

        # Get part names:
        if (x and y and score):
            name = self.KEYPOINTS[part]

        assert (
            len(name) == len(x) == len(y) == len(score)
        ), f"Incompatible sizes between coordinates and parts names for the '{part}' (name: {len(name)}, x: {len(x)}, y: {len(y)}, score: {len(score)})."

        # Return data:
        return {"name": name, "score": score, "x": x, "y": y}
