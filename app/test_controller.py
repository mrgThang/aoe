import tkinter as tk

from app.helpers import State, Side, INIT_WIDTH, INFO_BOARD_WIDTH, ActionType, INIT_HEIGHT
from app.map import Map
from app.utils import mapping_from_key_list_to_action_type
from map_components import CraftsManA
from models import GameResp, GameActionsResp


class TestController:

    def __init__(self, window: tk.Tk, frame: tk.Frame, canvas: tk.Canvas):
        self._window: tk.Tk = window
        self._frame: tk.Frame = frame
        self._canvas: tk.Canvas = canvas
        self._state: State = State.WAITING
        self._craftsman: CraftsManA = None

        self._key_press_list = []
        self._stay_button: tk.Button = None
        self._move_button: tk.Button = None
        self._build_button: tk.Button = None
        self._destroy_button: tk.Button = None

        self._point_text: tk.Label = tk.Label(self._frame, text="A:0 B:0", font=("Arial", 12))
        self._point_text.place(x=INIT_WIDTH - INFO_BOARD_WIDTH, y=100)
        self._point_text.pack()

        self._list_actions = GameActionsResp(actions=[])
        self._side = Side.A
        self._cur_action = ActionType.MOVE

        self._my_map: Map = None
        self.init_map()

    def init_map(self):
        window_width = INIT_WIDTH
        window_height = INIT_HEIGHT
        grid_width = 11
        grid_height = 11

        self._frame.config(width=window_width, height=window_height)
        self._canvas.config(width=window_width-INFO_BOARD_WIDTH, height=window_height)

        if self._my_map:
            self._my_map.delete()
        self._my_map = Map(canvas=self._canvas, width=grid_width, height=grid_height)
        self._my_map.init_map(
            data=GameResp(
                field=GameResp.Field(
                    castle_coeff=10,
                    wall_coeff=1,
                    territory_coeff=1,
                    width=grid_width,
                    height=grid_height,
                    ponds=[
                        GameResp.Field.PondResp(x=0, y=0)
                    ],
                    castles=[GameResp.Field.CastleResp(x=7, y=7)],
                    craftsmen=[
                        GameResp.Field.CraftsMenResp(x=1, y=1, side=Side.A, id="1"),
                        GameResp.Field.CraftsMenResp(x=2, y=2, side=Side.A, id="2"),
                        GameResp.Field.CraftsMenResp(x=3, y=3, side=Side.A, id="3"),
                        GameResp.Field.CraftsMenResp(x=4, y=4, side=Side.B, id="4"),
                        GameResp.Field.CraftsMenResp(x=5, y=5, side=Side.B, id="5"),
                        GameResp.Field.CraftsMenResp(x=6, y=6, side=Side.B, id="6")
                    ]
                )
            ),
            window_width=grid_width,
            window_height=grid_height
        )

        (point_a, point_b) = self._my_map.calculate_point()
        self._point_text.config(text=f"A:{point_a} B:{point_b}")

        self._state = State.WAITING
        if self._move_button:
            self._move_button.destroy()
        if self._build_button:
            self._build_button.destroy()
        if self._destroy_button:
            self._destroy_button.destroy()
        self.start()

    def resize(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        if self._my_map:
            self._my_map.resize(window_width=window_width-INFO_BOARD_WIDTH, window_height=window_height)
        self._point_text.place(x=window_width - INFO_BOARD_WIDTH, y=100)

    def update_map(self):
        destroy_actions = [action for action in self._list_actions.actions if action.action == ActionType.DESTROY]
        build_actions = [action for action in self._list_actions.actions if action.action == ActionType.BUILD]
        move_actions = [action for action in self._list_actions.actions if action.action == ActionType.MOVE]
        for action in destroy_actions:
            self._my_map.change_map_component_from_actions_response(child_action=action)
        for action in build_actions:
            self._my_map.change_map_component_from_actions_response(child_action=action)
        for action in move_actions:
            self._my_map.change_map_component_from_actions_response(child_action=action)
        self._my_map.update_territory_status()
        self._my_map.remove_is_played()
        self._my_map.reset()

        (point_a, point_b) = self._my_map.calculate_point()
        self._point_text.config(text=f"A:{point_a} B:{point_b}")

        self._list_actions = GameActionsResp(actions=[])

        self._state = State.WAITING
        if self._stay_button:
            self._stay_button.destroy()
        if self._move_button:
            self._move_button.destroy()
        if self._build_button:
            self._build_button.destroy()
        if self._destroy_button:
            self._destroy_button.destroy()

        self.start()

    def start(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()

        if self._state == State.WAITING:
            self._craftsman = self._my_map.choose_craftsman_without_loop(
                side=self._side,
                window_width=window_width-INFO_BOARD_WIDTH,
                window_height=window_height)
            if self._craftsman is None:
                if self._side == Side.A:
                    self._side = Side.B
                else:
                    self._side = Side.A
                self.update_map()
            if self._craftsman:
                self._state = State.CHOOSE_ACTION
                self.display_button_choose_action()

    def display_button_choose_action(self):
        window_width = self._window.winfo_width()
        window_height = self._window.winfo_height()
        display_x, display_y = self._my_map.get_actual_position(position=self._craftsman.position,
                                                                window_width=window_width-INFO_BOARD_WIDTH,
                                                                window_height=window_height)
        if self._stay_button:
            self._stay_button.destroy()
        if self._move_button:
            self._move_button.destroy()
        if self._build_button:
            self._build_button.destroy()
        if self._destroy_button:
            self._destroy_button.destroy()

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

        if action_type is ActionType.STAY:
            self._list_actions.actions.append(
                GameActionsResp.ChildAction(
                    action=ActionType.STAY,
                    action_param=None,
                    craftsman_id=self._craftsman.craftsmen_id
                )
            )
            self._my_map.remove_border_of_craftsman()
            self._my_map.update_queue(position=self._craftsman.position)
            self._my_map.revert_neighbor_color(x=self._craftsman.position.x, y=self._craftsman.position.y)
            self._key_press_list = []
            self._state = State.WAITING
            self.start()
        else:
            self._cur_action = action_type
            self._state = State.CHOOSE_DIRECTION

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
            self._list_actions.actions.append(
                GameActionsResp.ChildAction(
                    action=self._cur_action,
                    action_param=mapping_from_key_list_to_action_type(action=self._cur_action,
                                                                      key_list=self._key_press_list),
                    craftsman_id=self._craftsman.craftsmen_id
                )
            )

            self._my_map.choose_direction(window_width=window_width-INFO_BOARD_WIDTH,
                                          window_height=window_height, key_list=self._key_press_list)
            self._my_map.remove_border_of_craftsman()
            self._key_press_list = []
            self._state = State.WAITING
            self.start()
            return
