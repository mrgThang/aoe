import copy
import json
import os
import tkinter as tk
from typing import Union

from dotenv import load_dotenv

from helpers import INIT_WIDTH, INIT_HEIGHT, Side, INFO_BOARD_WIDTH, State, ActionType, MoveType, \
    mapping_from_dist_to_action_type
from models import AbstractObject, Neutral, Position, Castle, CraftsMenA, CraftsMenB
from services import Service
from services_models import GameResp, GameActionsReq

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Map:
    _point: list[list[AbstractObject]]
    _width: int
    _height: int
    _is_on_click: bool
    _chosen_craftsman_pos: Position

    def __init__(self, canvas: tk.Canvas, data: GameResp, width: int, height: int,
                 window_width: int, window_height: int):
        self._width = width
        self._height = height
        self._is_on_click = False
        self._chosen_craftsman_pos = Position(x=-1, y=-1)
        self.create_map_neutral()
        self.create_map_component(data=data)
        self.display(canvas=canvas, window_width=window_width, window_height=window_height)

    def create_map_component(self, data: GameResp):
        if data is None or data.field is None:
            return
        for c in data.field.castles:
            self._point[c.x][c.y] = Castle(position=Position(x=c.x, y=c.y))
        for c in data.field.craftsmen:
            if c.side is Side.A:
                self._point[c.x][c.y] = CraftsMenA(position=Position(x=c.x, y=c.y), craftsmen_id=c.id)
            if c.side is Side.B:
                self._point[c.x][c.y] = CraftsMenB(position=Position(x=c.x, y=c.y), craftsmen_id=c.id)

    def create_map_neutral(self):
        self._point = [[
            Neutral(position=Position(x=x, y=y))
            for y in range(self._height)]
            for x in range(self._width)]

    def resize(self, canvas: tk.Canvas, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for row in self._point:
            for square in row:
                x1 = square.position.x * rect_width
                y1 = square.position.y * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height

                square.change_the_position(
                    x1=x1, y1=y1, x2=x2, y2=y2, canvas=canvas
                )

    def display(self, canvas: tk.Canvas, window_width: int, window_height: int):
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for row in self._point:
            for square in row:
                x1 = square.position.x * rect_width
                y1 = square.position.y * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height

                square.display(
                    x1=x1, y1=y1, x2=x2, y2=y2, canvas=canvas
                )

    def delete(self, canvas: tk.Canvas):
        for row in self._point:
            for square in row:
                square.delete(canvas=canvas)

    def on_click(self, event, canvas: tk.Canvas, window_width: int, window_height: int, cur_state: State) -> Position:
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for row in self._point:
            for square in row:
                x1 = square.position.x * rect_width
                y1 = square.position.y * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height
                is_on_click = square.on_click(event=event, x1=x1, y1=y1, x2=x2, y2=y2, canvas=canvas)

                if is_on_click is True and (type(square) is CraftsMenA or type(square) is CraftsMenB)\
                        and cur_state is State.WAITING:
                    self._chosen_craftsman_pos = square.position
                    square.choose(canvas=canvas, x1=x1, y1=y1, x2=x2, y2=y2)
                    self.remove_neighbor_wrapper(canvas=canvas, x=square.position.x, y=square.position.y)
                    return square.position

                if is_on_click is True and cur_state is State.CHOOSE_DIRECTION:
                    distance_x = abs(self._chosen_craftsman_pos.x - square.position.x)
                    distance_y = abs(self._chosen_craftsman_pos.y - square.position.y)
                    if max(distance_x, distance_y) == 1:
                        square.change_color(canvas=canvas)
                        self._chosen_craftsman_pos = Position(x=-1, y=-1)
                        square.choose(canvas=canvas, x1=x1, y1=y1, x2=x2, y2=y2)
                        return square.position

        return Position(x=-1, y=-1)

    def remove_neighbor_wrapper(self, canvas: tk.Canvas, x: int, y: int):
        board_size = len(self._point)
        border_list = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for (i,j) in border_list:
            if 0 <= x+i < board_size and 0 <= y+j < board_size:
                self._point[x+i][y+j].remove_wrapper(canvas)

    def check_hover(self, event, canvas: tk.Canvas, window_width: int, window_height: int):
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
                    square.on_hover(canvas=canvas, event=event, x1=x1, y1=y1, x2=x2, y2=y2)

    def find_craftsmen_id_with_position(self, position: Position):
        return self._point[position.x][position.y].craftsmen_id


class MapController:
    _window: tk.Tk
    _frame: tk.Frame
    _canvas: tk.Canvas
    _service: Service
    _move_button: tk.Button
    _build_button: tk.Button
    _destroy_button: tk.Button
    _button: tk.Button
    _my_map: Map
    _craftsmen_position: Position
    _state: State
    _last_state: State
    _turn: int
    _turn_text: tk.Label
    _time_remain: int
    _time_remain_text: tk.Label
    _request_data: tk.Text
    _current_data: GameActionsReq
    _next_data: GameActionsReq.ChildAction
    _send_button: tk.Button
    _response_text: tk.Label
    _team_id: int
    _side: Side
    _side_text: tk.Label

    def __init__(self, window: tk.Tk, frame: tk.Frame, canvas: tk.Canvas):
        self._window = window
        self._frame = frame
        self._canvas = canvas
        self._services = Service()
        self._team_id = os.getenv('TEAM_ID', 0)

        self._button = tk.Button(frame, text="Create Map", command=self.update_map)
        self._button.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=0)
        self._button.pack()

        self._side = Side.A
        self._side_text = tk.Label(self._frame, text="Side: A", font=("Arial", 12))
        self._side_text.place(x=INIT_WIDTH - INFO_BOARD_WIDTH, y=50)
        self._side_text.pack()

        self._turn = 1
        self._turn_text = tk.Label(self._frame, text="Turn: 1", font=("Arial", 12))
        self._turn_text.place(x=INIT_WIDTH - INFO_BOARD_WIDTH, y=100)
        self._turn_text.pack()

        self._time_remain = 30
        self._time_remain_text = tk.Label(self._frame, text="Time remaining: 30", font=("Arial", 12))
        self._time_remain_text.place(x=INIT_WIDTH - INFO_BOARD_WIDTH, y=150)
        self._time_remain_text.pack()

        self._request_data = tk.Text(self._frame, font=("Courier New", 10), width=100, height=15)
        self._request_data.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=200)
        self._request_data.pack()

        self._next_data = GameActionsReq.ChildAction(action=ActionType.MOVE, action_param=MoveType.LEFT, crafts_man_id="1")
        self._current_data = GameActionsReq(turn=1, actions=[])

        self._send_button = tk.Button(frame, text="Send data", command=self.send_data)
        self._send_button.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=550)
        self._send_button.pack()

        self._response_text = tk.Label(self._frame, text="Response", font=("Arial", 12))
        self._response_text.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=600)
        self._response_text.pack()

        self._my_map = self.init_map()
        self._state = State.WAITING
        self._last_state = None
        self._craftsmen_position = Position(x=-1, y=-1)

    def update_map(self):
        data = self._services.get_game_with_game_id()
        if self._my_map:
            self._my_map.delete(canvas=self._canvas)
        self._my_map = self.create_map_from_server(data=data)
        for side in data.sides:
            if side.team_id == self._team_id:
                self._side = side.side

        status_data = self._services.get_game_status_with_game_id()
        self._turn = status_data.cur_turn
        self._turn_text.config(text=f"Turn: {str(self._turn)}")
        self._time_remain = status_data.remaining
        self._state = State.WAITING

    def resize(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        if self._my_map:
            self._my_map.resize(canvas=self._canvas,
                                window_width=window_width-INFO_BOARD_WIDTH, window_height=window_height)
        self._button.place(x=window_width-INFO_BOARD_WIDTH, y=0)
        self._turn_text.place(x=window_width-INFO_BOARD_WIDTH, y=50)
        self._side_text.place(x=window_width-INFO_BOARD_WIDTH, y=100)
        self._time_remain_text.place(x=window_width-INFO_BOARD_WIDTH, y=150)
        self._request_data.place(x=window_width-INFO_BOARD_WIDTH, y=200)
        self._send_button.place(x=window_width-INFO_BOARD_WIDTH, y=550)
        self._response_text.place(x=window_width-INFO_BOARD_WIDTH, y=600)

    def create_map_from_server(self, data: GameResp):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        grid_width = data.field.width
        grid_height = data.field.height

        self._frame.config(width=window_width, height=window_height)
        self._canvas.config(width=window_width-INFO_BOARD_WIDTH, height=window_height)

        return Map(canvas=self._canvas, data=data, width=grid_width, height=grid_height,
                   window_width=window_width-INFO_BOARD_WIDTH, window_height=window_height)

    def init_map(self):
        window_width = INIT_WIDTH
        window_height = INIT_HEIGHT
        grid_width = 25
        grid_height = 25

        self._frame.config(width=window_width, height=window_height)
        self._canvas.config(width=window_width-INFO_BOARD_WIDTH, height=window_height)

        return Map(canvas=self._canvas, data=GameResp(), width=grid_width, height=grid_height,
                   window_width=window_width-INFO_BOARD_WIDTH, window_height=window_height)

    def on_click(self, event):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()

        click_position: Position = self._my_map.on_click(event=event, canvas=self._canvas,
                                                         window_width=window_width-INFO_BOARD_WIDTH,
                                                         window_height=window_height,
                                                         cur_state=self._state)

        if click_position.x != -1 and self._state == State.WAITING:
            self._craftsmen_position = click_position
            self._next_data.craftsman_id = self._my_map.find_craftsmen_id_with_position(click_position)
            self._last_state = self._state
            self._state = State.CHOOSE_ACTION
            self.display_button_choose_action(event)

        if click_position.x != -1 and self._state == State.CHOOSE_DIRECTION:
            self._next_data.action_param = mapping_from_dist_to_action_type(action=self._next_data.action,
                                                                            click_pos=click_position,
                                                                            craftsmen_pos=self._craftsmen_position)
            self.store_request()
            self._last_state = self._state
            self._state = State.WAITING

    def display_button_choose_action(self, event):
        self._move_button = tk.Button(self._window, text="Move", font=("Comic Sans", 15), fg="#00FF00", bg="black",
                                      command=lambda: self.display_choose_direction(action_type=ActionType.MOVE))
        self._move_button.place(x=event.x, y=event.y)

        self._build_button = tk.Button(self._window, text="Build", font=("Comic Sans", 15), fg="#00FF00", bg="black",
                                       command=lambda: self.display_choose_direction(action_type=ActionType.BUILD))
        self._build_button.place(x=event.x+100, y=event.y)

        self._destroy_button = tk.Button(self._window, text="Destroy", font=("Comic Sans", 15), fg="#00FF00", bg="black",
                                         command=lambda: self.display_choose_direction(action_type=ActionType.DESTROY))
        self._destroy_button.place(x=event.x+200, y=event.y)

    def store_request(self):
        for action in self._current_data.actions:
            if action.craftsman_id == self._next_data.craftsman_id:
                self._current_data.actions.remove(action)
        self._current_data.actions.append(copy.deepcopy(self._next_data))

        self._current_data.turn = self._turn + 1
        if self._side is Side.A and self._current_data.turn%2 == 1:
            self._current_data.turn += 1
        if self._side is Side.B and self._current_data.turn%2 == 0:
            self._current_data.turn += 1
        data = self._current_data.dict()
        pretty_json = json.dumps(data, indent=1)
        self._request_data.delete("1.0", tk.END)
        self._request_data.insert(tk.END, pretty_json)

    def display_choose_direction(self, action_type: ActionType):
        self._move_button.destroy()
        self._build_button.destroy()
        self._destroy_button.destroy()

        self._next_data.action = action_type
        self._last_state = self._state
        self._state = State.CHOOSE_DIRECTION

    def check_hover(self, event):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        if self._state == State.CHOOSE_DIRECTION:
            self._my_map.check_hover(event=event, canvas=self._canvas,
                                     window_width=window_width-INFO_BOARD_WIDTH, window_height=window_height)

    def update_timer(self):
        if self._time_remain is None:
            self._time_remain_text.config(text="Time remaining: None")
            return
        if self._time_remain >= 1:
            self._time_remain_text.config(text=f"Time remaining: {self._time_remain}")
            self._time_remain_text.after(1000, self.update_timer)
            self._time_remain -= 1
        elif self._time_remain < 1:
            self.update_map()
            self._time_remain_text.after(200, self.update_timer)

    def send_data(self):
        json_text = self._request_data.get("1.0", tk.END)
        data = json.loads(json_text)
        resp = self._services.post_game_actions(GameActionsReq(**data))
        self._response_text.config(text=str(resp))
