from commons.log import log, log_progress
from commons.util import Argument, create_if_missing, load_args

import processor as p

ARGUMENTS = [
    Argument('-w', '--work_dir', type=str,
             required=True, help='Working directory'),
    Argument('-d', '--debug', type=bool, help='Debug flag'),
    Argument('-f', '--fps_out', type=int, help='Output frames per second'),
    Argument('-m', '--mode', options=["2d", "3d"], default="2d",
             help='Extraction mode'),
    Argument('-ph', '--phases', type=list, help='Phases of pipeline'),
    Argument('-sk', '--skeleton', type=dict, help='Poses configs'),
    Argument('-sg', '--segment', type=dict, help='Split configs'),
    Argument('-dl', '--download', type=dict, help='Download configs'),
    Argument('-no', '--normalize', type=dict, help='Normalization configs'),
    Argument('-me', '--metadata', type=dict, help='Metadata configs')
]

PHASES = {
    "download": p.Downloader,
    "segment": p.Segmenter,
    "skeleton": p.Skeletor,
    "normalize": p.Normalizer
}


def run(args):
    print_args(args)

    # Create work dir:
    workdir = args.work_dir
    create_if_missing(workdir)

    # Load metadata:
    metadata = load_metadata(args)
    metadata = metadata.groupby(["session", "scene"])

    last_processor = None
    total = len(metadata)

    # Iterates per groups of session x scene to optimize storage consumption,
    # by processing files in batch of those groups.
    # Every .vid file requires at least 1GB of disk space, and here we dispose
    # them as soon as we finish the process of the stage.
    for idx, ((session, scene), rows) in enumerate(metadata):
        # Retrieve progress:
        _, group_phases = load_group_progress(workdir, session, scene)
        print_group(idx, total, session, scene)

        # Run pipeline:
        for name, phase in group_phases.items():
            processor = phase(args)
            print_phase(name, processor)
            processor.run(rows)

            # Update progress:
            append_group_progress(workdir, session, scene, name)

            # Delete the output of the last phase, if enabled:
            if last_processor:
                last_processor.delete_output_if_enabled()
            last_processor = processor
    log("\nDONE", 1)


def load_group_progress(workdir, session, scene):
    from commons.util import normpath, read_json, exists

    # Load progress:
    path = normpath(f"{workdir}/progress.json")
    progress = read_json(path) if exists(path) else dict()

    # Retrieve group details:
    group_key = f"{session}-{scene}"
    group_progress = progress[group_key] if (group_key in progress) else list()
    group_phases = {n: p for n, p in PHASES.items() if (
        n in args.phases) and (n not in group_progress)}
    return group_progress, group_phases


def append_group_progress(workdir, session, scene, new_phase):
    from commons.util import normpath, read_json, exists, save_json

    # Load current progress:
    path = normpath(f"{workdir}/progress.json")
    progress = read_json(path) if exists(path) else dict()

    # Update group progress:
    group_key = f"{session}-{scene}"
    group_progress = progress[group_key] if (group_key in progress) else list()
    group_progress.append(new_phase)

    # Save progress:
    progress[group_key] = group_progress
    save_json(progress, path)


def load_metadata(args):
    log("\nLoading metadata...")
    processor = p.Metadator(args)
    return processor.run()


def print_group(idx, total, session, scene):
    log("", 1)
    log("=" * 60, 1)
    log_progress(idx + 1, total,
                 f"Session '{session}' | Scene '{scene}'".upper())
    log("-" * 60, 1)


def print_phase(name, processor):
    log(f"-> {name.capitalize()}", 1)


def print_processing():
    log("", 1)
    log("=" * 60, 1)
    log("PROCESSING:")
    log("-" * 60, 1)


def print_args(args):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    log("", 1)
    log("=" * 60, 1)
    log("ARGUMENTS:")
    log("-" * 60, 1)
    log(pp.pformat(vars(args)))
    log("-" * 60, 1)


if __name__ == '__main__':
    args = load_args('ASLLVD-Skeleton Creator', ARGUMENTS)
    run(args)
