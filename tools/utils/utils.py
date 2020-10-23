import pandas as pd
from commons.util import download_file, exists
from commons.log import log

METADATA_COLUMNS = [
    'Main New Gloss.1', 'Consultant', 'Session', 'Scene', 'Start', 'End'
]
METADATA_IGNORED_VALUES = ['============', '------------']


def load_metadata(path, source_url, columns=METADATA_COLUMNS, nrows=None):
    import string
    import re

    def norm_column_name(name):
        special_chars = re.escape(string.punctuation + string.whitespace)
        return re.sub(r'[' + special_chars + ']', '_', name)

    if __ensure_metadata(path, source_url):
        if not columns:
            columns = METADATA_COLUMNS

        df = pd.read_excel(path,
                           na_values=METADATA_IGNORED_VALUES,
                           keep_default_na=False)
        df = df[columns]
        df = df.dropna(how='all')
        df = df.head(nrows)
        norm_columns = {x: norm_column_name(x) for x in columns}
        df = df.rename(index=str, columns=norm_columns)
        return df


def __ensure_metadata(path, source_url):
    if exists(path):
        metadata_ok = True
    else:
        assert (source_url is not None
                ), "Metadata file is missing; this, URL must be informed."
        metadata_ok = download_file(source_url, path)
    return metadata_ok


def progress_bar(current, total, message=None, overwritable=False):
    increments = 50
    percentual = ((current / total) * 100)
    i = int(percentual // (100 / increments))
    prefix = "{} ".format(message) if message else ""
    text = "\r{}|{: <{}}| {:.0f}%".format(prefix, '█' * i, increments,
                                          percentual)

    if overwritable:
        end = "\r"
    elif percentual >= 100:
        end = "\n"
    else:
        end = ""
    log(text, 1, end=end)


def create_filename(file_pattern, session, scene):
    return file_pattern.format(session=session,
                               scene=int(scene),
                               camera=1)
