
import os
import sys
import pickle
import argparse

import numpy as np
from numpy.lib.format import open_memmap

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from feeder.feeder_sl import Feeder_SL

toolbar_width = 30


def print_toolbar(rate, annotation=''):
    # setup toolbar
    sys.stdout.write("{}[".format(annotation))
    for i in range(toolbar_width):
        if i * 1.0 / toolbar_width > rate:
            sys.stdout.write(' ')
        else:
            sys.stdout.write('-')
        sys.stdout.flush()
    sys.stdout.write(']\r')


def end_toolbar():
    sys.stdout.write("\n")


def gendata(
        data_path,
        label_path,
        data_out_path,
        label_out_path,
        num_person_in=5,  # observe the first 5 persons
        num_person_out=2,  # then choose 2 persons with the highest score
        joints=130,
        max_frame=300,
        channels=3,
        debug=False):

    feeder = Feeder_SL(
        data_path=data_path,
        label_path=label_path,
        num_person_in=num_person_in,
        num_person_out=num_person_out,
        window_size=max_frame,
        joints=joints,
        channels=channels,
        debug=debug)

    sample_name = feeder.sample_name
    sample_label = []

    fp = open_memmap(
        data_out_path,
        dtype='float32',
        mode='w+',
        shape=(len(sample_name), channels, max_frame, joints, num_person_out))

    for i, _ in enumerate(sample_name):
        data, label = feeder[i]
        print_toolbar(i * 1.0 / len(sample_name),
                      '({:>5}/{:<5}) Processing data: '.format(
                          i + 1, len(sample_name)))
        fp[i, :, 0:data.shape[1], :, :] = data
        sample_label.append(label)

    with open(label_out_path, 'wb') as f:
        pickle.dump((sample_name, list(sample_label)), f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sign Language Data Converter.')
    parser.add_argument('--input_dir')
    parser.add_argument('--output_dir')
    parser.add_argument('--debug', default=False)
    arg = parser.parse_args()

    part = ['train', 'val']

    for p in part:
        data_path = '{}/{}/data'.format(arg.input_dir, p)
        label_path = '{}/{}/label.json'.format(arg.input_dir, p)
        data_out_path = '{}/{}_data.npy'.format(arg.output_dir, p)
        label_out_path = '{}/{}_label.pkl'.format(arg.output_dir, p)
        debug = arg.debug

        if not os.path.exists(arg.output_dir):
            os.makedirs(arg.output_dir)
        
        gendata(data_path, label_path, data_out_path, label_out_path, num_person_in=1,
                num_person_out=1, max_frame=120, joints=130, channels=3, debug=debug)
