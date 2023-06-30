import tkinter as tk

from PIL import Image, ImageTk


class Position:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class AbstractObject:
    position: Position
    rectangle: int
    border: int
    is_chosen: bool

    def __init__(self, position: Position):
        self.position = position
        self.is_chosen = False
        self.border = None
        self.rectangle = None

    def delete(self, canvas: tk.Canvas):
        if self.rectangle:
            canvas.delete(self.rectangle)
        if self.border:
            canvas.delete(self.border)

    def display(self, x1: int, y1: int,
                x2: int, y2: int, canvas: tk.Canvas):
        pass

    def change_the_position(self, x1: int, y1: int,
                            x2: int, y2: int, canvas: tk.Canvas):
        pass

    def on_click(self, event, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int):
        return False

    def on_hover(self, event, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int):
        pass

    def change_color(self, canvas: tk.Canvas):
        pass


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
        super().__init__(position=position, image_path="images/castle.png")


class Pond(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color="black")


class Neutral(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color='white')

    def on_hover(self, event, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int):
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            canvas.itemconfig(self.rectangle, fill='blue')
        else:
            if not self.is_chosen:
                canvas.itemconfig(self.rectangle, fill='white')

    def on_click(self, event, canvas: tk.Canvas,
                 x1: int, y1: int, x2: int, y2: int):
        if not self.is_chosen:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.is_chosen = True
                return True
        return False

    def change_color(self, canvas: tk.Canvas):
        if self.is_chosen:
            canvas.itemconfig(self.rectangle, fill='blue')


class CraftsMenA(AbstractObjectWithImage):

    def __init__(self, position: Position):
        super().__init__(position=position, image_path="images/craftsmen_a.png")

    def on_click(self, event, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int):
        if not self.is_chosen:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.is_chosen = True
                self.border = canvas.create_rectangle(x1, y1, x2, y2, width=5, outline="red")
                return True
        return False


class CraftsMenB(AbstractObjectWithImage):
    def __init__(self, position: Position):
        super().__init__(position=position, image_path="images/craftsmen_b.png")


class WallA(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color='blue')


class WallB(AbstractObjectWithColor):
    def __init__(self, position: Position):
        super().__init__(position=position, color='pink')


class OpenTerritoryA(AbstractObjectWithColor):
    pass


class OpenTerritoryB(AbstractObjectWithColor):
    pass


class CloseTerritoryA(AbstractObjectWithColor):
    pass


class CloseTerritoryB(AbstractObjectWithColor):
    pass
