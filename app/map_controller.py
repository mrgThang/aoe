import copy
import json
import os
import tkinter as tk
from typing import List

from app.helpers import State, Side, INIT_WIDTH, INFO_BOARD_WIDTH, ActionType, MoveType, INIT_HEIGHT
from app.map import Map
from app.utils import mapping_from_key_list_to_action_type
from map_components import CraftsManA
from models import GameActionsReq, GameResp, GameActionsResp
from services import Service


class MapController:

    def __init__(self, window: tk.Tk, frame: tk.Frame, canvas: tk.Canvas):
        self._window: tk.Tk = window
        self._frame: tk.Frame = frame
        self._canvas: tk.Canvas = canvas
        self._services: Service = Service()
        self._team_id: int = int(os.getenv('TEAM_ID', 0))
        self._state: State = State.WAITING
        self._craftsman: CraftsManA = None
        self._new_action: GameActionsReq.ChildAction = GameActionsReq.ChildAction(action=ActionType.MOVE,
                                                                                  action_param=MoveType.LEFT,
                                                                                  crafts_man_id="1")
        self._key_press_list = []
        self._stay_button: tk.Button = None
        self._move_button: tk.Button = None
        self._build_button: tk.Button = None
        self._destroy_button: tk.Button = None

        self._pull_map_button: tk.Button = tk.Button(frame, text="Create Map", command=self.create_map)
        self._pull_map_button.place(x=INIT_WIDTH - INFO_BOARD_WIDTH, y=0)
        self._pull_map_button.pack()

        self._side: Side = Side.A
        self._side_text: tk.Label = tk.Label(self._frame, text="Side: A", font=("Arial", 12))
        self._side_text.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=50)
        self._side_text.pack()

        self._turn: int = 1
        self._turn_text: tk.Label = tk.Label(self._frame, text=f"Turn: {self._turn}", font=("Arial", 12))
        self._turn_text.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=100)
        self._turn_text.pack()

        self._time_remain: int = 30
        self._time_remain_text: tk.Label = tk.Label(self._frame, text=f"Time remaining: {self._time_remain}",
                                                    font=("Arial", 12))
        self._time_remain_text.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=150)
        self._time_remain_text.pack()

        self._request_data: GameActionsReq = GameActionsReq(turn=1, actions=[])
        self._request_data_text: tk.Text = tk.Text(self._frame, font=("Courier New", 10), width=100, height=15)
        self._request_data_text.place(x=INIT_WIDTH - INFO_BOARD_WIDTH, y=200)
        self._request_data_text.pack()

        self._send_request_button: tk.Button = tk.Button(frame, text="Send data", command=self.send_data)
        self._send_request_button.place(x=INIT_WIDTH - INFO_BOARD_WIDTH, y=550)
        self._send_request_button.pack()

        self._response_text: tk.Label = tk.Label(self._frame, text="Response", font=("Arial", 12))
        self._response_text.place(x=INIT_WIDTH-INFO_BOARD_WIDTH, y=600)
        self._response_text.pack()

        self._my_map: Map = None
        self.init_map()

    def init_map(self):
        window_width = INIT_WIDTH
        window_height = INIT_HEIGHT
        grid_width = 25
        grid_height = 25

        self._frame.config(width=window_width, height=window_height)
        self._canvas.config(width=window_width-INFO_BOARD_WIDTH, height=window_height)

        self._my_map = Map(canvas=self._canvas, width=grid_width, height=grid_height)
        self._my_map.init_map(data=GameResp(), window_width=window_width-INFO_BOARD_WIDTH, window_height=window_height)

    def resize(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        if self._my_map:
            self._my_map.resize(window_width=window_width-INFO_BOARD_WIDTH, window_height=window_height)
        self._pull_map_button.place(x=window_width - INFO_BOARD_WIDTH, y=0)
        self._turn_text.place(x=window_width-INFO_BOARD_WIDTH, y=50)
        self._side_text.place(x=window_width-INFO_BOARD_WIDTH, y=100)
        self._time_remain_text.place(x=window_width-INFO_BOARD_WIDTH, y=150)
        self._request_data_text.place(x=window_width-INFO_BOARD_WIDTH, y=200)
        self._send_request_button.place(x=window_width-INFO_BOARD_WIDTH, y=550)
        self._response_text.place(x=window_width-INFO_BOARD_WIDTH, y=600)

    def create_map(self):
        data = self._services.get_game_with_game_id()
        list_actions = self._services.get_game_actions_with_game_id()
        status_data = self._services.get_game_status_with_game_id()

        self._turn = status_data.cur_turn
        self._turn_text.config(text=f"Turn: {str(self._turn)}")
        self.configure_turn_in_request_data()

        self.create_map_from_server(data=data, list_actions=list_actions)
        for side in data.sides:
            if side.team_id == self._team_id:
                self._side = side.side
        self._side_text.config(text=f"Side: {self._side}")

        data = self._request_data.dict()
        pretty_json = json.dumps(data, indent=1)
        self._request_data_text.delete("1.0", tk.END)
        self._request_data_text.insert(tk.END, pretty_json)
        self._time_remain = status_data.remaining
        self._state = State.WAITING
        if self._move_button:
            self._move_button.destroy()
        if self._build_button:
            self._build_button.destroy()
        if self._destroy_button:
            self._destroy_button.destroy()
        self.start()

    def create_map_from_server(self, data: GameResp, list_actions: List[GameActionsResp]):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        grid_width = data.field.width
        grid_height = data.field.height

        self._frame.config(width=window_width, height=window_height)
        self._canvas.config(width=window_width-INFO_BOARD_WIDTH, height=window_height)

        if self._my_map:
            self._my_map.delete()
        self._my_map = Map(canvas=self._canvas, width=grid_width, height=grid_height)
        self._my_map.init_map(data=data, window_width=window_width, window_height=window_height)

        for i in range(0, len(list_actions)):
            if self._turn >= list_actions[i].turn and i == len(list_actions) - 1 or \
                    self._turn >= list_actions[i].turn != list_actions[i + 1].turn:
                destroy_actions = [action for action in list_actions[i].actions if action.action == ActionType.DESTROY]
                build_actions = [action for action in list_actions[i].actions if action.action == ActionType.BUILD]
                move_actions = [action for action in list_actions[i].actions if action.action == ActionType.MOVE]
                for action in destroy_actions:
                    self._my_map.change_map_component_from_actions_response(child_action=action)
                for action in build_actions:
                    self._my_map.change_map_component_from_actions_response(child_action=action)
                for action in move_actions:
                    self._my_map.change_map_component_from_actions_response(child_action=action)

    def update_map(self):
        data = self._services.get_game_with_game_id()
        list_actions = self._services.get_game_actions_with_game_id()
        status_data = self._services.get_game_status_with_game_id()

        self._turn = status_data.cur_turn
        self._turn_text.config(text=f"Turn: {str(self._turn)}")
        self.configure_turn_in_request_data()

        self.update_map_from_server(data=data, list_actions=list_actions)
        for side in data.sides:
            if side.team_id == self._team_id:
                self._side = side.side

        data = self._request_data.dict()
        pretty_json = json.dumps(data, indent=1)
        self._request_data_text.delete("1.0", tk.END)
        self._request_data_text.insert(tk.END, pretty_json)
        self._time_remain = status_data.remaining
        self.start()

    def update_map_from_server(self, data: GameResp, list_actions: List[GameActionsResp]):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        grid_width = data.field.width
        grid_height = data.field.height

        if not self._my_map:
            self._my_map = Map(canvas=self._canvas, width=grid_width, height=grid_height)
            self._my_map.init_map(data=data, window_width=window_width, window_height=window_height)

        if (self._side is Side.A and self._turn % 2 == 0) or \
                (self._side is Side.B and self._turn % 2 == 1):
            self._my_map.reset()
            self._request_data: GameActionsReq = GameActionsReq(turn=self._turn, actions=[])
            self._state = State.WAITING
            if self._stay_button:
                self._stay_button.destroy()
            if self._move_button:
                self._move_button.destroy()
            if self._build_button:
                self._build_button.destroy()
            if self._destroy_button:
                self._destroy_button.destroy()
        for i in range(0, len(list_actions)):
            if (self._turn == list_actions[i].turn and i == len(list_actions) - 1) or \
                    (self._turn == list_actions[i].turn and list_actions[i].turn != list_actions[i+1].turn):
                destroy_actions = [action for action in list_actions[i].actions if action.action == ActionType.DESTROY]
                build_actions = [action for action in list_actions[i].actions if action.action == ActionType.BUILD]
                move_actions = [action for action in list_actions[i].actions if action.action == ActionType.MOVE]
                for action in destroy_actions:
                    self._my_map.change_map_component_from_actions_response(child_action=action)
                for action in build_actions:
                    self._my_map.change_map_component_from_actions_response(child_action=action)
                for action in move_actions:
                    self._my_map.change_map_component_from_actions_response(child_action=action)

    def start(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()

        if self._state == State.WAITING:
            self._craftsman = self._my_map.choose_craftsman(side=self._side,
                                                            window_width=window_width-INFO_BOARD_WIDTH,
                                                            window_height=window_height)
            self._new_action.craftsman_id = self._craftsman.craftsmen_id
            if self._craftsman:
                self._state = State.CHOOSE_ACTION
                self.display_button_choose_action()

    def display_button_choose_action(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        display_x, display_y = self._my_map.get_actual_position(position=self._craftsman.position,
                                                                window_width=window_width-INFO_BOARD_WIDTH,
                                                                window_height=window_height)
        self._stay_button = tk.Button(self._window, text="q: Stay",
                                      font=("Comic Sans", 11), fg="#00FF00", bg="black",
                                      command=lambda: self.display_choose_direction(action_type=ActionType.STAY))
        self._stay_button.place(x=display_x - 100, y=display_y + 50)

        self._move_button = tk.Button(self._window, text="w: Move",
                                      font=("Comic Sans", 11), fg="#00FF00", bg="black",
                                      command=lambda: self.display_choose_direction(action_type=ActionType.MOVE))
        self._move_button.place(x=display_x, y=display_y + 50)

        self._build_button = tk.Button(self._window, text="e: Build",
                                       font=("Comic Sans", 11), fg="#00FF00", bg="black",
                                       command=lambda: self.display_choose_direction(action_type=ActionType.BUILD))
        self._build_button.place(x=display_x + 100, y=display_y + 50)

        self._destroy_button = tk.Button(self._window, text="r: Destroy",
                                         font=("Comic Sans", 11), fg="#00FF00", bg="black",
                                         command=lambda: self.display_choose_direction(action_type=ActionType.DESTROY))
        self._destroy_button.place(x=display_x + 200, y=display_y + 50)

    def store_request(self):
        for action in self._request_data.actions:
            if action.craftsman_id == self._new_action.craftsman_id:
                self._request_data.actions.remove(action)
        self._request_data.actions.append(copy.deepcopy(self._new_action))

        self.configure_turn_in_request_data()
        data = self._request_data.dict()
        pretty_json = json.dumps(data, indent=1)
        self._request_data_text.delete("1.0", tk.END)
        self._request_data_text.insert(tk.END, pretty_json)

    def configure_turn_in_request_data(self):
        self._request_data.turn = self._turn + 1
        if self._side is Side.A and self._request_data.turn % 2 == 1:
            self._request_data.turn += 1
        if self._side is Side.B and self._request_data.turn % 2 == 0:
            self._request_data.turn += 1

    def display_choose_direction(self, action_type: ActionType):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()

        self._stay_button.destroy()
        self._move_button.destroy()
        self._build_button.destroy()
        self._destroy_button.destroy()

        self._my_map.update_choose_action_on_craftsman(craftsman=self._craftsman, action_type=action_type,
                                                       window_width=window_width-INFO_BOARD_WIDTH,
                                                       window_height=window_height)

        self._new_action.action = action_type
        if action_type is ActionType.STAY:
            self._new_action.action_param = None
            self.store_request()
            self._my_map.remove_border_of_craftsman()
            self._my_map.update_queue(position=self._craftsman.position)
            self._my_map.revert_neighbor_color(x=self._craftsman.position.x, y=self._craftsman.position.y)
            self._key_press_list = []
            self._state = State.WAITING
            self.start()
        else:
            self._state = State.CHOOSE_DIRECTION


    def update_timer(self):
        if self._time_remain is None:
            self._time_remain_text.config(text="Time remaining: None")
            return
        if self._time_remain >= 1:
            self._time_remain_text.config(text=f"Time remaining: {self._time_remain}")
            self._time_remain_text.after(1000, self.update_timer)
            self._time_remain -= 1
        elif self._time_remain < 1:
            status_data = self._services.get_game_status_with_game_id()
            if self._turn < status_data.cur_turn:
                self.update_map()
                self._time_remain_text.after(200, self.update_timer)
            else:
                self._time_remain_text.after(500, self.update_timer)

    def send_data(self):
        json_text = self._request_data_text.get("1.0", tk.END)
        data = json.loads(json_text)
        resp = self._services.post_game_actions(GameActionsReq(**data))
        self._response_text.config(text=str(resp))

    def on_key_press(self, keysym: str):
        accepted_key_direction = ["Left", "Right", "Up", "Down"]
        if self._state == State.CHOOSE_DIRECTION:
            if keysym not in self._key_press_list and keysym in accepted_key_direction and len(self._key_press_list) < 2:
                self._key_press_list.append(keysym)

    def on_key_release(self, keysym: str):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        accepted_key_direction = ["Left", "Right", "Up", "Down"]

        if keysym == "Return":
            self._send_request_button.invoke()
            return

        if self._state == State.CHOOSE_ACTION:
            if keysym == "q" and self._stay_button and self._stay_button.winfo_exists():
                self._stay_button.invoke()
            if keysym == "w" and self._move_button and self._move_button.winfo_exists():
                self._move_button.invoke()
            elif keysym == "e" and self._build_button and self._build_button.winfo_exists():
                self._build_button.invoke()
            elif keysym == "r" and self._destroy_button and self._destroy_button.winfo_exists():
                self._destroy_button.invoke()
            return

        if self._state == State.CHOOSE_DIRECTION:
            if keysym not in accepted_key_direction or self._key_press_list == []:
                self._key_press_list = []
                return
            self._new_action.action_param = mapping_from_key_list_to_action_type(action=self._new_action.action,
                                                                                 key_list=self._key_press_list)
            self.store_request()
            self._my_map.choose_direction(window_width=window_width-INFO_BOARD_WIDTH,
                                          window_height=window_height, key_list=self._key_press_list)
            self._my_map.remove_border_of_craftsman()
            self._key_press_list = []
            self._state = State.WAITING
            self.start()
            return
