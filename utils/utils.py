from commons.util import exists, filter_files, replace_special_chars


def create_filename(session_or_sign=None,
                    base=None,
                    scene=None,
                    ext=None,
                    camera=None,
                    uid=None,
                    dir=None):
    from commons.util import normpath

    # assert (session_or_sign is not None), "Session or sign must be informed"
    # assert (scene is not None), "Session must be informed"

    def clean_part(part):
        return replace_special_chars(part, "_").lower()

    # Compose parts:
    parts = []

    if session_or_sign is not None:
        parts.append(f"{clean_part(session_or_sign):s}")

    if base is not None:
        parts.append(f"{base:s}")

    if scene is not None:
        parts.append(f"scn{scene:03.0f}")

    if camera is not None:
        parts.append(f"cam{camera:02.0f}")

    if uid is not None:
        parts.append(f"{uid:05.0f}")

    # Compose file name:
    video_name = "-".join(parts)
    if ext is not None:
        ext = ext if ext.startswith(".") else f".{ext}"
        video_name = f"{video_name}{ext}".lower()
    if dir is not None:
        video_name = normpath(f"{dir}/{video_name}")
    return video_name


def get_camera_files_if_all_matched(session_or_sign,
                                    scene,
                                    cameras,
                                    formats,
                                    person=None,
                                    dir=None):
    """
    Obtain the video files for the cameras, and return only if all camera has
    an equivalent file. Otherwise, returns empty.
    """
    fmt_paths = dict()

    for cam in cameras:
        for fmt in formats:
            path = create_filename(session_or_sign=session_or_sign,
                                   scene=int(scene),
                                   camera=cam,
                                   person=person,
                                   dir=dir,
                                   ext=fmt)
            if exists(path):
                fmt_paths[cam] = {"fmt": fmt, "path": path}
                break

    assert all([cam in fmt_paths for cam in cameras]
               ), "Failed to retrieve camera files"
    return fmt_paths


def get_camera_dirs_if_all_matched(basename,
                                   scene,
                                   cameras,
                                   person=None,
                                   dir=None):
    """
    Obtain the video directories for the cameras, and return only if all
    camera has an equivalent file. Otherwise, returns empty.
    """
    camera_dirs = dict()

    for cam in cameras:
        _dir = create_filename(base=basename,
                               camera=cam,
                               dir=dir)
        filtered = filter_files(dir=_dir, ext="ppm")
        if filtered:
            camera_dirs[cam] = _dir

    assert all([cam in camera_dirs for cam in cameras]
               ), "Failed to retrieve camera directories"
    return camera_dirs


def create_uid(*fields):
    from hashlib import sha1
    SIZE = 6
    data = "-".join([str(x) for x in fields])
    return int(sha1(data.encode("utf-8")).hexdigest(), 16) % (10 ** SIZE)
