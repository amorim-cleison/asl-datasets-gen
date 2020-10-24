from commons.util import create_if_missing, exists, save_args


class Processor:
    """
        Base Processor
    """
    def __init__(self, phase_name, args=None):
        self.args = args
        self.phase_name = phase_name
        self.phase_args = self.args.__getattribute__(phase_name)
        self.work_dir = self.args.work_dir

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
        from os.path import realpath

        if attr in self.phase_args:
            value = self.phase_args[attr]
            fullpath = f"{self.work_dir}/{value}"
            path = realpath(fullpath)
        else:
            path = None
        return path

    def start(self):
        pass
