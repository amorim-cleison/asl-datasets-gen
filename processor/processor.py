from commons.util import (create_if_missing, delete_dir, exists, normpath,
                          save_args)

from utils import ArgsReader


class Processor:
    """
        Base Processor
    """

    def __init__(self, phase_name, args):
        self.args_reader = ArgsReader(args, phase_name)
        self.phase_name = phase_name
        self.work_dir = normpath(self.get_arg("work_dir"))
        self.delete_on_finish = self.get_arg("delete_on_finish", False)

        # Workdir:
        assert (self.work_dir is not None), "Workdir must be informed"
        create_if_missing(self.work_dir)

        # Save args:
        self.session_file = normpath(f"{self.work_dir}/config.yaml")
        if not exists(self.session_file):
            save_args(args, self.session_file)

        # Directories:
        self.input_dir = self.__try_get_as_path("input_dir")
        self.output_dir = self.__try_get_as_path("output_dir")
        if self.output_dir:
            create_if_missing(self.output_dir)

    def __try_get_as_path(self, attr):
        value = self.get_arg(attr)

        if value is not None:
            fullpath = f"{self.work_dir}/{value}"
            path = normpath(fullpath)
        else:
            path = None
        return path

    def get_cameras(self):
        # 'camera 1': front view
        # 'camera 2': side view
        # 'camera 3': facial close up
        mode_cameras = {"2d": [1], "3d": [1, 2]}
        mode = self.get_arg("mode")
        assert (mode is not None) and (
            mode
            in mode_cameras), "There is no camera configuration for this mode"
        return mode_cameras[mode]

    def is_debug(self):
        return self.get_arg("debug", False)

    def get_arg(self, name, default=None):
        return self.args_reader.get_arg(name, default)

    def run(self, metadata):
        pass

    def delete_output_if_enabled(self):
        if self.delete_on_finish and self.output_dir:
            delete_dir(self.output_dir)
