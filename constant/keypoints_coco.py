from .constants import PART_BODY, PART_FACE, PART_HAND_LEFT, PART_HAND_RIGHT

KEYPOINTS_COCO = {
    PART_BODY: [
        "nose",
        "neck",
        "shoulder_right",
        "elbow_right",
        "wrist_right",
        "shoulder_left",
        "elbow_left",
        "wrist_left",
        "hip_right",
        "knee_right",
        "ankle_right",
        "hip_left",
        "knee_left",
        "ankle_left",
        "eye_right",
        "eye_left",
        "ear_right",
        "ear_left"
    ],
    PART_FACE: [
        # Face contour:
        "face_contour_right",
        "face_contour_right_1"
        "face_contour_right_2",
        "face_contour_right_3",
        "face_contour_right_4",
        "face_contour_right_5",
        "face_contour_right_6",
        "face_chin_1",
        "face_chin_2",
        "face_chin_3",
        "face_contour_left_1",
        "face_contour_left_2",
        "face_contour_left_3",
        "face_contour_left_4",
        "face_contour_left_5",
        "face_contour_left_6",
        "face_contour_left",

        # Right eyebrow:
        "eyebrow_right_corner_right",
        "eyebrow_right_top_1",
        "eyebrow_right_top",
        "eyebrow_right_top_2",
        "eyebrow_right_corner_left",

        # Left eyebrow:
        "eyebrow_left_corner_right",
        "eyebrow_left_top_1",
        "eyebrow_left_top",
        "eyebrow_left_top_2",
        "eyebrow_left_corner_left",

        # Nose:
        "nose_top",
        "nose_middle_1",
        "nose_middle_2",
        "nose_middle_3",
        "nose_bottom_1",
        "nose_bottom_2",
        "nose_bottom",
        "nose_bottom_3",
        "nose_bottom_4",

        # Left eye:
        "eye_left_corner_right",
        "eye_left_top_1",
        "eye_left_top_2",
        "eye_left_corner_left",
        "eye_left_bottom_1",
        "eye_left_bottom_2",

        # Right eye:
        "eye_right_corner_right",
        "eye_right_top_1",
        "eye_right_top_2",
        "eye_right_corner_left",
        "eye_right_bottom_1",
        "eye_right_bottom_2",

        # Outer lips:
        "lips_outer_right",
        "lips_outer_top_1",
        "lips_outer_top_2",
        "lips_outer_top",
        "lips_outer_top_3",
        "lips_outer_top_4",
        "lips_outer_left",
        "lips_outer_bottom_1",
        "lips_outer_bottom_2",
        "lips_outer_bottom",
        "lips_outer_bottom_3",
        "lips_outer_bottom_4",

        # Inner lips:
        "lips_inner_right",
        "lips_inner_top_1",
        "lips_inner_top",
        "lips_inner_top_2",
        "lips_inner_left",
        "lips_inner_bottom_1",
        "lips_inner_bottom",
        "lips_inner_bottom_2",

        # Eye balls:
        "eye_ball_right",
        "eye_ball_left",
    ],
    PART_HAND_LEFT: [
        "wrist",

        # Thumb:
        "thumb_base",
        "thumb_joint_1",
        "thumb_joint_2",
        "thumb_tip",

        # Index finger:
        "index_finger_base",
        "index_finger_joint_1",
        "index_finger_joint_2",
        "index_finger_tip",

        # Middle finger:
        "middle_finger_base",
        "middle_finger_joint_1",
        "middle_finger_joint_2",
        "middle_finger_tip",

        # Ring finger:
        "ring_finger_base",
        "ring_finger_joint_1",
        "ring_finger_joint_2",
        "ring_finger_tip",

        # Pinky:
        "pinky_base",
        "pinky_joint_1",
        "pinky_joint_2",
        "pinky_tip",
    ],
    PART_HAND_RIGHT: [
        "wrist",

        # Thumb:
        "thumb_base",
        "thumb_joint_1",
        "thumb_joint_2",
        "thumb_tip",

        # Index finger:
        "index_finger_base",
        "index_finger_joint_1",
        "index_finger_joint_2",
        "index_finger_tip",

        # Middle finger:
        "middle_finger_base",
        "middle_finger_joint_1",
        "middle_finger_joint_2",
        "middle_finger_tip",

        # Ring finger:
        "ring_finger_base",
        "ring_finger_joint_1",
        "ring_finger_joint_2",
        "ring_finger_tip",

        # Pinky:
        "pinky_base",
        "pinky_joint_1",
        "pinky_joint_2",
        "pinky_tip",
    ]
}
