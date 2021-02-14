from commons.util import (create_if_missing, exists, normpath,
                          save_args)
from commons.log import log, log_err

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
        MODE_CAMERAS = {"2d": [1], "3d": [1, 2]}
        mode = self.get_arg("mode")
        assert (mode is not None)
        cameras = list()

        for m in mode:
            assert (
                m in MODE_CAMERAS), f"There is no camera configuration for the mode `{m}`"
            cameras.extend(MODE_CAMERAS[m])
        return set(cameras)

    def is_debug(self):
        return self.get_arg("debug", False)

    def get_arg(self, name, default=None):
        return self.args_reader.get_arg(name, default)

    def run(self, group, rows):
        pass

    def log_skipped(self):
        log("    Skipped")

    def log_failed(self, e):
        log_err(f"   FAILED ({str(e)})", ex=e)

    def __get_del_path(self, path):
        path = normpath(path, path_as_str=False)
        return normpath(f"{path.parent}/{path.stem}.del")

    def output_exists(self, path):
        del_path = self.__get_del_path(path)
        return exists(path) or exists(del_path)

    def delete_output_if_enabled(self):
        from commons.util import filter_files, save_items, delete_file

        if self.delete_on_finish and self.output_dir:
            all_files = set(filter_files(self.output_dir))
            del_files = set(filter_files(self.output_dir, ext="del"))
            new_files = all_files - del_files

            for f in new_files:
                del_path = self.__get_del_path(f)
                save_items([], del_path)
                delete_file(f)
