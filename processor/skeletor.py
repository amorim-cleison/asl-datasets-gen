#!/usr/bin/env python3
import copy
import tempfile

from commons.log import log, log_progress
from commons.util import (create_if_missing, delete_dir, directory,
                          execute_command, exists, filename, filter_files,
                          normpath, read_json, save_json)
from constant import KEYPOINTS_COCO, PARTS_OPENPOSE_MAPPING
from utils import create_filename, get_camera_dirs_if_all_matched

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

        # OpenPose executable file:
        self.openpose = self.get_arg("openpose_path")
        # assert exists(
        #     self.openpose), "Path to OpenPose executable is not valid."

        # OpenPose models directory:
        self.model_path = normpath(self.get_arg("models_dir"))
        assert exists(self.model_path), "Path to OpenPose models is not valid."

    def run(self, group, rows):
        tempdir = tempfile.gettempdir()
        snippets_dir = normpath(f"{tempdir}/snippets")
        create_if_missing(snippets_dir)

        if not rows.empty:
            self.process_videos(rows, self.input_dir,
                                snippets_dir, self.output_dir,
                                self.get_cameras(), self.modes)

    def process_videos(self, rows, input_dir, snippets_dir, output_dir,
                       cameras, modes):
        total = len(rows.index)

        for row_idx, row in enumerate(rows.itertuples()):
            # Log current:
            log_progress(row_idx + 1, total, row.basename)

            # Create target paths per mode:
            mode_paths = {
                mode: create_filename(base=row.basename,
                                      dir=normpath(f"{output_dir}/{mode}"),
                                      ext="json")
                for mode in modes
            }
            mode_paths = {
                mode: path
                for mode, path in mode_paths.items()
                if not self.output_exists(path)
            }

            # Get valid input files per camera:
            camera_dirs = get_camera_dirs_if_all_matched(basename=row.basename,
                                                         scene=row.scene,
                                                         cameras=cameras,
                                                         modes=self.modes,
                                                         dir=input_dir)

            if (not mode_paths) or (not camera_dirs):
                self.log_skipped()
            else:
                try:
                    create_if_missing(snippets_dir)

                    # Estimate skeletons/snippets:
                    cam_snippets = self.estimate_snippets(
                        camera_dirs, snippets_dir)

                    # Pack snippets and save:
                    self.pack_and_save_snippets(cam_snippets, mode_paths, row)
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

    def get_properties(self, row, mode):
        return {
            "label": row.label,
            "gloss": row.gloss,
            "consultant": row.consultant,
            "session": row.session,
            "scene": row.scene,
            "frame_start": row.frame_start,
            "frame_end": row.frame_end,
            "handshape_dh_start": row.d_start_hs,
            "handshape_dh_end": row.d_end_hs,
            "handshape_ndh_start": row.nd_start_hs,
            "handshape_ndh_end": row.nd_end_hs,
            "passive_arm": row.passive_arm,
            "fps": self.get_arg("fps_out"),
            "mode": mode
        }

    def estimate_snippets(self, camera_dirs, snippets_dir):
        cam_snippets = dict()

        for cam, _dir in camera_dirs.items():
            log(f"   Estimating (cam {cam:02.0f})...")
            self.run_openpose(_dir, snippets_dir)

            basename = filename(_dir, False)
            snippets = sorted(
                filter_files(snippets_dir, name=f"{basename}*", ext="json"))
            assert (len(snippets) > 0), "Failed to estimate snippets."
            cam_snippets[cam] = snippets
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

    def pack_and_save_snippets(self, cam_snippets, mode_paths, row):
        for mode, path in mode_paths.items():
            log(f"   Packing ({mode})...")
            properties = self.get_properties(row, mode)

            # Pack snippets into single data and save:
            data = self.pack_snippets(cam_snippets, properties, mode)
            create_if_missing(directory(path))
            save_json(data, path)

    def pack_snippets(self, cams_snippets, properties, mode="2d"):
        assert (mode is not None), "`Mode` must be informed"

        def validate_mapping(cams_snippets, required_size, mode):
            assert (
                len(cams_snippets) >= required_size
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
                frame['skeleton'][part]["z"] = frame_cam2['skeleton'][part][
                    "x"]
                frame['skeleton'][part]["score"] = [
                    (score_cam1 + score_cam2) / 2
                    for (score_cam1, score_cam2
                         ) in zip(frame_cam1['skeleton'][part]["score"],
                                  frame_cam2['skeleton'][part]["score"])
                ]
            merged_frames.append(frame)
        return merged_frames

    def create_frames_from_snippets(self, snippets):
        frames = list()

        def get_frame_index(path):
            return int(filename(path, False).split("_")[-2])

        for path in snippets:
            data = read_json(path)
            frame = {'frame_index': get_frame_index(path), 'skeleton': {}}

            # Consider only first person:
            person = data['people'][0]

            for src_part, tgt_part in self.PARTS_MAPPING.items():
                frame['skeleton'][tgt_part] = self.create_coordinates(
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
