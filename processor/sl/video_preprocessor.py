import processor.sl.preprocessor as pp

from commons.util import delete_dir, create_if_missing
from commons.log import log


class VideoPreprocessor:

    PHASES = {
        "download": pp.Downloader,
        "segment": pp.Segmenter,
        "skeleton": pp.Skeletor,
        "filter": pp.Filter,
        "split": pp.Holdouter,
        "normalize": pp.Normalizer
    }

    def __init__(self, args=None):
        self.arg = args
        super().__init__(self.arg)

    def start(self):
        workdir = self.arg.work_dir

        # Clean workdir:
        if self.arg.clean_workdir:
            delete_dir(workdir)
            create_if_missing(workdir)

        # Run pipeline:
        for name, phase in self.PHASES.items():
            if name in self.arg.phases:
                self.print_phase(name)
                phase(self.arg).start()

        # Remove workdir:
        # if self.arg.clean_workdir:
        #     self.remove_dir(workdir)

        log("\nDONE", 1)

    def print_phase(self, name):
        log("", 1)
        log("-" * 60, 1)
        log(name.upper(), 1)
        log("-" * 60, 1)
