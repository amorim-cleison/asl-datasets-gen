#!/usr/bin/env python3
import json
import os
import subprocess

from tools import utils

from .preprocessor import Preprocessor


class Keypoint_Preprocessor(Preprocessor):
    """
        Select estimated keypoints
    """

    RANGE_SEPARATOR = '..'

    def __init__(self, argv=None):
        super().__init__('filter', argv)
        self.keypoints = self.__get_keypoints(self.arg)

    def start(self):
        src_label_path = '{}/label.json'.format(self.input_dir)
       
        if not os.path.isfile(src_label_path):
            self.print_log("No data for keypoints selection")
        else:
            self.print_log("Source directory: '{}'".format(self.input_dir))
            self.print_log(
                "Selecting keypoints to '{}'...".format(self.output_dir))
            self.process_items(
                self.input_dir, src_label_path, self.output_dir, 2)
            self.print_log("Keypoint selection complete.")

    def process_items(self, input_dir, src_label_path, output_dir, dimensions=2):
        # Target labels:
        labels = self.read_json(src_label_path)
        tgt_label_path = '{}/label.json'.format(output_dir)
        label_map = self.load_label_map(tgt_label_path)

        for name, value in labels.items():
            if name not in label_map:
                self.print_log("* {} ...".format(name))
                cur_path = '{}/{}.json'.format(input_dir, name)
                tgt_path = '{}/{}.json'.format(output_dir, name)
                content = self.read_json(cur_path)
                frames = content['data']

                for frame in frames:
                    skeletons = frame['skeleton']

                    for skeleton in skeletons:
                        # Select keypoints:
                        new_score, new_pose = self.select_keypoints(
                            self.keypoints, dimensions,
                            skeleton['score'], skeleton['pose'])

                        # Update keypoints:
                        skeleton['score'] = new_score
                        skeleton['pose'] = new_pose

                # Save output:
                self.save_json(content, tgt_path)

                # Save into label map:
                label_map[name] = value
                self.save_json(label_map, tgt_label_path)

    def select_keypoints(self, keypoints, dimensions, score, pose):
        new_score = list()
        new_pose = list()

        for i in keypoints:
            # Select scores:
            new_score.append(score[i])

            # Select keypoints:
            pose_start = i * dimensions
            pose_end = pose_start + dimensions
            new_pose.extend(pose[pose_start: pose_end])
        return new_score, new_pose

    def load_label_map(self, label_map_path):
        label_map = dict()

        if os.path.isfile(label_map_path):
            label_map = self.read_json(label_map_path)
        return label_map

    def __get_keypoints(self, arg):
        arg_points = arg.keypoint['points']
        arg_points = arg_points.replace(' ', '')
        arg_points = utils.parser.str2list(arg_points)
        keypoints = list()

        for p in arg_points:
            if self.RANGE_SEPARATOR in p:
                bounds = p.split(self.RANGE_SEPARATOR)

                if bounds[0] and bounds[1]:
                    bnd_start = int(bounds[0])
                    bnd_end = int(bounds[1]) + 1
                    rng_points = range(bnd_start, bnd_end)
                    keypoints.extend(rng_points)
                else:
                    raise ValueError(
                        "Invalid keypoint interval: '{}'".format(p))
            else:
                keypoints.append(int(p))
        return keypoints
