import tkinter as tk
from random import Random
from tkinter import *

id_000 = ["molar office ishmeal","sollem lament yi sang"]##list
Prescripts = ["solo lei heng with a base sinner", "do a mirror dungeon extreme run with "+Random().choice(id_000)+" solo", "Read the entirty of orv and the sequal within four months"]##list
root = tk.Tk()
root.title("precript proxy system")
root.geometry("350x200")
root.configure(background="#000000")
tk.box_color = (light_blue := "#000000")
tk.text_color = (black := "#6A9EFF")
label = tk.Label(root, text="Press to recive a Prescript by the Will Of The City",
                 wraplength=300, font=("Arial", 16), fg=tk.text_color, bg=tk.box_color)
label.pack(pady=20)




def on_click():##function and also user output
    if not Prescripts:
        label.config(text="No more Prescripts available.")
        return
    for _ in range(len(Prescripts)):##alogrithm to randomize the output and also remove the used one from the list
        random_index = Random().randint(0, len(Prescripts) - 1)
        if 0 <= random_index < len(Prescripts):
            random_sentence = Prescripts.pop(random_index)
            label.config(text=random_sentence)
            break

button = tk.Button(root, text="Recive?", command=on_click)## user input
button.pack()
root.mainloop()