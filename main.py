from commons.log import log
from commons.util import create_if_missing, delete_dir, Argument, load_args

import processor as p


ARGUMENTS = [
    Argument('-w', '--work_dir', type=str, required=True, help='Working directory'),
    Argument('-cw', '--clean_workdir', type=bool, help='Clean work dir'),
    Argument('-e', '--metadata_file', type=str, help='Metadata file'),
    Argument('-eu', '--metadata_url', type=str, help='Metadata URL'),
    Argument('-fp', '--file_pattern', type=str, help='Filename pattern'),
    Argument('-d', '--debug', type=bool, help='Debug flag'),
    Argument('-m', '--mode', options=["2d", "3d"], default="2d",
             help='Extraction mode'),
    Argument('--print_log', type=bool, default=True, help='Print log'),
    Argument('-ph', '--phases', type=list, help='Phases of pipeline'),
    Argument('-sk', '--skeleton', type=dict, help='Poses configs'),
    Argument('-sg', '--segment', type=dict, help='Split configs'),
    Argument('-dl', '--download', type=dict, help='Download configs'),
    Argument('-no', '--normalize', type=dict, help='Normalization configs'),
    Argument('-do',
             '--debug_opts',
             type=dict,
             help='Debug options',
             default={
                 "download_items": 2,
                 "split_items": 5,
                 "pose_items": 3,
                 "gendata_joints": 18
             })
]

PHASES = {
    "download": p.Downloader,
    "segment": p.Segmenter,
    "skeleton": p.Skeletor,
    "normalize": p.Normalizer
}


def run(args):
    workdir = args.work_dir

    # Clean workdir:
    if args.clean_workdir:
        delete_dir(workdir)
        create_if_missing(workdir)

    # Run pipeline:
    for name, phase in PHASES.items():
        if name in args.phases:
            print_phase(name)
            phase(args).start()

    # Remove workdir:
    # if self.arg.clean_workdir:
    #     self.remove_dir(workdir)

    log("\nDONE", 1)


def print_phase(name):
    log("", 1)
    log("-" * 60, 1)
    log(name.upper(), 1)
    log("-" * 60, 1)


if __name__ == '__main__':
    args = load_args('ASLLVD-Skeleton Creator', ARGUMENTS)
    run(args)
