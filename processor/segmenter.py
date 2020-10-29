#!/usr/bin/env python3
import shutil
import tempfile

import ffmpy
from commons.log import log, log_progress
from commons.util import (create_if_missing, delete_dir, exists, filename,
                          filter_files)
from utils import (create_video_name, get_camera_files_if_all_matched,
                   load_files_properties, remove_special_chars,
                   save_files_properties)

from .processor import Processor


class Segmenter(Processor):
    """
        Preprocessor for splitting original videos
    """
    def __init__(self, args=None):
        super().__init__('segment', args)
        self.fps_in = self.get_phase_arg("fps_in")
        self.fps_out = self.get_phase_arg("fps_out")

    def start(self):
        nrows = self.get_debug_arg(
            "segment_items") if self.is_debug() else None

        # Recreates output dir if there is no video processed:
        files = filter_files(self.output_dir, ext="mov")
        if len(files) == 0:
            delete_dir(self.output_dir)

        create_if_missing(self.output_dir)

        # Load metadata:
        log("Loading metadata...", 1)  # FIXME: print_log
        metadata = self.load_metadata([
            'Main New Gloss', 'Consultant', 'D Start HS', 'N-D Start HS',
            'D End HS', 'N-D End HS', 'Passive Arm', 'Session', 'Scene',
            'Start', 'End'
        ], nrows)

        if metadata.empty:
            log("Nothing to split.", 1)  # FIXME: print_log
        else:
            # Split videos:
            log(f"Source directory: '{self.input_dir}'", 1)  # FIXME: print_log
            log(f"Splitting videos to '{self.output_dir}'...",
                1)  # FIXME: print_log
            self.split_videos(metadata, self.input_dir, self.get_cameras(),
                              self.output_dir)
            log("Split finished.")  # FIXME: print_log

    def split_videos(self, metadata, input_dir, cameras, output_dir):
        files_properties, _ = load_files_properties(self.output_dir)
        tempdir = tempfile.gettempdir()
        total = len(metadata.index) * len(cameras)
        last_gloss = None

        for row_idx, row in enumerate(metadata.itertuples()):
            gloss = row.Main_New_Gloss if row.Main_New_Gloss else last_gloss
            last_gloss = gloss

            if gloss and row.Session and row.Scene:
                # Important variables:
                sign = remove_special_chars(gloss).lower()
                consultant = remove_special_chars(row.Consultant).lower()
                session = row.Session
                scene = row.Scene
                frame_start = row.Start
                frame_end = row.End

                camera_files = get_camera_files_if_all_matched(
                    session_or_sign=session,
                    scene=scene,
                    cameras=cameras,
                    dir=input_dir)

                for cam_idx, (cam, file) in enumerate(camera_files.items()):
                    tgt_filepath = create_video_name(session_or_sign=sign,
                                                     person=consultant,
                                                     scene=scene,
                                                     camera=cam,
                                                     dir=output_dir)
                    tgt_filename = filename(tgt_filepath)

                    log_progress((len(cameras) * row_idx) + (cam_idx + 1),
                                 total, f"{tgt_filename} ")

                    # Splits only if file is not present:
                    if not exists(tgt_filepath):
                        tmp_filepath = create_video_name(session_or_sign=sign,
                                                         person=consultant,
                                                         scene=scene,
                                                         camera=cam,
                                                         dir=tempdir)

                        log(
                            f"    Segmenting frames "
                            f"[{frame_start:.0f} ~ {frame_end:.0f}] "
                            f"from '{filename(file)}'...", 2)

                        # Split file in temporary diretory:
                        self.split_video(file, tmp_filepath, frame_start,
                                         frame_end, self.fps_in, self.fps_out)

                        # Save file to target directory:
                        shutil.move(tmp_filepath, tgt_filepath)

                    # Save partial labels:
                    files_properties[tgt_filename] = self.create_properties(
                        tgt_filename, sign, gloss, row, cam)
                    save_files_properties(files_properties, self.output_dir)

        return files_properties

    def create_properties(self, file, sign, gloss, row, cam):
        return {
            "file": file,
            "label": sign,
            "gloss": gloss,
            "consultant": row.Consultant,
            "session": row.Session,
            "scene": int(row.Scene),
            "camera": int(cam),
            "frame_start": int(row.Start),
            "frame_end": int(row.End),
            "handshape_dh_start": row.D_Start_HS,
            "handshape_dh_end": row.D_End_HS,
            "handshape_ndh_start": row.N_D_Start_HS,
            "handshape_ndh_end": row.N_D_End_HS,
            "passive_arm": row.Passive_Arm
        }

    def split_video(self, input_file, output_file, start, end, input_fps,
                    output_fps):
        start_sec = self.frame_to_sec(start, input_fps)
        length_sec = self.frame_to_sec(end - start, input_fps)
        self.run_ffmpeg(input_file, output_file, start_sec, length_sec,
                        output_fps)

    def run_ffmpeg(self, src, tgt, start, length, fps):
        assert exists(src), f'Video not found: {src}'
        input_args = {src: None}
        output_args = {
            tgt: [
                '-ss', start, '-t', length, '-r',
                str(fps), '-y', '-loglevel', 'error'
            ]
        }
        ff = ffmpy.FFmpeg(inputs=input_args, outputs=output_args)
        ff.run()

    # def create_target_name(self, sign, person, scene, camera):
    #     return f"{sign:s}-{person:s}-scn{scene:03d}-cam{camera:02d}.mov"

    def frame_to_sec(self, frame, fps):
        res = frame / fps
        secs, milis = divmod(res * 1000, 1000)
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)
        return '%02d:%02d:%02d.%03d' % (hours, mins, secs, milis)
