import tkinter as tk
import json

def load_json():
    data = {
        "a": 1,
        "b": 1
    }
    try:
        pretty_json = json.dumps(data, indent=4)
        json_entry.delete("1.0", tk.END)
        json_entry.insert(tk.END, pretty_json)
    except json.JSONDecodeError as e:
        json_entry.delete("1.0", tk.END)
        json_entry.insert(tk.END, f"Invalid JSON:\n{str(e)}")

# Create the Tkinter window
window = tk.Tk()

# Create a Text widget for the JSON editor
json_entry = tk.Text(window, font=("Courier New", 12))
json_entry.pack(fill=tk.BOTH, expand=True)

# Create a button to load and format the JSON
load_button = tk.Button(window, text="Load JSON", command=load_json)
load_button.pack()

# Run the Tkinter event loop
window.mainloop()