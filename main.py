#!/usr/bin/env python
from processor.sl.video_preprocessor import VideoPreprocessor
from tools.utils.args_util import Argument, load_args

ARGUMENTS = [
    Argument("-i", "--input_dir", type=str, help="Input directory"),
    Argument('-o', '--output_dir', type=str, help='Output directory'),
    Argument('-w', '--work_dir', type=str, help='Working directory'),
    Argument('-cw', '--clean_workdir', type=bool, help='Clean work dir'),
    Argument('-m', '--metadata_file', type=str, help='Metadata file'),
    Argument('-d', '--debug', type=bool, help='Debug flag'),
    Argument('--save_log', type=bool, default=True, help='Save log'),
    Argument('--print_log', type=bool, default=True, help='Print log'),
    Argument('-ph', '--phases', type=list, help='Phases of pipeline'),
    Argument('-sk', '--skeleton', type=dict, help='Poses configs'),
    Argument('-fi', '--filter', type=dict, help='keypoint configs'),
    Argument('-sp', '--split', type=dict, help='Holdout configs'),
    Argument('-sg', '--segment', type=dict, help='Split configs'),
    Argument('-dl', '--download', type=dict, help='Download configs'),
    Argument('-no', '--normalize', type=dict, help='Data generation configs'),
    Argument('-do', '--debug_opts', type=dict, help='Debug options',
             default={
                 "download_items": 2,
                 "split_items": 5,
                 "pose_items": 3,
                 "gendata_joints": 18
             })
]

if __name__ == '__main__':
    args = load_args('ASLLVD-Skeleton Creator', ARGUMENTS)

    VideoPreprocessor(args).start()
