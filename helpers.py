from enum import Enum

INIT_WIDTH = 900
INIT_HEIGHT = 800


class ActionType(Enum):
    STAY = "stay"
    MOVE = "move"
    BUILD = "build"
    DESTROY = "destroy"


class ActionParam(Enum):
    pass


class MoveType(ActionParam, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UPPER_LEFT = "upper_left"
    UPPER_RIGHT = "upper_right"
    LOWER_LEFT = "lower_left"
    LOWER_RIGHT = "lower_right"


class BuildAndDestroyType(Enum):
    ABOVE = "above"
    BELOW = "below"
    LEFT = "left"
    RIGHT = "right"


class Side(Enum):
    A = "A"
    B = "B"
