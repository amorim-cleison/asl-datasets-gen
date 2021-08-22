from commons.model import Coordinate
from copy import deepcopy


class JsonReader:
    def __init__(self, json, parts):
        self._raw = json
        self._parts = parts

    def get_data(self, person=0) -> list:
        """
        Return the set of coordinates by body part read from JSON data.
        """
        pass


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

        def get_property(new_frame, part, prop, i):
            return (new_frame["skeleton"][part][prop][i]) if (
                prop in new_frame["skeleton"][part]) else None

        if "skeleton" in new_frame:
            for part in self._parts:
                points = len(new_frame["skeleton"][part]["score"])
                new_frame["skeleton"][part] = {
                    new_frame["skeleton"][part]["name"][i]:
                    Coordinate(get_property(new_frame, part, "x", i),
                               get_property(new_frame, part, "y", i),
                               get_property(new_frame, part, "z", i),
                               get_property(new_frame, part, "score", i),
                               get_property(new_frame, part, "name", i))
                    for i in range(points)
                }
        return new_frame
