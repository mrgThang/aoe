from app.helpers import ActionType, MoveType, BuildAndDestroyType


def mapping_from_key_list_to_action_type(action: ActionType, key_list: list):
    if action is ActionType.MOVE:
        if "Left" in key_list:
            if "Up" in key_list:
                return MoveType.UPPER_LEFT
            if "Down" in key_list:
                return MoveType.LOWER_LEFT
            return MoveType.LEFT
        if "Right" in key_list:
            if "Up" in key_list:
                return MoveType.UPPER_RIGHT
            if "Down" in key_list:
                return MoveType.LOWER_RIGHT
            return MoveType.RIGHT
        if "Up" in key_list:
            return MoveType.UP
        if "Down" in key_list:
            return MoveType.DOWN
    elif action is ActionType.BUILD or action is ActionType.DESTROY:
        if "Left" in key_list:
            return BuildAndDestroyType.LEFT
        if "Right" in key_list:
            return BuildAndDestroyType.RIGHT
        if "Up" in key_list:
            return BuildAndDestroyType.ABOVE
        if "Down" in key_list:
            return BuildAndDestroyType.BELOW
    else:
        return None
