import tkinter as tk

from PIL import Image, ImageTk

from app.helpers import WALL_B_COLOR, WALL_A_COLOR, CHOOSE_COLOR, BORDER_COLOR, NEUTRAL_COLOR, POND_COLOR, ActionType


class Position:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class AbstractObject:

    def __init__(self, position: Position):
        self.position: Position = position
        self.is_chosen: bool = False
        self.border: int = None
        self.rectangle: int = None
        self.wrapper: int = None
        self.craftsmen_id: str = None

    def delete(self, canvas: tk.Canvas):
        if self.rectangle:
            canvas.delete(self.rectangle)
            self.rectangle = None
        if self.border:
            canvas.delete(self.border)
            self.border = None
        if self.wrapper:
            canvas.delete(self.wrapper)
            self.wrapper = None
        self.is_chosen = False

    def delete_wrapper(self, canvas: tk.Canvas):
        if self.wrapper:
            canvas.delete(self.wrapper)
            self.wrapper = None
        self.is_chosen = False

    def delete_border(self, canvas: tk.Canvas):
        if self.border:
            canvas.delete(self.border)
            self.border = None
        self.is_chosen = False

    def remove_wrapper(self, canvas: tk.Canvas):
        canvas.delete(self.wrapper)
        self.wrapper = None
        self.is_chosen = False

    def display(self, x1: int, y1: int,
                x2: int, y2: int, canvas: tk.Canvas):
        pass

    def change_the_position(self, x1: int, y1: int,
                            x2: int, y2: int, canvas: tk.Canvas):
        pass

    def on_click(self, event, canvas: tk.Canvas,
                 x1: int, y1: int, x2: int, y2: int):
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            return True
        return False

    def on_hover(self, event, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int):
        pass

    def revert_color(self, canvas: tk.Canvas):
        pass

    def change_color(self, canvas: tk.Canvas):
        pass

    def choose_action(self, canvas: tk.Canvas, action_type: ActionType, x1: int, y1: int, x2: int, y2: int):
        pass

    def raise_rectangle(self, canvas: tk.Canvas):
        canvas.tag_raise(self.rectangle)


class AbstractObjectWithColor(AbstractObject):
    color: str

    def __init__(self, position: Position, color: str):
        super().__init__(position=position)
        self.color = color

    def display(self, x1: int, y1: int,
                x2: int, y2: int, canvas: tk.Canvas):
        self.rectangle = canvas.create_rectangle(x1, y1, x2, y2, fill=self.color)

    def change_the_position(self, x1: int, y1: int,
                            x2: int, y2: int, canvas: tk.Canvas):
        if not self.rectangle:
            self.rectangle = canvas.create_rectangle(x1, y1, x2, y2, fill=self.color)
        rect_coords = (x1, y1, x2, y2)
        canvas.coords(self.rectangle, rect_coords)


class AbstractObjectWithImage(AbstractObject):

    def __init__(self, position: Position, image_path: str):
        super().__init__(position=position)
        self.image_path = image_path
        self.image = None
        self.border = None

    def display(self, x1: int, y1: int,
                x2: int, y2: int, canvas: tk.Canvas):
        image = Image.open(self.image_path)
        resized_image = image.resize((int(x2-x1), int(y2-y1)))
        self.image = ImageTk.PhotoImage(resized_image)
        self.rectangle = canvas.create_image(x1, y1, image=self.image, anchor=tk.NW)

    def change_the_position(self, x1: int, y1: int,
                            x2: int, y2: int, canvas: tk.Canvas):
        image = Image.open(self.image_path)
        resized_image = image.resize((int(x2-x1), int(y2-y1)))
        self.image = ImageTk.PhotoImage(resized_image)
        canvas.itemconfig(self.rectangle, image=self.image)
        canvas.coords(self.rectangle, x1, y1)


class Castle(AbstractObjectWithImage):
    def __init__(self, position: Position):
        super().__init__(position=position, image_path="./images/castle.png")


class Pond(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color=POND_COLOR)


class Neutral(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color=NEUTRAL_COLOR)

    def revert_color(self, canvas: tk.Canvas):
        canvas.itemconfig(self.rectangle, fill=NEUTRAL_COLOR)

    def change_color(self, canvas: tk.Canvas):
        canvas.itemconfig(self.rectangle, fill=CHOOSE_COLOR)


class CraftsManA(AbstractObjectWithImage):

    def __init__(self, position: Position, craftsmen_id: str):
        super().__init__(position=position, image_path="./images/craftsmen_a.png")
        self.craftsmen_id = craftsmen_id
        self.is_played = False

    def choose(self, canvas: tk.Canvas,
               x1: int, y1: int, x2: int, y2: int):
        self.is_chosen = True
        if not self.border:
            self.border = canvas.create_rectangle(x1, y1, x2, y2, width=5, outline=BORDER_COLOR)

    def choose_action(self, canvas: tk.Canvas, action_type: ActionType, x1: int, y1: int, x2: int, y2: int):
        if self.wrapper:
            canvas.delete(self.wrapper)
            self.wrapper = None
        text_x = int(x1 + (x2 - x1) / 2)
        text_y = int(y1 + (y2 - y1) / 2)
        self.wrapper = canvas.create_text(text_x, text_y, text=action_type, font=("Arial", 10), fill=BORDER_COLOR)


class CraftsManB(AbstractObjectWithImage):
    def __init__(self, position: Position, craftsmen_id: str):
        super().__init__(position=position, image_path="./images/craftsmen_b.png")
        self.craftsmen_id = craftsmen_id
        self.is_played = False

    def choose(self, canvas: tk.Canvas,
               x1: int, y1: int, x2: int, y2: int):
        self.is_chosen = True
        if not self.border:
            self.border = canvas.create_rectangle(x1, y1, x2, y2, width=5, outline=BORDER_COLOR)

    def choose_action(self, canvas: tk.Canvas, action_type: ActionType, x1: int, y1: int, x2: int, y2: int):
        if self.wrapper:
            canvas.delete(self.wrapper)
            self.wrapper = None
        text_x = int(x1 + (x2 - x1) / 2)
        text_y = int(y1 + (y2 - y1) / 2)
        self.wrapper = canvas.create_text(text_x, text_y, text=action_type, font=("Arial", 10), fill=BORDER_COLOR)


class WallA(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color=WALL_A_COLOR)

    def revert_color(self, canvas: tk.Canvas):
        canvas.itemconfig(self.rectangle, fill=WALL_A_COLOR)

    def change_color(self, canvas: tk.Canvas):
        canvas.itemconfig(self.rectangle, fill=CHOOSE_COLOR)


class WallB(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color=WALL_B_COLOR)

    def revert_color(self, canvas: tk.Canvas):
        canvas.itemconfig(self.rectangle, fill=WALL_B_COLOR)

    def change_color(self, canvas: tk.Canvas):
        canvas.itemconfig(self.rectangle, fill=CHOOSE_COLOR)


class OpenTerritoryA(AbstractObjectWithColor):
    pass


class OpenTerritoryB(AbstractObjectWithColor):
    pass


class CloseTerritoryA(AbstractObjectWithColor):
    pass


class CloseTerritoryB(AbstractObjectWithColor):
    pass
