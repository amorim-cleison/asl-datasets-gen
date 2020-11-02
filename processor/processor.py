from commons.util import create_if_missing, exists, save_args, normpath


class Processor:
    """
        Base Processor
    """
    def __init__(self, phase_name, args):
        self.args = args if args is dict else vars(args)
        self.phase_name = phase_name
        self.phase_args = self.args[phase_name]
        self.debug_args = self.get_arg("debug_opts")
        self.work_dir = normpath(self.get_arg("work_dir"))

        # Workdir:
        assert (self.work_dir is not None), "Workdir must be informed"
        create_if_missing(self.work_dir)

        # Save args:
        self.session_file = f"{self.work_dir}/config.yaml"
        if not exists(self.session_file):
            save_args(self.args, self.session_file)

        # Directories:
        self.input_dir = self.__try_get_as_path("input_dir")
        self.output_dir = self.__try_get_as_path("output_dir")
        create_if_missing(self.output_dir)

    def __try_get_as_path(self, attr):
        value = self.get_phase_arg(attr)

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
        return self.args.get(name, self.get_phase_arg(name, default))

    def get_phase_arg(self, name, default=None):
        if (self.phase_args is not None):
            return self.phase_args.get(name, default)
        else:
            return default

    def get_debug_arg(self, name, default=None):
        if (self.debug_args is not None):
            return self.debug_args.get(name, None)
        else:
            return default

    def load_metadata(self, columns, nrows):
        from utils import load_metadata
        return load_metadata(normpath(self.get_arg("metadata_file")),
                             self.get_arg("metadata_url"), columns, nrows)

    def start(self):
        pass
