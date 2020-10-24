from commons.log import log
from commons.util import create_if_missing, delete_dir, Argument, load_args

import processor as p


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
    Argument('-fi', '--filter', type=dict, help='Keypoint configs'),
    Argument('-sp', '--split', type=dict, help='Holdout configs'),
    Argument('-sg', '--segment', type=dict, help='Split configs'),
    Argument('-dl', '--download', type=dict, help='Download configs'),
    Argument('-no', '--normalize', type=dict, help='Data generation configs'),
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
    "filter": p.Filter,
    "split": p.Holdouter,
    # FIXME: enable this again
    # "normalize": pp.Normalizer
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
