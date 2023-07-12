import copy
import os
import queue
import tkinter as tk

from dotenv import load_dotenv

from helpers import Side, ActionType, MoveType, BuildAndDestroyType
from map_components import AbstractObject, Neutral, Position, Castle, CraftsManA, CraftsManB, Pond, \
    AbstractObjectWithImage, WallA, WallB
from models import GameResp, GameActionsResp

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
load_dotenv(os.path.join(BASE_DIR, '../.env'))


class Map:
    def __init__(self, width: int, height: int, canvas: tk.Canvas, start_queue: bool = True):
        self._width: int = width
        self._height: int = height
        self._canvas = canvas
        self._is_on_click: bool = False
        self._chosen_craftsman_pos: Position = Position(x=-1, y=-1)
        self._point: list[list[AbstractObject]] = []
        self._craftsmen: list[AbstractObjectWithImage] = []
        if start_queue:
            self._queue = queue.Queue()
        else:
            self._queue = None
        self._castle_point = 0
        self._territory_point = 0
        self._wall_point = 0
        self._is_checked: list[list[bool]] = []

    def init_map(self, data: GameResp, window_width: int, window_height: int):
        self.create_map_neutral()
        self.create_map_component(data=data)
        self.display(window_width=window_width, window_height=window_height)

    def create_map_neutral(self):
        self._point = [[
            Neutral(position=Position(x=x, y=y))
            for y in range(self._height)]
            for x in range(self._width)]

    def create_map_component(self, data: GameResp):
        if data is None or data.field is None:
            return
        self._castle_point = data.field.castle_coeff
        self._territory_point = data.field.territory_coeff
        self._wall_point = data.field.wall_coeff
        for castle in data.field.castles:
            self._point[castle.x][castle.y] = Castle(position=Position(x=castle.x, y=castle.y))
        for pond in data.field.ponds:
            self._point[pond.x][pond.y] = Pond(position=Position(x=pond.x, y=pond.y))
        for craftsman in data.field.craftsmen:
            if craftsman.side == Side.A:
                self._craftsmen.append(CraftsManA(position=Position(x=craftsman.x, y=craftsman.y),
                                                  craftsmen_id=craftsman.id))
            if craftsman.side == Side.B:
                self._craftsmen.append(CraftsManB(position=Position(x=craftsman.x, y=craftsman.y),
                                                  craftsmen_id=craftsman.id))

    def change_map_component_from_actions_response(self, child_action: GameActionsResp.ChildAction):
        for craftsman in self._craftsmen:
            if craftsman.craftsmen_id == child_action.craftsman_id:
                if child_action.action == ActionType.MOVE:
                    self.handle_move_action(craftsman=craftsman, child_action=child_action)
                if child_action.action == ActionType.BUILD:
                    self.handle_build_action(craftsman=craftsman, child_action=child_action)
                if child_action.action == ActionType.DESTROY:
                    self.handle_destroy_action(craftsman=craftsman, child_action=child_action)

    def handle_move_action(self, craftsman: AbstractObjectWithImage, child_action: GameActionsResp.ChildAction):
        move_type_mapping = {
            MoveType.UPPER_LEFT: (-1, -1),
            MoveType.LEFT: (-1, 0),
            MoveType.LOWER_LEFT: (-1, 1),
            MoveType.UP: (0, -1),
            MoveType.DOWN: (0, 1),
            MoveType.UPPER_RIGHT: (1, -1),
            MoveType.RIGHT: (1, 0),
            MoveType.LOWER_RIGHT: (1, 1)
        }
        (x, y) = move_type_mapping.get(child_action.action_param)
        target_pos = Position(x=craftsman.position.x + x, y=craftsman.position.y + y)
        if 0 <= target_pos.x < self._width and 0 <= target_pos.y < self._height:
            type_of_target = type(self._point[target_pos.x][target_pos.y])
            is_target_have_craftsman = self.check_if_position_has_craftsman(
                position=self._point[target_pos.x][target_pos.y].position)
            if not is_target_have_craftsman:
                if type_of_target is Neutral or type_of_target is Castle:
                    craftsman.position = target_pos
                    craftsman.raise_rectangle(canvas=self._canvas)
                if type_of_target is WallA and type(craftsman) is CraftsManA:
                    craftsman.position = target_pos
                    craftsman.raise_rectangle(canvas=self._canvas)
                if type_of_target is WallB and type(craftsman) is CraftsManB:
                    craftsman.position = target_pos
                    craftsman.raise_rectangle(canvas=self._canvas)

    def handle_build_action(self, craftsman: AbstractObjectWithImage, child_action: GameActionsResp.ChildAction):
        build_type_mapping = {
            BuildAndDestroyType.LEFT: (-1, 0),
            BuildAndDestroyType.RIGHT: (1, 0),
            BuildAndDestroyType.ABOVE: (0, -1),
            BuildAndDestroyType.BELOW: (0, 1)
        }
        (x, y) = build_type_mapping.get(child_action.action_param)
        target_pos = Position(x=craftsman.position.x + x, y=craftsman.position.y + y)
        if 0 <= target_pos.x < self._width and 0 <= target_pos.y < self._height:
            type_of_target = type(self._point[target_pos.x][target_pos.y])
            is_target_have_craftsman = self.check_if_position_has_craftsman(
                position=self._point[target_pos.x][target_pos.y].position)
            if not is_target_have_craftsman and type_of_target is Neutral:
                if type(craftsman) is CraftsManA:
                    self._point[target_pos.x][target_pos.y] = WallA(position=target_pos)
                else:
                    self._point[target_pos.x][target_pos.y] = WallB(position=target_pos)

    def handle_destroy_action(self, craftsman: AbstractObjectWithImage, child_action: GameActionsResp.ChildAction):
        destroy_type_mapping = {
            BuildAndDestroyType.LEFT: (-1, 0),
            BuildAndDestroyType.RIGHT: (1, 0),
            BuildAndDestroyType.ABOVE: (0, -1),
            BuildAndDestroyType.BELOW: (0, 1)
        }
        (x, y) = destroy_type_mapping.get(child_action.action_param)
        target_pos = Position(x=craftsman.position.x + x, y=craftsman.position.y + y)
        if 0 <= target_pos.x < self._width and 0 <= target_pos.y < self._height:
            type_of_target = type(self._point[target_pos.x][target_pos.y])
            if type_of_target is WallA or type_of_target is WallB:
                self._point[target_pos.x][target_pos.y] = Neutral(position=target_pos)

    def check_if_position_has_craftsman(self, position: Position) \
            -> bool:
        for craftsman in self._craftsmen:
            if craftsman.position.x == position.x and craftsman.position.y == position.y:
                return True
        return False

    def resize(self, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for row in self._point:
            for square in row:
                x1 = square.position.x * rect_width
                y1 = square.position.y * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height
                square.change_the_position(
                    x1=x1, y1=y1, x2=x2, y2=y2, canvas=self._canvas
                )

        for craftsman in self._craftsmen:
            x1 = craftsman.position.x * rect_width
            y1 = craftsman.position.y * rect_height
            x2 = x1 + rect_width
            y2 = y1 + rect_height
            craftsman.change_the_position(
                x1=x1, y1=y1, x2=x2, y2=y2, canvas=self._canvas
            )
            craftsman.raise_rectangle(canvas=self._canvas)

    def display(self, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for row in self._point:
            for square in row:
                x1 = square.position.x * rect_width
                y1 = square.position.y * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height
                square.display(
                    x1=x1, y1=y1, x2=x2, y2=y2, canvas=self._canvas
                )

        for craftsman in self._craftsmen:
            x1 = craftsman.position.x * rect_width
            y1 = craftsman.position.y * rect_height
            x2 = x1 + rect_width
            y2 = y1 + rect_height
            craftsman.display(
                x1=x1, y1=y1, x2=x2, y2=y2, canvas=self._canvas
            )

    def delete(self):
        self.reset()
        for row in self._point:
            for square in row:
                square.delete(canvas=self._canvas)
        for craftsman in self._craftsmen:
            craftsman.delete(canvas=self._canvas)

    def reset(self):
        for row in self._point:
            for square in row:
                square.delete_wrapper(canvas=self._canvas)
                square.revert_color(canvas=self._canvas)
        for craftsman in self._craftsmen:
            craftsman.delete_border(canvas=self._canvas)
            craftsman.delete_wrapper(canvas=self._canvas)
            craftsman.is_played = False

    def choose_craftsman(self, side: Side, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for craftsman in self._craftsmen:
            if side == Side.A and type(craftsman) is CraftsManA or side == Side.B and type(craftsman) is CraftsManB:
                if not craftsman.is_played:
                    x1 = craftsman.position.x * rect_width
                    y1 = craftsman.position.y * rect_height
                    x2 = x1 + rect_width
                    y2 = y1 + rect_height
                    craftsman.choose(canvas=self._canvas, x1=x1, y1=y1, x2=x2, y2=y2)
                    craftsman.is_played = True
                    self._chosen_craftsman_pos = craftsman.position
                    return craftsman
        for craftsman in self._craftsmen:
            if side == Side.A and type(craftsman) is CraftsManA or side == Side.B and type(craftsman) is CraftsManB:
                craftsman.is_played = False
        for craftsman in self._craftsmen:
            if side == Side.A and type(craftsman) is CraftsManA or side == Side.B and type(craftsman) is CraftsManB:
                if not craftsman.is_played:
                    x1 = craftsman.position.x * rect_width
                    y1 = craftsman.position.y * rect_height
                    x2 = x1 + rect_width
                    y2 = y1 + rect_height
                    craftsman.choose(canvas=self._canvas, x1=x1, y1=y1, x2=x2, y2=y2)
                    craftsman.is_played = True
                    self._chosen_craftsman_pos = craftsman.position
                    return craftsman
        return None

    def choose_craftsman_without_loop(self, side: Side, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for craftsman in self._craftsmen:
            if side == Side.A and type(craftsman) is CraftsManA or side == Side.B and type(craftsman) is CraftsManB:
                if not craftsman.is_played:
                    x1 = craftsman.position.x * rect_width
                    y1 = craftsman.position.y * rect_height
                    x2 = x1 + rect_width
                    y2 = y1 + rect_height
                    craftsman.choose(canvas=self._canvas, x1=x1, y1=y1, x2=x2, y2=y2)
                    craftsman.is_played = True
                    self._chosen_craftsman_pos = craftsman.position
                    return craftsman
        return None

    def remove_is_played(self):
        for craftsman in self._craftsmen:
            craftsman.is_played = False

    def choose_direction(self, window_width: int, window_height: int, key_list: list):
        square_x = self._chosen_craftsman_pos.x
        square_y = self._chosen_craftsman_pos.y

        if "Left" in key_list:
            square_x -= 1
        if "Right" in key_list:
            square_x += 1
        if "Up" in key_list:
            square_y -= 1
        if "Down" in key_list:
            square_y += 1

        if 0 <= square_x < window_width - 1 and 0 <= square_y < window_height - 1:
            self._point[square_x][square_y].change_color(canvas=self._canvas)
            self._point[square_x][square_y].raise_rectangle(canvas=self._canvas)
            self.update_queue(position=self._point[square_x][square_y].position)
            self.revert_neighbor_color(x=self._chosen_craftsman_pos.x, y=self._chosen_craftsman_pos.y)

    def update_queue(self, position: Position):
        self._queue.put(position)
        if self._queue.qsize() > len(self._craftsmen) / 2:
            self._queue.get()

    def remove_border_of_craftsman(self):
        for craftsman in self._craftsmen:
            craftsman.delete_border(canvas=self._canvas)

    def revert_neighbor_color(self, x: int, y: int):
        border_list = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for (i, j) in border_list:
            if 0 <= x + i < self._width and 0 <= y + j < self._height:
                is_change_color = True
                queue_current_size = self._queue.qsize()
                for index in range(0, queue_current_size):
                    item = self._queue.get()
                    if item.x == self._point[x + i][y + j].position.x and \
                            item.y == self._point[x + i][y + j].position.y:
                        is_change_color = False
                    self._queue.put(item)
                if is_change_color:
                    self._point[x + i][y + j].revert_color(self._canvas)

    def get_actual_position(self, position: Position, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)
        return position.x * rect_width, position.y * rect_height

    def update_choose_action_on_craftsman(self, craftsman: AbstractObject, action_type: ActionType,
                                          window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)
        x1 = craftsman.position.x * rect_width
        y1 = craftsman.position.y * rect_height
        x2 = x1 + rect_width
        y2 = y1 + rect_height
        craftsman.choose_action(canvas=self._canvas, action_type=action_type,
                                x1=x1, x2=x2, y1=y1, y2=y2)

    def calculate_point(self) -> (int, int):
        point_a = 0
        point_b = 0

        for row in self._point:
            for square in row:
                if type(square) is WallA:
                    point_a += self._wall_point
                if type(square) is WallB:
                    point_b += self._wall_point
                if square.is_close_territory_a or square.is_open_territory_a:
                    if type(square) is Castle:
                        point_a += self._castle_point
                    else:
                        point_a += self._territory_point
                if square.is_close_territory_b or square.is_open_territory_b:
                    if type(square) is Castle:
                        point_b += self._castle_point
                    else:
                        point_b += self._territory_point

        return point_a, point_b

    def update_territory_status(self):
        for row in self._point:
            for square in row:
                is_close_territory_a = self.check_if_square_is_close_territory(square, side=Side.A)
                is_close_territory_b = self.check_if_square_is_close_territory(square, side=Side.B)
                if is_close_territory_a and is_close_territory_b:
                    square.is_close_territory_a = True
                    square.is_close_territory_b = True
                    square.is_open_territory_a = False
                    square.is_open_territory_b = False
                elif is_close_territory_a:
                    square.is_close_territory_a = True
                    square.is_close_territory_b = False
                    square.is_open_territory_a = False
                    square.is_open_territory_b = False
                elif is_close_territory_b:
                    square.is_close_territory_a = False
                    square.is_close_territory_b = True
                    square.is_open_territory_a = False
                    square.is_open_territory_b = False
                else:
                    if square.is_close_territory_a:
                        square.is_close_territory_a = False
                        square.is_close_territory_b = False
                        square.is_open_territory_a = True
                        square.is_open_territory_b = False
                    if square.is_close_territory_b:
                        square.is_close_territory_a = False
                        square.is_close_territory_b = False
                        square.is_open_territory_a = False
                        square.is_open_territory_b = True

    def check_if_square_is_close_territory(self, square, side: Side):
        if type(square) is WallA and side == Side.A:
            return False
        if type(square) is WallB and side == Side.B:
            return False
        self._is_checked = [[
            False
            for y in range(self._height)]
            for x in range(self._width)]
        return self.bfs(square=square, side=side)

    def bfs(self, square, side: Side):
        x = square.position.x
        y = square.position.y
        if self._is_checked[x][y]:
            return True
        self._is_checked[x][y] = True
        if type(self._point[x][y]) is WallA and side == Side.A:
            return True
        if type(self._point[x][y]) is WallB and side == Side.B:
            return True
        if x == 0 or y == 0 \
                or x == self._width-1 or y == self._height-1:
            return False
        if not self.bfs(square=self._point[x-1][y], side=side):
            return False
        if not self.bfs(square=self._point[x][y-1], side=side):
            return False
        if not self.bfs(square=self._point[x+1][y], side=side):
            return False
        if not self.bfs(square=self._point[x][y+1], side=side):
            return False
        return True

    def init_map_but_not_render(self, data: GameResp):
        self.create_map_neutral()
        self.create_map_component(data=data)

    def handle_actions_but_not_render(self, child_action: GameActionsResp.ChildAction):
        for craftsman in self._craftsmen:
            if craftsman.craftsmen_id == child_action.craftsman_id:
                if child_action.action == ActionType.MOVE:
                    self.handle_move_action_but_not_render(craftsman=craftsman, child_action=child_action)
                if child_action.action == ActionType.BUILD:
                    self.handle_build_action_but_not_render(craftsman=craftsman, child_action=child_action)
                if child_action.action == ActionType.DESTROY:
                    self.handle_destroy_action_but_not_render(craftsman=craftsman, child_action=child_action)

    def handle_move_action_but_not_render(self, craftsman: AbstractObject, child_action: GameActionsResp.ChildAction):
        move_type_mapping = {
            MoveType.UPPER_LEFT: (-1, -1),
            MoveType.LEFT: (-1, 0),
            MoveType.LOWER_LEFT: (-1, 1),
            MoveType.UP: (0, -1),
            MoveType.DOWN: (0, 1),
            MoveType.UPPER_RIGHT: (1, -1),
            MoveType.RIGHT: (1, 0),
            MoveType.LOWER_RIGHT: (1, 1)
        }
        (x, y) = move_type_mapping.get(child_action.action_param)
        target_pos = Position(x=craftsman.position.x + x, y=craftsman.position.y + y)
        if 0 <= target_pos.x < self._width and 0 <= target_pos.y < self._height:
            type_of_target = type(self._point[target_pos.x][target_pos.y])
            is_target_have_craftsman = self.check_if_position_has_craftsman(
                position=self._point[target_pos.x][target_pos.y].position)
            if not is_target_have_craftsman:
                if type_of_target is Neutral or type_of_target is Castle:
                    craftsman.position = target_pos
                if type_of_target is WallA and type(craftsman) is CraftsManA:
                    craftsman.position = target_pos
                if type_of_target is WallB and type(craftsman) is CraftsManB:
                    craftsman.position = target_pos

    def handle_build_action_but_not_render(self, craftsman: AbstractObject, child_action: GameActionsResp.ChildAction):
        build_type_mapping = {
            BuildAndDestroyType.LEFT: (-1, 0),
            BuildAndDestroyType.RIGHT: (1, 0),
            BuildAndDestroyType.ABOVE: (0, -1),
            BuildAndDestroyType.BELOW: (0, 1)
        }
        (x, y) = build_type_mapping.get(child_action.action_param)
        target_pos = Position(x=craftsman.position.x + x, y=craftsman.position.y + y)
        if 0 <= target_pos.x < self._width and 0 <= target_pos.y < self._height:
            type_of_target = type(self._point[target_pos.x][target_pos.y])
            is_target_have_craftsman = self.check_if_position_has_craftsman(
                position=self._point[target_pos.x][target_pos.y].position)
            if not is_target_have_craftsman and type_of_target is Neutral:
                if type(craftsman) is CraftsManA:
                    self._point[target_pos.x][target_pos.y] = WallA(position=target_pos)
                else:
                    self._point[target_pos.x][target_pos.y] = WallB(position=target_pos)

    def handle_destroy_action_but_not_render(self, craftsman: AbstractObject, child_action: GameActionsResp.ChildAction):
        destroy_type_mapping = {
            BuildAndDestroyType.LEFT: (-1, 0),
            BuildAndDestroyType.RIGHT: (1, 0),
            BuildAndDestroyType.ABOVE: (0, -1),
            BuildAndDestroyType.BELOW: (0, 1)
        }
        (x, y) = destroy_type_mapping.get(child_action.action_param)
        target_pos = Position(x=craftsman.position.x + x, y=craftsman.position.y + y)
        if 0 <= target_pos.x < self._width and 0 <= target_pos.y < self._height:
            type_of_target = type(self._point[target_pos.x][target_pos.y])
            if type_of_target is WallA or type_of_target is WallB:
                self._point[target_pos.x][target_pos.y] = Neutral(position=target_pos)


def create_new_map_from_old_map_and_actions(old_map: Map, list_actions: GameActionsResp):
    new_map: Map = copy.deepcopy(old_map)
    destroy_actions = [action for action in list_actions.actions if action.action == ActionType.DESTROY]
    build_actions = [action for action in list_actions.actions if action.action == ActionType.BUILD]
    move_actions = [action for action in list_actions.actions if action.action == ActionType.MOVE]

    for child_action in destroy_actions:
        new_map.handle_actions_but_not_render(child_action=child_action)
    for child_action in build_actions:
        new_map.handle_actions_but_not_render(child_action=child_action)
    for child_action in move_actions:
        new_map.handle_actions_but_not_render(child_action=child_action)

    new_map.update_territory_status()

    return new_map
