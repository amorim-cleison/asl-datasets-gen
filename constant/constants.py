PART_BODY = "body"
PART_FACE = "face"
PART_HAND_LEFT = "hand_left"
PART_HAND_RIGHT = "hand_right"

PARTS_OPENPOSE_MAPPING = {
    "pose_keypoints_2d": PART_BODY,
    "face_keypoints_2d": PART_FACE,
    "hand_left_keypoints_2d": PART_HAND_LEFT,
    "hand_right_keypoints_2d": PART_HAND_RIGHT
}

PARTS = PARTS_OPENPOSE_MAPPING.values()

# -------------------------------------------------------------------
# PHONOLOGY:
# -------------------------------------------------------------------

MOVE_THRESHOLD = 0.30
ORIENTATION_THRESHOLD = 0.30
CONFIDENCE_THRESHOLD = 0.15

# Directions, according to user's perspective.
# Index are: [negative, positive].
DIRECTIONS = {
    "x": ["right", "left"],
    "y": ["up", "down"],
    "z": ["body", "front"]
}

HAND_DOMINANCE = {"hand_right": "dh", "hand_left": "ndh"}

HAND_HANDSHAPE = {
    "hand_right": {
        "start": f"handshape_{HAND_DOMINANCE['hand_right']}_start",
        "end": f"handshape_{HAND_DOMINANCE['hand_right']}_end"
    },
    "hand_left": {
        "start": f"handshape_{HAND_DOMINANCE['hand_left']}_start",
        "end": f"handshape_{HAND_DOMINANCE['hand_left']}_end"
    }
}
# -------------------------------------------------------------------
