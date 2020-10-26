import copy

PARTS_MAPPING = {
    "pose_keypoints_2d": "body",
    "face_keypoints_2d": "face",
    "hand_left_keypoints_2d": "hand_left",
    "hand_right_keypoints_2d": "hand_right"
}


def pack_snippets(cams_snippets, properties, mode="2d"):
    assert (mode is not None), "`Mode` must be informed"

    def validate_mapping(cams_snippets, required_size, mode):
        assert (
            len(cams_snippets) == required_size
        ), f"Camera x snippets mapping size is not compatible with '{mode}' mode"

    if mode == "2d":
        validate_mapping(cams_snippets, 1, mode)
        frames = __read_frames(cams_snippets[1])
    elif mode == "3d":
        validate_mapping(cams_snippets, 2, mode)
        frames_cam1 = __read_frames(cams_snippets[1])
        frames_cam2 = __read_frames(cams_snippets[2])
        frames = __merge_into_3d(frames_cam1, frames_cam2)
    else:
        frames = []

    packed_data = copy.deepcopy(properties)
    packed_data["frames"] = frames
    return packed_data


def __merge_into_3d(frames_cam1, frames_cam2):
    assert (len(frames_cam1) == len(frames_cam2)
            ), "The length of the frames from camera 1 and 2 must be equal."
    merged_frames = list()

    for frame_cam1, frame_cam2 in zip(frames_cam1, frames_cam2):
        frame = copy.deepcopy(frame_cam1)

        for part in PARTS_MAPPING.values():
            frame[part]["z"] = frame_cam2[part]["x"]
            frame[part]["score"] = [
                (score_cam1 + score_cam2) / 2
                for (score_cam1, score_cam2) in zip(frame_cam1[part]["score"],
                                                    frame_cam2[part]["score"])
            ]
        merged_frames.append(frame)
    return merged_frames


def __read_frames(snippets):
    from commons.util import read_json, filename
    frames = list()

    def get_frame_index(path):
        return int(filename(path, False).split("_")[1])

    for path in snippets:
        data = read_json(path)
        frame = {'frame_index': get_frame_index(path)}

        # Consider only first person:
        person = data['people'][0]

        for src_part, tgt_part in PARTS_MAPPING.items():
            frame[tgt_part] = __read_coordinates(person[src_part])
        frames.append(frame)
    return frames


def __read_coordinates(keypoints):
    x = list()
    y = list()
    score = list()

    for i in range(0, len(keypoints), 3):
        x.append(keypoints[i])
        y.append(keypoints[i + 1])
        score.append(keypoints[i + 2])
    return {"score": score, "x": x, "y": y}
