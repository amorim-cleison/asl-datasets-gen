from tools.utils.util import import_class

from .preprocessor.io import IO


class VideoPreprocessor(IO):
    def __init__(self, args=None):
        self.arg = args
        super().__init__(self.arg)

    def start(self):
        workdir = self.arg.work_dir

        # Clean workdir:
        if self.arg.clean_workdir:
            self.remove_dir(workdir)
            self.create_dir(workdir)

        phases = self.get_phases()

        # Run pipeline:
        for name, phase in phases.items():
            if name in self.arg.phases:
                self.print_phase(name)
                phase(self.arg).start()

        # Remove workdir:
        # if self.arg.clean_workdir:
        #     self.remove_dir(workdir)

        self.print_log("\nDONE")

    def get_phases(self):
        return dict(
            download=import_class(
                'processor.sl.preprocessor.downloader.Downloader_Preprocessor'
            ),
            segment=import_class(
                'processor.sl.preprocessor.splitter.Splitter_Preprocessor'),
            skeleton=import_class(
                'processor.sl.preprocessor.openpose.OpenPose_Preprocessor'),
            filter=import_class(
                'processor.sl.preprocessor.keypoint.Keypoint_Preprocessor'),
            split=import_class(
                'processor.sl.preprocessor.holdout.Holdout_Preprocessor'),
            normalize=import_class(
                'processor.sl.preprocessor.gendata.Gendata_Preprocessor'))

    def print_phase(self, name):
        self.print_log("")
        self.print_log("-" * 60)
        self.print_log(name.upper())
        self.print_log("-" * 60)
