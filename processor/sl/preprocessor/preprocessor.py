import os
import shutil
import json

import pandas
import xlrd
import re
import string
import torchlight
from .io import IO
import subprocess


class Preprocessor(IO):
    """
        Base Processor
    """

    METADATA_COLUMNS = ['Main New Gloss.1',
                        'Consultant', 'Session', 'Scene', 'Start', 'End']
    METADATA_IGNORED_VALUES = ['============', '------------']

    def __init__(self, phase_name, argv=None):
        super().__init__(argv)
        self.phase_name = phase_name
        self.file_pattern = self.arg.download['file_pattern']
        self.input_dir, self.output_dir = self.get_input_output_dir(phase_name)
        self.ensure_dir_exists(self.output_dir)

    def start(self):
        pass

    def get_input_output_dir(self, phase_name):
        input_dir = None
        output_dir = None
        work_dir = self.arg.work_dir
        phase_args = self.arg.__getattribute__(phase_name)

        if 'input_dir' in phase_args:
            str_input_dir = '{}/{}'.format(work_dir, phase_args['input_dir'])
            input_dir = os.path.realpath(str_input_dir)
        if 'output_dir' in phase_args:
            str_output_dir = '{}/{}'.format(work_dir, phase_args['output_dir'])
            output_dir = os.path.realpath(str_output_dir)
        return input_dir, output_dir

    def progress_bar(self, current, total, message=None, overwritable=False):
        increments = 50
        percentual = ((current / total) * 100)
        i = int(percentual // (100 / increments))
        prefix = "{} ".format(message) if message else ""
        text = "\r{}|{: <{}}| {:.0f}%".format(
            prefix, '█' * i, increments, percentual)

        if overwritable:
            end = "\r"
        elif percentual >= 100:
            end = "\n"
        else:
            end = ""
        print(text, end=end)

    def load_metadata(self, columns=None, nrows=None):
        if self.__ensure_metadata():
            if not columns:
                columns = self.METADATA_COLUMNS

            df = pandas.read_excel(self.arg.metadata_file,
                                   na_values=self.METADATA_IGNORED_VALUES,
                                   keep_default_na=False)
            df = df[columns]
            df = df.dropna(how='all')
            df = df.head(nrows)
            norm_columns = {x: self.normalize(x) for x in columns}
            df = df.rename(index=str, columns=norm_columns)

        return df

    def __ensure_metadata(self):
        if os.path.isfile(self.arg.metadata_file):
            metadata_ok = True
        else:
            metadata_url = self.arg.download['metadata_url']

            self.print_log("Downloading metadata to '{}'...".format(
                self.arg.metadata_file))
            self.print_log("Source Url: {}".format(metadata_url))
            metadata_ok = self.download_file(
                metadata_url, self.arg.metadata_file)
        return metadata_ok

    def download_file(self, url, file):
        try:
            command = 'wget {}'.format(url)
            args = {
                '-O': file,
                '-q': '',
                '--show-progress': ''
            }
            command_line = self.create_command_line(command, args)
            subprocess.check_call(command_line, shell=True,
                                  stderr=subprocess.STDOUT)
            success = True

        except subprocess.CalledProcessError as e:
            success = False
            self.print_log(" FAILED ({} {})".format(e.returncode, e.output))

        return success

    def format_filename(self, session, scene):
        return self.file_pattern.format(session=session,
                                        scene=int(scene),
                                        camera=1)

    def normalize(self, text):
        special_chars = re.escape(string.punctuation + string.whitespace)
        return re.sub(r'['+special_chars+']', '_', text)
