from commons.util import (replace_special_chars, filter_files)


def create_filename(session_or_sign,
                    scene,
                    ext=None,
                    camera=None,
                    person=None,
                    dir=None):
    from commons.util import normpath
    assert (session_or_sign is not None), "Session or sign must be informed"
    assert (scene is not None), "Session must be informed"

    def clean_part(part):
        return replace_special_chars(part, "_").lower()

    # Compose parts:
    parts = []
    parts.append(f"{clean_part(session_or_sign):s}")
    if person is not None:
        parts.append(f"{clean_part(person):s}")
    parts.append(f"scn{scene:03.0f}")
    if camera is not None:
        parts.append(f"cam{camera:02.0f}")

    # Compose file name:
    video_name = "-".join(parts)
    if ext is not None:
        ext = ext if ext.startswith(".") else f".{ext}"
        video_name = f"{video_name}{ext}"
    if dir is not None:
        video_name = normpath(f"{dir}/{video_name}")
    return video_name.lower()


def get_camera_files_if_all_matched(session_or_sign,
                                    scene,
                                    cameras,
                                    person=None,
                                    dir=None):
    """
    Obtain the video files for the cameras, and return only if all camera has
    an equivalent file. Otherwise, returns empty.
    """
    camera_files = dict()

    for cam in cameras:
        file = create_filename(session_or_sign=session_or_sign,
                               scene=int(scene),
                               camera=cam,
                               person=person)
        filtered = filter_files(dir=dir, name=file)
        if filtered:
            camera_files[cam] = filtered[0]
    return camera_files if len(camera_files) == len(cameras) else dict()


def get_camera_dirs_if_all_matched(session_or_sign,
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
        _dir = create_filename(session_or_sign=session_or_sign,
                               scene=int(scene),
                               camera=cam,
                               person=person,
                               dir=dir)
        filtered = filter_files(dir=_dir, ext="ppm")
        if filtered:
            camera_dirs[cam] = _dir
    return camera_dirs if len(camera_dirs) == len(cameras) else dict()
