from commons.model import Coordinate
from copy import deepcopy


class JsonReader:
    def __init__(self, json, model):
        self._raw = json
        self._model = model

    def get_data(self, person=0) -> list:
        """
        Return the set of coordinates by body part read from JSON data.
        """
        pass


class OpenPoseReader(JsonReader):
    """
    Reader for the `OpenPose` JSON layout
    """
    def get_data(self, person=0):
        data = self._raw["people"][person]
        coordinates = [self.__get_parts_coordinates(data)]
        return {"coordinates": coordinates}

    def __get_parts_coordinates(self, data):
        parts = dict()
        step = 3
        start = 0

        for part, points in self._model.items():
            keypoints = data[f"{part}_keypoints_2d"]
            finish = start + (len(points) * step)
            parts[part] = [
                Coordinate(keypoints[i], keypoints[i + 1], 1, keypoints[i + 2])
                for i in range(start, finish, step)
            ]
        return parts


class AsllvdSkeletonReader(JsonReader):
    """
    Reader for the `ASLLVD Skeleton` JSON layout
    """
    def get_data(self, person=0):
        data = deepcopy(self._raw)
        frames = sorted(data["frames"], key=lambda x: x["frame_index"])
        frames = [self.__get_parts_coordinates(frame) for frame in frames]
        data["frames"] = frames
        return data

    def __get_parts_coordinates(self, frame):
        new_frame = deepcopy(frame)

        for part in self._model["parts"]:
            points = len(new_frame["skeleton"][part]["score"])
            new_frame["skeleton"][part] = {
                new_frame["skeleton"][part]["name"][i]:
                Coordinate(new_frame["skeleton"][part]["x"][i],
                           new_frame["skeleton"][part]["y"][i],
                           new_frame["skeleton"][part]["z"][i],
                           new_frame["skeleton"][part]["score"][i],
                           new_frame["skeleton"][part]["name"][i])
                for i in range(points)
            }
        return new_frame
