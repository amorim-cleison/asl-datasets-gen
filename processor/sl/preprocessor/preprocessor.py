from commons.util import create_if_missing, exists
from tools.utils import save_args


class Preprocessor:
    """
        Base Processor
    """
    def __init__(self, phase_name, args=None):
        super().__init__(args)
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
            save_args(vars(self.args), self.session_file)

        # Directories:
        self.input_dir = self.__get_path(self.work_dir,
                                         self.phase_args['input_dir'])
        self.output_dir = self.__get_path(self.work_dir,
                                          self.phase_args['output_dir'])
        create_if_missing(self.output_dir)

    def __get_path(self, work_dir, path):
        from os.path import realpath
        assert (work_dir is not None), "Workdir must be informed"
        assert (path is not None), "Path must be informed"
        fullpath = f"{work_dir}/{path}"
        return realpath(fullpath)

    def start(self):
        pass
