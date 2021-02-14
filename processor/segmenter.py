#!/usr/bin/env python3
import shutil
import tempfile

from commons.log import log, log_progress
from commons.util import (create_if_missing, delete_dir,
                          exists, normpath, filename, execute_command)
from utils import (get_camera_files_if_all_matched, create_filename)

from .processor import Processor


class Segmenter(Processor):
    """
        Preprocessor for splitting original videos
    """

    FORMAT_PRIORITIES = ["mov", "vid"]

    def __init__(self, args=None):
        super().__init__('segment', args)
        self.fps_in = self.get_arg("fps_in")
        self.fps_out = self.get_arg("fps_out")
        self.vidreader_path = self.get_arg("vidreader_path")

    def run(self, group, rows):
        if not rows.empty:
            self.split_videos(rows, self.input_dir, self.get_cameras(),
                              self.output_dir)

    def split_videos(self, rows, input_dir, cameras, output_dir):
        tempdir = tempfile.gettempdir()
        total = len(rows.index) * len(cameras)

        for row_idx, row in enumerate(rows.itertuples()):
            camera_files = get_camera_files_if_all_matched(
                session_or_sign=row.session,
                scene=row.scene,
                formats=self.FORMAT_PRIORITIES,
                cameras=cameras,
                dir=input_dir)

            for cam_idx, (cam, file) in enumerate(camera_files.items()):
                tgt_path = create_filename(base=row.basename,
                                           camera=cam,
                                           dir=output_dir)
                log_progress((len(cameras) * row_idx) + (cam_idx + 1),
                             total, f"{row.basename} (cam {cam:02.0f})")

                # Splits only if the file is not already present:
                if self.output_exists(tgt_path):
                    self.log_skipped()
                else:
                    tmp_path = create_filename(base=row.basename,
                                               camera=cam,
                                               dir=tempdir)
                    create_if_missing(tmp_path)
                    prefix = filename(tmp_path)

                    log(f"    Segmenting frames "
                        f"[{row.frame_start:.0f} ~ {row.frame_end:.0f}] ", 2)

                    try:
                        # Split file in temporary diretory:
                        self.split_video(file, tmp_path, prefix,
                                         row.frame_start,
                                         row.frame_end, self.fps_in,
                                         self.fps_out)

                        # Save file to target directory:
                        shutil.move(tmp_path, tgt_path)
                    except Exception as e:
                        self.log_failed(e)
                        delete_dir(tmp_path)

    def split_video(self, input_file, output_path, prefix, start, end, fps_in,
                    fps_out):
        executable = normpath(self.vidreader_path)
        assert exists(
            executable), f"Could not locate `vidReader` executable at `{executable}`."

        args = [input_file, output_path, prefix, start, end, fps_in, fps_out]
        success, _, e = execute_command(executable, args)

        if not success:
            raise e
