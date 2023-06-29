import tkinter as tk

from helpers import INIT_WIDTH, INIT_HEIGHT
from map import MapController


def resize_map(event):
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    frame.config(width=window_width, height=window_height)
    canvas.config(width=window_width - 100, height=window_height)
    map_controller.resize()


def on_map_click(event):
    map_controller.on_click(event=event)


def check_hover(event):
    map_controller.check_hover(event=event)


window = tk.Tk()
window.geometry(f"{INIT_WIDTH}x{INIT_HEIGHT}")
frame = tk.Frame(window, width=INIT_WIDTH, height=INIT_HEIGHT)
frame.pack(anchor=tk.NW)

canvas = tk.Canvas(frame, width=INIT_WIDTH-100, height=INIT_HEIGHT)
canvas.pack(fill=tk.BOTH, expand=True, anchor=tk.NW)
map_controller = MapController(window=window, canvas=canvas, frame=frame)

canvas.bind("<Button-1>", on_map_click)
canvas.bind("<Motion>", check_hover)

window.bind("<Configure>", resize_map)
window.mainloop()
