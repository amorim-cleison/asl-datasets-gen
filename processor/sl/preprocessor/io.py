import os
import shutil
import json

import pandas
import xlrd
import re
import string
import torchlight


class IO:
    """
        IO
    """

    def __init__(self, argv=None):
        self.arg = argv
        self.init_environment()

    def init_environment(self):
        self.io = torchlight.IO(
            self.arg.work_dir,
            save_log=self.arg.save_log,
            print_log=self.arg.print_log)
        self.io.save_arg(self.arg)

    def progress_bar(self, current, total):
        increments = 50
        percentual = ((current / total) * 100)
        i = int(percentual // (100 / increments))
        text = "\r|{0: <{1}}| {2:.0f}%".format('█' * i, increments, percentual)
        print(text, end="\n" if percentual >= 100 else "")

    def ensure_dir_exists(self, dir):
        if not os.path.exists(dir):
            self.create_dir(dir)

    def create_dir(self, dir):
        os.makedirs(dir)

    def remove_dir(self, dir):
        if os.path.exists(dir):
            shutil.rmtree(dir, ignore_errors=True)

    def save_items(self, items, path):
        with open(path, 'w') as f:
            for item in items:
                f.write("{}{}".format(item, os.linesep))

    def save_map(self, map, path):
        with open(path, 'w') as f:
            for key, val in map.items():
                f.write("{}:{}{}".format(key, val, os.linesep))

    def save_json(self, data, path):
        with open(path, 'w') as f:
            json.dump(data, f)

    def read_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def create_command_line(self, command, args):
        command_line = command + ' '
        command_line += ' '.join(['{} {}'.format(k, v)
                                  for k, v in args.items()])
        return command_line

    def print_log(self, log=''):
        self.io.print_log(log)
