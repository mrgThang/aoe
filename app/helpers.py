from enum import Enum, IntEnum

INIT_WIDTH = 1100
INIT_HEIGHT = 800
INFO_BOARD_WIDTH = 300

NEUTRAL_COLOR = "white"
POND_COLOR = "black"
BORDER_COLOR = 'red'
CHOOSE_COLOR = 'yellow'
WALL_A_COLOR = '#ADD8E6'
WALL_B_COLOR = 'pink'


class ActionType(str, Enum):
    STAY = "STAY"
    MOVE = "MOVE"
    BUILD = "BUILD"
    DESTROY = "DESTROY"


class MoveType(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UPPER_LEFT = "UPPER_LEFT"
    UPPER_RIGHT = "UPPER_RIGHT"
    LOWER_LEFT = "LOWER_LEFT"
    LOWER_RIGHT = "LOWER_RIGHT"


class BuildAndDestroyType(str, Enum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Side(str, Enum):
    A = "A"
    B = "B"


class State(IntEnum):
    WAITING = 0
    CHOOSE_ACTION = 1
    CHOOSE_DIRECTION = 2
