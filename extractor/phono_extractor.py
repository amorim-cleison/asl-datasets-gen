class PhonoExtactor():
    def __init__(self, model):
        self._model = model

    def create_result(self, value, score=None):
        from constant import CONFIDENCE_THRESHOLD
        if value:
            if score is None:
                return {"value": value}
            elif score > CONFIDENCE_THRESHOLD:
                return {"value": value, "score": score}

    def extract_attributes(self, data, frame, idx_frame, num_frames,
                           last_frame):
        skeleton = frame["skeleton"]

        def get_hand_attributes(hand, data, skeleton, idx_frame, num_frames,
                                last_frame):
            from constant import HAND_DOMINANCE
            dom = HAND_DOMINANCE[hand]
            movement = None
            orientation = None
            handshape = None

            if self.__has_handshape_action(hand, data):
                movement = self.get_hand_movement(hand, skeleton, last_frame)
                orientation = self.get_palm_orientation(hand, skeleton)
                handshape = self.get_hand_shape(hand, data, idx_frame,
                                                num_frames)

            return {
                f"movement_{dom}": movement,
                f"orientation_{dom}": orientation,
                f"handshape_{dom}": handshape
            }

        attributes = dict()
        attributes.update(
            get_hand_attributes("hand_right", data, skeleton, idx_frame,
                                num_frames, last_frame))
        attributes.update(
            get_hand_attributes("hand_left", data, skeleton, idx_frame,
                                num_frames, last_frame))
        attributes.update(
            {"non_manual": {
                "mouth_opening": self.get_mouth_opening(skeleton)
            }})
        return attributes

    def get_hand_shape(self, hand, data, frame_idx, num_frames):
        """
        Obtain the handshape of the hand, based on the provided `data`.
        """
        from constant import HAND_HANDSHAPE

        def get_shape(data, frame_idx, names):
            return data[names["start"]] \
                if (frame_idx <= (num_frames / 2)) \
                else data[names["end"]]

        if hand not in HAND_HANDSHAPE:
            raise Exception("Unknown hand")
        shape = get_shape(data, frame_idx, HAND_HANDSHAPE[hand])
        return self.create_result(shape)

    def get_hand_movement(self, hand, keypoints, last_keypoints):
        """
        Calculate movement in space and return one (or the combination of more
        than one) of the options:
        - right
        - left
        - up
        - down
        - front
        - back
        """
        from constant import MOVE_THRESHOLD, DIRECTIONS
        hand_keypoints = keypoints[hand]
        hand_last_keypoints = last_keypoints[hand] if last_keypoints else None

        if hand_keypoints and hand_last_keypoints:
            # displacement = hand_keypoints["wrist"] - \
            #     hand_last_keypoints["wrist"]
            displacement = (hand_keypoints["middle_finger_base"] -
                            hand_last_keypoints["middle_finger_base"])\
                .to_normalized()
            direction = self._get_directions(displacement, DIRECTIONS,
                                             MOVE_THRESHOLD)
            score = displacement.score
            return self.create_result("_".join(direction), score)

    def get_palm_orientation(self, hand, keypoints):
        """
        Calculate palm orientation and return one (or the combination of more
        than one) of the options:
        - right
        - left
        - up
        - down
        - front
        - back
        """
        from constant.constants import DIRECTIONS, ORIENTATION_THRESHOLD
        hand_keypoints = keypoints[hand]

        if hand_keypoints:
            # Calculation is made by find the normal vector of the plane defined by
            # three main hand keypoints (fist, base of the pinky finger, and base
            # of the index finger).
            # Normal vector is defined as the cross product between two vectors in
            # the plane.
            # https://mathinsight.org/forming_planes
            # https://mathinsight.org/forming_plane_examples
            wrist = hand_keypoints["wrist"]
            index_base = hand_keypoints["index_finger_base"]
            pinky_base = hand_keypoints["pinky_base"]

            if hand == "hand_right":
                b = wrist - pinky_base
                c = wrist - index_base
            elif hand == "hand_left":
                b = wrist - index_base
                c = wrist - pinky_base
            else:
                raise Exception("Unknown hand")

            normal = b.cross_product(c).to_normalized()
            direction = self._get_directions(normal, DIRECTIONS,
                                             ORIENTATION_THRESHOLD)
            score = normal.score
            return self.create_result("_".join(direction), score)

    def _get_directions(self, vector, names, threshold=0.0):
        def calculate_move(value, labels):
            INDEXES = NEGATIVE, POSITIVE = 0, 1
            assert len(labels) == len(INDEXES), "Invalid labels size."

            direction = list()
            if value > threshold:
                direction.append(labels[POSITIVE])
            elif value < (threshold * -1):
                direction.append(labels[NEGATIVE])
            else:
                pass
            return direction

        # Select only the most significant axis:
        # import numpy as np
        # values = vector.to_tuple()
        # argmax = np.argmax(np.abs(values))
        # axis = list(names.keys())[argmax]
        # directions = calculate_move(values[argmax], names[axis])

        # Warning: labels must consider "mirrored" interpretation due
        # to the target user's (inside video) perspective axes.
        directions = list()
        directions.extend(calculate_move(vector.x, names["x"]))
        directions.extend(calculate_move(vector.y, names["y"]))
        directions.extend(calculate_move(vector.z, names["z"]))
        return directions

    def get_mouth_opening(self, keypoints):
        """
        Calculate the degree of `openness` for the mouth.
        """
        from statistics import mean
        """
        Check calculation in the paper:
        'Normal growth and development of the lips : a 3-dimensional
        study from 6 years to adulthood using a geometric model'
        (VIRGILIO F. FERRARIO, CHIARELLA SFORZA, JOHANNES H. SCHMITZ, VERONICA CIUSA
        AND ANNA COLOMBO), Pg. 3
        """
        face_keypoints = keypoints["face"]

        if face_keypoints:
            ch_l = face_keypoints["lips_outer_left"]  # cheilion left
            ch_r = face_keypoints["lips_outer_right"]  # cheilion left
            ls = face_keypoints["lips_outer_top"]  # labiale superius
            li = face_keypoints["lips_outer_bottom"]  # labiale inferius

            mouth_width = ch_l.dist_to(ch_r)  # mouth width = ch_r - ch_l
            vermilion_height = li.dist_to(ls)  # vermilion height = ls - li

            vermilion_height_to_mouth_width = vermilion_height / mouth_width
            score = mean([ch_l.score, ch_r.score, ls.score, li.score])

            # TODO: test the calculation above
            return self.create_result(vermilion_height_to_mouth_width, score)

    def __has_handshape_action(self, hand, data):
        from constant import HAND_HANDSHAPE
        handshape = HAND_HANDSHAPE[hand]
        return data[handshape["start"]] or data[handshape["end"]]
