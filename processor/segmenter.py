#!/usr/bin/env python3
import shutil
import tempfile

from commons.log import log, log_progress
from commons.util import (create_if_missing, delete_dir, execute_command,
                          exists, filename, normpath)
from utils import create_filename, get_camera_files_if_all_matched

from .processor import Processor


class Segmenter(Processor):
    """
        Preprocessor for splitting original videos
    """

    def __init__(self, args=None):
        super().__init__('segment', args)
        self.fps_in = self.get_arg("fps_in")
        self.fps_out = self.get_arg("fps_out")
        self.formats = self.get_arg("format")
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
                formats=self.formats,
                cameras=cameras,
                modes=self.modes,
                dir=input_dir)

            for cam_idx, (cam, fmt_path) in enumerate(camera_files.items()):
                fmt = fmt_path["fmt"]
                path = fmt_path["path"]
                tgt_path = create_filename(base=row.basename,
                                           camera=cam,
                                           dir=output_dir)

                log_progress((len(cameras) * row_idx) + (cam_idx + 1),
                             total, f"{row.basename} (cam {cam:02.0f}) ({fmt})")

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
                        self.split_video(path, tmp_path, fmt, prefix,
                                         row.frame_start, row.frame_end,
                                         self.fps_in, self.fps_out)

                        # Save file to target directory:
                        shutil.move(tmp_path, tgt_path)
                    except Exception as e:
                        self.log_failed(e)
                        delete_dir(tmp_path)

    def split_video(self, input_path, output_dir, fmt, prefix, frame_start,
                    frame_end, fps_in, fps_out):
        from math import ceil, floor

        ROUND_BASE = 10.0
        FORMAT_SPLIT_FN = {
            "mov": self.split_mov,
            "vid": self.split_vid
        }

        if frame_end is None:
            frame_end = frame_start

        frame_start = int(floor(frame_start / ROUND_BASE) * ROUND_BASE)
        frame_end = int(ceil(frame_end / ROUND_BASE) * ROUND_BASE)
        step = int(fps_in / fps_out)

        for frame in range(frame_start, (frame_end + 1), step):
            fn = FORMAT_SPLIT_FN[fmt]
            output_path = f"{output_dir}/{prefix}_{frame:05d}.ppm"
            args = {
                "input_path": input_path,
                "output_path": output_path,
                "frame": frame
            }
            fn(**args)

            if not exists(output_path):
                raise Exception(f"Failed to segment frame {frame}")

    def split_mov(self, input_path, output_path, frame):
        from ffmpy import FFmpeg
        input_args = {input_path: None}
        output_args = {
            output_path: [
                "-vf", f"select='between(n\\,{frame}\\,{frame})",
                "-hide_banner",
                "-loglevel", "error"
            ]
        }
        ff = FFmpeg(inputs=input_args, outputs=output_args)
        ff.run()

    def split_vid(self, input_path, output_path, frame):
        executable = normpath(self.vidreader_path)
        assert exists(
            executable), f"Failed to locate `vidReader` at `{executable}`."

        args = [input_path, output_path, frame]
        success, _, e = execute_command(executable, args)

        if not success:
            raise e
