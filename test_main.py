import tkinter as tk

def button_hover(event):
    button.config(bg='blue')

def button_unhover(event):
    button.config(bg='red')

# Create the Tkinter window
window = tk.Tk()

# Create a button
button = tk.Button(window, text="Hover Button")

# Bind the Enter and Leave events to the button
button.bind("<Enter>", button_hover)
button.bind("<Leave>", button_unhover)

# Pack the button in the window
button.pack()

# Run the Tkinter event loop
window.mainloop()