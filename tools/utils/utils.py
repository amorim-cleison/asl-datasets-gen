import re
import pandas as pd
from commons.util import download_file, exists, save_json, read_json
from commons.log import log

METADATA_COLUMNS = [
    'Main New Gloss.1', 'Consultant', 'Session', 'Scene', 'Start', 'End'
]
METADATA_IGNORED_VALUES = ['============', '------------']


def remove_special_chars(text):
    import string
    import re
    special_chars = re.escape(string.punctuation + string.whitespace)
    return re.sub(r'[' + special_chars + ']', '_', text)


def load_metadata(path, source_url, columns=METADATA_COLUMNS, nrows=None):
    if __ensure_metadata(path, source_url):
        if not columns:
            columns = METADATA_COLUMNS

        df = pd.read_excel(path,
                           na_values=METADATA_IGNORED_VALUES,
                           keep_default_na=False,
                           nrows=(nrows * 2))
        df = df[columns]
        df = df.dropna(how='all')
        df = df.where(pd.notnull(df), None)
        df = df.head(nrows)
        norm_columns = {x: remove_special_chars(x) for x in columns}
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


def create_json_name(session_or_sign,
                     scene,
                     camera=None,
                     person=None,
                     dir=None):
    return create_filename(session_or_sign=session_or_sign,
                           scene=scene,
                           camera=camera,
                           ext="json",
                           person=person,
                           dir=dir)


def create_video_name(session_or_sign,
                      scene,
                      camera=None,
                      person=None,
                      dir=None):
    return create_filename(session_or_sign=session_or_sign,
                           scene=scene,
                           camera=camera,
                           ext="mov",
                           person=person,
                           dir=dir)


def create_filename(session_or_sign,
                    scene,
                    ext,
                    camera=None,
                    person=None,
                    dir=None):
    from commons.util import normalize_path
    assert (session_or_sign is not None), "Session or sign must be informed"
    assert (scene is not None), "Session must be informed"

    # Compose parts:
    parts = []
    parts.append(f"{session_or_sign:s}")
    if person is not None:
        parts.append(f"{person:s}")
    parts.append(f"scn{scene:03.0f}")
    if camera is not None:
        parts.append(f"cam{camera:02.0f}")

    # Compose video name:
    video_name = "-".join(parts)
    video_name = f"{video_name}.{ext}"
    if dir is not None:
        video_name = f"{dir}/{video_name}"
    return normalize_path(video_name).lower()


def save_files_properties(files_properties, dir):
    path = f"{dir}/files_properties.json"
    save_json(files_properties, path)


def load_files_properties(dir):
    files_properties = dict()
    labels = list()
    path = f"{dir}/files_properties.json"

    if exists(path):
        files_properties = read_json(path)
        labels = sorted(
            set(value["label"] for _, value in files_properties.items()))
    return files_properties, labels


def get_camera_files_if_all_matched(session_or_sign,
                                    scene,
                                    cameras,
                                    person=None,
                                    dir=None):
    """
    Obtain the video files from the cameras, and return only if all camera has
    an equivalent file. Otherwise, returns empty.
    """
    camera_files = dict()

    for cam in cameras:
        file = create_video_name(session_or_sign=session_or_sign,
                                 scene=int(scene),
                                 camera=cam,
                                 person=person,
                                 dir=dir)
        if exists(file):
            camera_files[cam] = file
    return camera_files if len(camera_files) == len(cameras) else dict()
