#!/usr/bin/env python3
import pandas as pd
from commons.log import log_progress_bar
from commons.util import is_empty
from utils import ArgsReader


class MetadataReader():
    """
        Preprocessor for preparing the metadata information
    """

    def __init__(self, argv=None):
        self.args_reader = ArgsReader(argv, "metadata")

    def load(self):
        debug = self.args_reader.get_arg("debug", False)
        nrows = self.args_reader.get_arg("debug_items") if debug else None

        # Load metadata:
        path = self.args_reader.get_arg("path")
        download_url = self.args_reader.get_arg("download_url")
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

        for row_idx, row in enumerate(metadata.itertuples()):
            log_progress_bar(row_idx + 1, total)

            gloss = row.Main_New_Gloss if not is_empty(
                row.Main_New_Gloss) else last_gloss
            last_gloss = gloss

            if gloss and row.Session and row.Scene:
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
                    "frame_end": int(row.End)
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
        from commons.util import exists, download_file
        if exists(path):
            metadata_ok = True
        else:
            assert (source_url is not None
                    ), "Metadata file is missing; this, URL must be informed."
            metadata_ok = download_file(source_url, path)
        return metadata_ok
