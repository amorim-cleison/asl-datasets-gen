#!/usr/bin/env python3
import pandas as pd
from commons.log import auto_log_progress
from commons.util import is_empty, normpath
from utils import create_filename, create_uid

from .processor import Processor


class Metadator(Processor):
    """
        Preprocessor for preparing the metadata information
    """

    def __init__(self, argv=None):
        super().__init__('metadata', argv)

    def run(self):
        nrows = self.get_arg(
            "debug_items") if self.is_debug() else None

        # Load metadata:
        path = normpath(self.get_arg("path"))
        download_url = self.get_arg("download_url")
        columns = [
            'Main New Gloss', 'Consultant', 'D Start HS', 'N-D Start HS',
            'D End HS', 'N-D End HS', 'Passive Arm', 'Session', 'Scene',
            'Start', 'End'
        ]
        metadata_rows = self.load_metadata(path, download_url, columns, nrows)

        # Process metadata:
        if not metadata_rows.empty:
            return self.process_metadata(metadata_rows, self.get_cameras())

    def process_metadata(self, metadata, cameras):
        all_rows = list()
        total = len(metadata.index)
        last_gloss = None
        uids = set()

        for row_idx, row in auto_log_progress(enumerate(metadata.itertuples()), total=total):
            gloss = row.Main_New_Gloss if not is_empty(
                row.Main_New_Gloss) else last_gloss
            last_gloss = gloss

            if gloss and row.Session and row.Scene:
                uid = create_uid(gloss, row.Consultant, row.Session,
                                 row.Scene, row.Start, row.End)
                basename = create_filename(session_or_sign=gloss, uid=uid)

                # Validate if already exists:
                if basename in uids:
                    raise Exception("Duplicated UID")
                else:
                    uids.add(basename)

                new_row = {
                    "label": self.create_label(gloss),
                    "gloss": gloss,
                    "consultant": row.Consultant,
                    "d_start_hs": row.D_Start_HS,
                    "nd_start_hs": row.N_D_Start_HS,
                    "d_end_hs": row.D_End_HS,
                    "nd_end_hs": row.N_D_End_HS,
                    "passive_arm": row.Passive_Arm,
                    "session": row.Session,
                    "scene": int(row.Scene),
                    "frame_start": int(row.Start),
                    "frame_end": int(row.End),
                    "basename": basename
                }
                all_rows.append(new_row)
        return pd.DataFrame(all_rows)

    def create_label(self, gloss):
        from commons.util import replace_special_chars
        label = replace_special_chars(gloss, "_")

        while label.startswith("_"):
            label = label[1:]
        while label.endswith("_"):
            label = label[:-1]
        return label.lower()

    def load_metadata(self, path, source_url, columns, nrows=None):
        from commons.util import replace_special_chars

        METADATA_IGNORED_VALUES = ['============', '------------']

        if self.__ensure_metadata(path, source_url):
            assert (columns is not None), "You must inform the `columns`"

            df = pd.read_excel(path,
                               na_values=METADATA_IGNORED_VALUES,
                               keep_default_na=False,
                               nrows=(nrows * 2) if (nrows is not None) else None)
            df = df[columns]
            df = df.dropna(how='all')
            df = df.where(pd.notnull(df), None)

            if (nrows is not None):
                df = df.head(nrows)
            norm_columns = {x: replace_special_chars(x, "_") for x in columns}
            df = df.rename(index=str, columns=norm_columns)
            return df

    def __ensure_metadata(self, path, source_url):
        import shutil
        import tempfile

        from commons.util import download_file, exists

        if exists(path):
            metadata_ok = True
        else:
            assert (source_url is not None
                    ), "Metadata file is missing; this, URL must be informed."
            tmp_path = normpath(f"{tempfile.gettempdir()}/metadata.partial")
            success, e = download_file(source_url, tmp_path)

            if success:
                shutil.move(tmp_path, path)
                metadata_ok = True
            else:
                self.log_failed(e)
        return metadata_ok
