
import argparse
import os
import pickle
import sys

import numpy as np
from numpy.lib.format import open_memmap

from .gendata_feeder import Gendata_Feeder
from .preprocessor import Preprocessor


class Gendata_Preprocessor(Preprocessor):
    """
        Generate data
    """

    def __init__(self, argv=None):
        super().__init__('normalize', argv)
        self.joints = self.arg.gendata['joints']
        self.channels = self.arg.gendata['channels']
        self.num_person = self.arg.gendata['num_person']
        self.max_frames = self.arg.gendata['max_frames']
        self.repeat_frames = self.arg.gendata['repeat_frames']

    def start(self):
        self.print_log("Source directory: {}".format(self.input_dir))
        self.print_log("Generating data to '{}'...".format(self.output_dir))

        parts = ['train', 'test', 'val']
        joints = self.joints
        num_items = None

        if self.arg.debug:
            num_items = self.arg.debug_opts['gendata_items']
            joints = self.arg.debug_opts['gendata_joints']

        for part in parts:
            data_path = '{}/{}'.format(self.input_dir, part)
            label_path = '{}/{}_label.json'.format(self.input_dir, part)
            data_out_path = '{}/{}_data.npy'.format(self.output_dir, part)
            label_out_path = '{}/{}_label.pkl'.format(self.output_dir, part)
            debug = self.arg.debug

            self.print_log("Generating '{}' data...".format(part))
            
            if not os.path.isfile(label_path):
                self.print_log(" Nothing to generate")
            else:
                self.gendata(data_path, label_path, data_out_path, label_out_path,
                             num_person_in=self.num_person,
                             num_person_out=self.num_person,
                             max_frame=self.max_frames,
                             joints=joints,
                             channels=self.channels,
                             repeat_frames=self.repeat_frames,
                             debug=debug,
                             num_items=num_items)

        self.print_log("Data generation finished.")

    def gendata(self,
                data_path,
                label_path,
                data_out_path,
                label_out_path,
                num_person_in,  # observe the first 5 persons
                num_person_out,  # then choose 2 persons with the highest score
                joints,
                max_frame,
                channels,
                repeat_frames,
                debug=False,
                num_items=None):

        feeder = Gendata_Feeder(
            data_path=data_path,
            label_path=label_path,
            num_person_in=num_person_in,
            num_person_out=num_person_out,
            window_size=max_frame,
            joints=joints,
            channels=channels,
            repeat_frames=repeat_frames,
            debug=debug,
            num_items=num_items)

        sample_name = feeder.sample_name
        sample_label = []

        fp = open_memmap(
            data_out_path,
            dtype='float32',
            mode='w+',
            shape=(len(sample_name), channels, max_frame, joints, num_person_out))

        total = len(sample_name)

        for i, _ in enumerate(sample_name):
            data, label = feeder[i]
            self.progress_bar(i+1, total)
            fp[i, :, 0:data.shape[1], :, :] = data
            sample_label.append(label)

        with open(label_out_path, 'wb') as f:
            pickle.dump((sample_name, list(sample_label)), f)
