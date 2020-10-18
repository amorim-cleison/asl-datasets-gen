#!/usr/bin/env python3
import os
import shutil
import tempfile

import ffmpy

from .preprocessor import Preprocessor


class Splitter_Preprocessor(Preprocessor):
    """
        Preprocessor for splitting original videos
    """

    def __init__(self, argv=None):
        super().__init__('segment', argv)
        self.fps_in = self.arg.split['fps_in']
        self.fps_out = self.arg.split['fps_out']
        # self.max_frames = self.arg.split['max_frames']

    def start(self):
        # Load metadata:
        self.print_log("Loading metadata...")
        metadata = self.load_metadata(
            ['Main New Gloss.1', 'Session', 'Scene', 'Start', 'End'])

        if metadata.empty:
            self.print_log("Nothing to split.")
        else:
            # Split videos:
            self.print_log("Source directory: '{}'".format(self.input_dir))
            self.print_log("Splitting videos to '{}'...".format(self.output_dir))
            labels, files_labels = self.split_videos(
                metadata, self.input_dir, self.output_dir)

            # Save labels:
            self.print_log("Saving labels...")
            self.save_labels(self.output_dir, labels, files_labels)
            self.print_log("Split finished.")

    def split_videos(self, metadata, input_dir, output_dir):
        labels = set()
        files_labels = dict()
        files_splitted = set()

        for row in metadata.itertuples():
            if row.Main_New_Gloss_1 and row.Session and row.Scene:
                src_filename = self.format_filename(row.Session, row.Scene)
                src_filename = src_filename.replace('/', '_')
                src_filepath = '{}/{}'.format(input_dir, src_filename)
                sign = self.normalize(str(row.Main_New_Gloss_1)).lower()
                tgt_filename = self.create_filename(sign, files_splitted)
                tgt_filepath = '{}/{}'.format(output_dir, tgt_filename)

                if os.path.isfile(src_filepath):
                    start = row.Start
                    end = row.End

                    # Verify max frames:
                    # if self.max_frames and (end - start) > self.max_frames:
                    #     self.print_file(tgt_filename, src_filename, start, end)
                    #     self.print_log(" SKIP (exceeds max frames)")

                    # else:

                    # Splits only if file is not present:
                    if not os.path.isfile(tgt_filepath):
                        tmp_filepath = '{}/{}'.format(tempfile.gettempdir(),
                                                      tgt_filename)

                        # Split file in temporary diretory:
                        self.print_file(tgt_filename, src_filename, start, end)
                        self.split_video(src_filepath, tmp_filepath,
                                         sign, start, end,
                                         self.fps_in, self.fps_out)

                        # Save file to target directory:
                        shutil.move(tmp_filepath, tgt_filepath)

                    # Stores label and file mappings:
                    if sign not in labels:
                        labels.add(sign)

                    files_labels[tgt_filename] = sign
                    files_splitted.add(tgt_filename)

                    # Verify debug option:
                    if self.arg.debug:
                        if len(files_splitted) >= self.arg.debug_opts['split_items']:
                            break

        return labels, files_labels

    def print_file(self, tgt_filename, src_filename, start, end):
        self.print_log(
            "* {} \t {} [{:.0f}~{:.0f}]".format(tgt_filename, src_filename, start, end))

    def split_video(self, input_file, output_file,
                    sign, start, end,
                    input_fps, output_fps):
        # Create video name:
        # filename, tgt_filepath = self.create_filename(sign, output_dir)
        start_sec = self.frame_to_sec(start, input_fps)
        length_sec = self.frame_to_sec(end - start, input_fps)
        self.run_ffmpeg(input_file, output_file,
                        start_sec, length_sec, output_fps)

    def run_ffmpeg(self, src, tgt, start, length, fps):
        if not os.path.isfile(src):
            self.print_log('Video not found: %s' % src)

        else:
            ff = ffmpy.FFmpeg(
                inputs={src: None},
                outputs={tgt: ['-ss', start,
                               '-t', length,
                               '-r', str(fps),
                               '-y',
                               '-loglevel', 'error'
                               ]}
            )
            ff.run()

    def save_labels(self, output_dir, labels, files_labels):
        labels_file = "{}/label_name.txt".format(output_dir)
        self.save_items(sorted(labels), labels_file)

        files_labels_file = "{}/file_label.txt".format(output_dir)
        self.save_map(files_labels, files_labels_file)

    def create_filename(self, sign, current_files):
        idx = 0
        filename = None

        while (not filename) or (filename in current_files):
            idx += 1
            filename = "{!s}-{:03d}.mov".format(sign, idx)
        return filename

    def frame_to_sec(self, frame, fps):
        res = frame / fps
        secs, milis = divmod(res * 1000, 1000)
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)
        return '%02d:%02d:%02d.%03d' % (hours, mins, secs, milis)
