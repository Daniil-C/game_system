""" Interface for main menu """
import tkinter as tk

F = tk.Frame(borderwidth = 2, relief ="ridge", cursor = "dot", height = 1080, width = 1920)
F.master.columnconfigure(0, weight = 1)
F.master.rowconfigure(0, weight = 1)
F.master.title("IMAGINARIUM")
F.grid_propagate(0)
F.grid(sticky = "NEWS")

F.columnconfigure(0, weight = 1)
F.columnconfigure(1, weight = 1)
F.columnconfigure(2, weight = 1)
F.rowconfigure(0, weight = 1)
F.rowconfigure(1, weight = 1)
F.rowconfigure(2, weight = 1)
F.rowconfigure(3, weight = 1)
F.rowconfigure(4, weight = 1)
F.rowconfigure(5, weight = 1)
F.rowconfigure(6, weight = 1)

Game_name = tk.Label(master = F, text = "IMAGINARIUM")
Game_name.grid(sticky = "NEWS", column = 1, row = 0)

Play_button = tk.Button(master = F, text = "Play")
Play_button.grid(sticky = "NEWS", column = 1, row = 2)

Exit_button = tk.Button(F, text = "Exit", command = F.quit)
Exit_button.grid(sticky = "NEWS", column = 1, row = 4)

Gear = tk.PhotoImage(file="settings.png")
Settings_button = tk.Button(master = F, image = Gear)
Settings_button.grid(sticky = "W", column = 0, row = 6)

tk.mainloop()
