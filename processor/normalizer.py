import os
import pickle

from numpy.lib.format import open_memmap

from feeder.normalizer_feeder import NormalizerFeeder
from .processor import Processor
from tools.utils import progress_bar

from commons.log import log, log_progress


class Normalizer(Processor):
    """
        Generate data
    """
    def __init__(self, argv=None):
        super().__init__('normalize', argv)
        self.joints = self.args.gendata['joints']
        self.channels = self.args.gendata['channels']
        self.num_person = self.args.gendata['num_person']
        self.max_frames = self.args.gendata['max_frames']
        self.repeat_frames = self.args.gendata['repeat_frames']

    def start(self):
        log(f"Source directory: {self.input_dir}", 1)  # FIXME: print_log
        log(f"Generating data to '{self.output_dir}'...",
            1)  # FIXME: print_log

        parts = ['train', 'test', 'val']
        joints = self.joints
        num_items = None

        if self.args.debug:
            num_items = self.args.debug_opts['gendata_items']
            joints = self.args.debug_opts['gendata_joints']

        for part in parts:
            data_path = '{}/{}'.format(self.input_dir, part)
            label_path = '{}/{}_label.json'.format(self.input_dir, part)
            data_out_path = '{}/{}_data.npy'.format(self.output_dir, part)
            label_out_path = '{}/{}_label.pkl'.format(self.output_dir, part)
            debug = self.args.debug

            log(f"Generating '{part}' data...", 1)  # FIXME: print_log

            if not os.path.isfile(label_path):
                log(" Nothing to generate"), 1  # FIXME: print_log
            else:
                self.gendata(data_path,
                             label_path,
                             data_out_path,
                             label_out_path,
                             num_person_in=self.num_person,
                             num_person_out=self.num_person,
                             max_frame=self.max_frames,
                             joints=joints,
                             channels=self.channels,
                             repeat_frames=self.repeat_frames,
                             debug=debug,
                             num_items=num_items)

        log("Data generation finished.", 1)  # FIXME: print_log

    def gendata(
            self,
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

        feeder = NormalizerFeeder(data_path=data_path,
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

        fp = open_memmap(data_out_path,
                         dtype='float32',
                         mode='w+',
                         shape=(len(sample_name), channels, max_frame, joints,
                                num_person_out))

        total = len(sample_name)

        for i, _ in enumerate(sample_name):
            data, label = feeder[i]
            log_progress(i + 1, total)
            fp[i, :, 0:data.shape[1], :, :] = data
            sample_label.append(label)

        with open(label_out_path, 'wb') as f:
            pickle.dump((sample_name, list(sample_label)), f)
