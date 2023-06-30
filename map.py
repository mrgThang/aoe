import tkinter as tk
from enum import Enum

from helpers import INIT_WIDTH, INIT_HEIGHT, Side
from models import AbstractObject, Neutral, Position, Castle, CraftsMenA, CraftsMenB
from services import Service
from services_models import GameResp


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
                self._point[c.x][c.y] = CraftsMenA(position=Position(x=c.x, y=c.y))
            if c.side is Side.B:
                self._point[c.x][c.y] = CraftsMenB(position=Position(x=c.x, y=c.y))

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

    def on_click(self, event, canvas: tk.Canvas, window_width: int, window_height: int) -> Position:
        rect_width = int(window_width / self._width)
        rect_height = int(window_height / self._height)

        for row in self._point:
            for square in row:
                x1 = square.position.x * rect_width
                y1 = square.position.y * rect_height
                x2 = x1 + rect_width
                y2 = y1 + rect_height
                is_on_click = square.on_click(event=event, x1=x1, y1=y1, x2=x2, y2=y2, canvas=canvas)
                if is_on_click is True and self._chosen_craftsman_pos.x == -1 and type(square) is CraftsMenA:
                    self._chosen_craftsman_pos = square.position
                    return square.position
                if is_on_click is True and self._chosen_craftsman_pos.x != -1:
                    distance_x = abs(self._chosen_craftsman_pos.x - square.position.x)
                    distance_y = abs(self._chosen_craftsman_pos.y - square.position.y)
                    if max(distance_x, distance_y) == 1:
                        square.change_color(canvas=canvas)
                        self._chosen_craftsman_pos = Position(x=-1, y=-1)
                        return square.position

        return Position(x=-1, y=-1)

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


class State(Enum):
    WAITING = 0
    CHOOSE_ACTION = 1
    CHOOSE_DIRECTION = 2


class MapController:
    _window: tk.Tk
    _frame: tk.Frame
    _canvas: tk.Canvas
    _move_button: tk.Button
    _build_button: tk.Button
    _destroy_button: tk.Button
    _button: tk.Button
    _my_map: Map
    _craftsmen_position: Position
    _state: State
    _last_state: State
    _turn: tk.Label

    def __init__(self, window: tk.Tk, frame: tk.Frame, canvas: tk.Canvas):
        self._window = window
        self._frame = frame
        self._canvas = canvas

        self._button = tk.Button(frame, text="Click me", command=self.button_click)
        self._button.place(x=INIT_WIDTH - 100, y=0)
        self._button.pack()

        self._turn = tk.Label(self._frame, text="Turn", font=("Arial", 12))
        self._turn.place(x=INIT_WIDTH - 100, y=100)
        self._turn.pack()

        self._my_map = self.init_map()
        self._state = State.WAITING
        self._last_state = None
        self._craftsmen_position = Position(x=-1, y=-1)

    def button_click(self):
        services: Service = Service()
        data = services.get_game_with_game_id()
        if self._my_map:
            self._my_map.delete(canvas=self._canvas)
        self._my_map = self.create_map_from_server(data=data)
        status_data = services.get_game_status_with_game_id()
        self._turn.config(text=str(status_data.cur_turn))

    def resize(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        if self._my_map:
            self._my_map.resize(canvas=self._canvas, window_width=window_width - 100, window_height=window_height)
        self._button.place(x=window_width - 100, y=0)
        self._turn.place(x=window_width - 100, y=100)

    def create_map_from_server(self, data: GameResp):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        grid_width = data.field.width
        grid_height = data.field.height

        self._frame.config(width=window_width, height=window_height)
        self._canvas.config(width=window_width - 100, height=window_height)

        return Map(canvas=self._canvas, data=data, width=grid_width, height=grid_height,
                   window_width=window_width-100, window_height=window_height)

    def init_map(self):
        window_width = INIT_WIDTH
        window_height = INIT_HEIGHT
        grid_width = 25
        grid_height = 25

        self._frame.config(width=window_width, height=window_height)
        self._canvas.config(width=window_width - 100, height=window_height)

        return Map(canvas=self._canvas, data=GameResp(), width=grid_width, height=grid_height,
                   window_width=window_width-100, window_height=window_height)

    def on_click(self, event):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()

        click_position = self._my_map.on_click(event=event, canvas=self._canvas,
                                               window_width=window_width-100, window_height=window_height)
        if click_position.x != -1 and self._state == State.WAITING:
            self._craftsmen_position = click_position
            self._last_state = self._state
            self._state = State.CHOOSE_ACTION
            self.display_button_choose_action()

        if click_position.x != -1 and self._state == State.CHOOSE_DIRECTION:
            self._last_state = self._state
            self._state = State.WAITING

    def display_button_choose_action(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()

        self._move_button = tk.Button(self._window, text="Move", font=("Comic Sans", 15), fg="#00FF00", bg="black",
                                      command=lambda: self.display_choose_direction(command="Move"))
        self._move_button.place(x=(window_width - 100) / 2 - 100, y=window_height / 2)

        self._build_button = tk.Button(self._window, text="Build", font=("Comic Sans", 15), fg="#00FF00", bg="black",
                                       command=lambda: self.display_choose_direction(command="Build"))
        self._build_button.place(x=(window_width - 100) / 2, y=window_height / 2)

        self._destroy_button = tk.Button(self._window, text="Destroy", font=("Comic Sans", 15), fg="#00FF00", bg="black",
                                         command=lambda: self.display_choose_direction(command="Build"))
        self._destroy_button.place(x=(window_width - 100) / 2 + 100, y=window_height / 2)

    def display_choose_direction(self, command: str):
        self._move_button.destroy()
        self._build_button.destroy()
        self._destroy_button.destroy()

        self._last_state = self._state
        self._state = State.CHOOSE_DIRECTION

    def check_hover(self, event):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        if self._state == State.CHOOSE_DIRECTION:
            self._my_map.check_hover(event=event, canvas=self._canvas,
                                     window_width=window_width-100, window_height=window_height)
