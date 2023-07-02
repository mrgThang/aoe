import os
import tkinter as tk

from dotenv import load_dotenv

from helpers import Side, State, ActionType, MoveType, BuildAndDestroyType
from map_components import AbstractObject, Neutral, Position, Castle, CraftsManA, CraftsManB, Pond, \
    AbstractObjectWithImage, WallA, WallB
from models import GameResp, GameActionsResp

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
load_dotenv(os.path.join(BASE_DIR, '../.env'))


class Map:
    def __init__(self, width: int, height: int, canvas: tk.Canvas):
        self._width: int = width
        self._height: int = height
        self._canvas = canvas
        self._is_on_click: bool = False
        self._chosen_craftsman_pos: Position = Position(x=-1, y=-1)
        self._point: list[list[AbstractObject]] = []
        self._craftsmen: list[AbstractObjectWithImage] = []

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
        target_pos = Position(x=craftsman.position.x+x, y=craftsman.position.y+y)
        if 0 <= target_pos.x < self._width and 0 <= target_pos.y < self._height:
            type_of_target = type(self._point[target_pos.x][target_pos.y])
            is_target_have_craftsman = self.check_if_position_has_craftsman(
                position=self._point[target_pos.x][target_pos.y].position)
            if not is_target_have_craftsman and (type_of_target is Neutral or type_of_target is Castle):
                craftsman.position = target_pos

    def handle_build_action(self, craftsman: AbstractObjectWithImage, child_action: GameActionsResp.ChildAction):
        build_type_mapping = {
            BuildAndDestroyType.LEFT: (-1, 0),
            BuildAndDestroyType.RIGHT: (1, 0),
            BuildAndDestroyType.ABOVE: (0, -1),
            BuildAndDestroyType.BELOW: (0, 1)
        }
        (x, y) = build_type_mapping.get(child_action.action_param)
        target_pos = Position(x=craftsman.position.x+x, y=craftsman.position.y+y)
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
        target_pos = Position(x=craftsman.position.x+x, y=craftsman.position.y+y)
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
        self.remove_wrapper_and_border()
        for row in self._point:
            for square in row:
                square.delete(canvas=self._canvas)
        for craftsman in self._craftsmen:
            craftsman.delete(canvas=self._canvas)

    def remove_wrapper_and_border(self):
        for row in self._point:
            for square in row:
                square.delete_wrapper(canvas=self._canvas)
        for craftsman in self._craftsmen:
            craftsman.delete_border(canvas=self._canvas)

    def on_click(self, event, window_width: int, window_height: int, cur_state: State) -> Position:
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)
        clicked_craftsman = self.get_clicked_craftsman(event=event,
                                                       window_width=window_width, window_height=window_height)
        if clicked_craftsman is not None and cur_state == State.WAITING:
            self._chosen_craftsman_pos = clicked_craftsman.position
            x1 = clicked_craftsman.position.x * rect_width
            y1 = clicked_craftsman.position.y * rect_height
            x2 = x1 + rect_width
            y2 = y1 + rect_height
            clicked_craftsman.choose(canvas=self._canvas, x1=x1, y1=y1, x2=x2, y2=y2)
            self.remove_neighbor_wrapper(x=clicked_craftsman.position.x, y=clicked_craftsman.position.y)
            return clicked_craftsman.position

        for row in self._point:
            for square in row:
                x1 = square.position.x * rect_width
                y1 = square.position.y * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height
                is_on_click = square.on_click(event=event, x1=x1, y1=y1, x2=x2, y2=y2, canvas=self._canvas)

                if is_on_click is True and cur_state == State.CHOOSE_DIRECTION:
                    distance_x = abs(self._chosen_craftsman_pos.x - square.position.x)
                    distance_y = abs(self._chosen_craftsman_pos.y - square.position.y)
                    if max(distance_x, distance_y) == 1:
                        square.change_color(canvas=self._canvas)
                        self._chosen_craftsman_pos = Position(x=-1, y=-1)
                        square.choose(canvas=self._canvas, x1=x1, y1=y1, x2=x2, y2=y2)
                        return square.position

        return Position(x=-1, y=-1)

    def get_clicked_craftsman(self, event, window_width: int, window_height: int) \
            -> AbstractObjectWithImage:
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for craftsman in self._craftsmen:
            x1 = craftsman.position.x * rect_width
            y1 = craftsman.position.y * rect_height
            x2 = x1 + rect_width
            y2 = y1 + rect_height
            is_on_click = craftsman.on_click(event=event, x1=x1, y1=y1, x2=x2, y2=y2, canvas=self._canvas)
            if is_on_click:
                return craftsman

        return None

    def remove_neighbor_wrapper(self, x: int, y: int):
        board_size = len(self._point)
        border_list = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for (i, j) in border_list:
            if 0 <= x+i < board_size and 0 <= y+j < board_size:
                self._point[x+i][y+j].remove_wrapper(self._canvas)

    def check_hover(self, event, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for row in self._point:
            for square in row:
                if max(abs(self._chosen_craftsman_pos.x-square.position.x),
                       abs(self._chosen_craftsman_pos.y-square.position.y)) == 1:
                    x1 = square.position.x * rect_width
                    y1 = square.position.y * rect_height
                    x2 = x1 + rect_width
                    y2 = y1 + rect_height
                    square.on_hover(canvas=self._canvas, event=event, x1=x1, y1=y1, x2=x2, y2=y2)

    def find_craftsmen_id_with_position(self, position: Position) -> str:
        for craftsman in self._craftsmen:
            if craftsman.position == position:
                return craftsman.craftsmen_id
        return "1"
