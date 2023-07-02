from app.helpers import ActionType, MoveType, BuildAndDestroyType
from map_components import Position


def mapping_from_dist_to_action_type(action: ActionType, craftsmen_pos: Position, click_pos: Position):
    dist_x = click_pos.x - craftsmen_pos.x
    dist_y = click_pos.y - craftsmen_pos.y
    dist = (dist_x, dist_y)
    move_type_mapping = {
        (-1, -1): MoveType.UPPER_LEFT,
        (-1, 0): MoveType.LEFT,
        (-1, 1): MoveType.LOWER_LEFT,
        (0, -1): MoveType.UP,
        (0, 1): MoveType.DOWN,
        (1, -1): MoveType.UPPER_RIGHT,
        (1, 0): MoveType.RIGHT,
        (1, 1): MoveType.LOWER_RIGHT
    }
    build_and_destroy_type_mapping = {
        (-1, 0): BuildAndDestroyType.LEFT,
        (1, 0): BuildAndDestroyType.RIGHT,
        (0, -1): BuildAndDestroyType.ABOVE,
        (0, 1): BuildAndDestroyType.BELOW
    }
    if action is ActionType.MOVE:
        return move_type_mapping.get(dist)
    else:
        return build_and_destroy_type_mapping.get(dist)
