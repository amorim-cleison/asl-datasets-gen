#!/usr/bin/env python3
import argparse
import json
import math
import os
import random
import shutil

from sklearn.model_selection import train_test_split

import tools
import tools.utils as utils

from .preprocessor import Preprocessor


class Holdout_Preprocessor(Preprocessor):
    """
        Proprocessing though Hold Out split
    """

    def __init__(self, argv=None):
        super().__init__('split', argv)
        self.test_size = (self.arg.holdout['test'] / 100)
        self.val_size = (self.arg.holdout['val'] / 100)
        self.train_size = 1 - (self.test_size + self.val_size)

        if 'seed' in self.arg.holdout:
            self.seed = self.arg.holdout['seed']
        else:
            self.seed = 1

    def start(self):
        label_path = '{}/label.json'.format(self.input_dir)
        self.print_log("Source directory: {}".format(self.input_dir))
        self.print_log("Holdout of data to '{}'...".format(self.output_dir))

        if not os.path.isfile(label_path):
            self.print_log("No data to holdout")
        else:
            # load labels for split:
            labels = self.read_json(label_path)
            X = [k for k in labels]
            y = [v['label'] for (k, v) in labels.items()]

            # Holdout (train, test, val):
            X_train, X_test, X_val, y_train, y_test, y_val = self.holdout_data(
                X, y, self.test_size, self.val_size)

            # Copy items:
            self.copy_items('train', self.train_size, X_train, y_train,
                            self.input_dir, self.output_dir, labels)
            self.copy_items('test', self.test_size, X_test,
                            y_test, self.input_dir, self.output_dir, labels)
            self.copy_items('val', self.val_size, X_val, y_val,
                            self.input_dir, self.output_dir, labels)
            self.print_log("Holdout complete.")

    def holdout_data(self, X, y, test_size, val_size):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.seed)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=val_size, random_state=self.seed)
        return X_train, X_test, X_val, y_train, y_test, y_val

    def copy_items(self, part, percent, items, labels, input_dir, output_dir, data):
        if items:
            self.print_log()
            self.print_log(
                "Saving '{}' data ({:.0%})...".format(part, percent))
            items_dir = '{}/{}'.format(output_dir, part)
            labels_path = '{}/{}_label.json'.format(output_dir, part)
            part_files = ['{}.json'.format(x) for x in items]
            part_labels = {x: data[x] for x in data if x in items}
            self.copy_files(part_files, input_dir, items_dir)
            self.save_json(part_labels, labels_path)

    def copy_files(self, items, src_dir, dest_dir):
        self.ensure_dir_exists(dest_dir)

        for item in items:
            self.print_log('* {}'.format(item))
            src = '{}/{}'.format(src_dir, item)
            dest = '{}/{}'.format(dest_dir, item)
            shutil.copy(src, dest)
