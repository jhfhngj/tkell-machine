from tkinter import *
import json
from PIL import Image, ImageTk

root = Tk()
root.title("Tkell Machine Editor")

CELL_SIZE = 10
GRID_W = 50
GRID_H = 50

selected_type = "mover"
facer = "right"
cells = []

directions = ["up","right","down","left"]

# EXACT same type order as simulation
typers = ["mover","cwrotator","ccwrotator","generator","push"]

# sprite storage
cell_sprites = {t: [] for t in typers}

def load_sprites():
    # EXACT same rotation logic as your simulation
    for wow in range(5):
        base = Image.open(f"sprite_{wow}.png")

        for i in range(4):
            # generator (wow == 3) is special
            if wow != 3:
                # base sprite faces RIGHT
                img = base.rotate((90 * i) - 90)
            else:
                # generator sprite faces UP
                img = base.rotate((90 * i) + 270)

            cell_sprites[typers[wow]].append(ImageTk.PhotoImage(img))

load_sprites()

# FIX Y‑AXIS FLIP
display_dir_map = {
    "up": "down",
    "down": "up",
    "left": "left",
    "right": "right"
}

def snap(v):
    return (v // CELL_SIZE) * CELL_SIZE

def place_cell(event):
    x = snap(event.x)-10
    y = snap(event.y)-10

    for c in cells:
        if c["x"] == x and c["y"] == y:
            c["type"] = selected_type
            c["facing"] = facer
            draw()
            return

    cells.append({"type": selected_type, "x": x, "y": y, "facing": facer})
    draw()

def delete_cell(event):
    x = snap(event.x)-10
    y = snap(event.y)-10

    cells[:] = [c for c in cells if not (c["x"] == x and c["y"] == y)]
    draw()

def rotate_cell(event):
    x = snap(event.x)
    y = snap(event.y)

    for c in cells:
        if c["x"] == x and c["y"] == y:
            idx = directions.index(c["facing"])
            c["facing"] = directions[(idx + 1) % 4]
            break

    draw()

def draw():
    canvas.delete("all")
    canvas.create_rectangle(0,0,GRID_W*CELL_SIZE,GRID_H*CELL_SIZE,fill="black")

    canvas.create_text(
        5, 5,
        text=f"Selected: {selected_type}\nFacing: {facer}",
        fill="white",
        anchor=NW,
        font=("Consolas", 10)
    )

    for c in cells:
        if c["type"] in cell_sprites:
            imgs = cell_sprites[c["type"]]

            # FIXED: use flipped direction for sprite selection
            disp_dir = display_dir_map[c["facing"]]
            img = imgs[directions.index(disp_dir)]

            canvas.create_image(c["x"], c["y"], image=img, anchor=NW)
        else:
            canvas.create_rectangle(
                c["x"], c["y"],
                c["x"]+CELL_SIZE, c["y"]+CELL_SIZE,
                fill="white"
            )

ROTATE_CW = {
    "up": "right",
    "right": "down",
    "down": "left",
    "left": "up"
}
ROTATE_CCW = {
    "up": "left",
    "left": "down",
    "down": "right",
    "right": "up"
}

def key(event):
    global selected_type, facer
    if event.char == "1": selected_type = "mover"
    if event.char == "2": selected_type = "generator"
    if event.char == "3": selected_type = "cwrotator"
    if event.char == "4": selected_type = "ccwrotator"
    if event.char == "5": selected_type = "push"

    if event.char == "e": facer = ROTATE_CW[facer]
    if event.char == "q": facer = ROTATE_CCW[facer]

    draw()

def save():
    with open("level.tkell","w") as f:
        json.dump(cells,f)
    print("Saved level.tkell")

def load():
    global cells
    try:
        with open("level.tkell","r") as f:
            cells = json.load(f)
        print("Loaded level.tkell")
    except Exception as e:
        print("No level file found:", e)
    draw()

canvas = Canvas(root, width=GRID_W*CELL_SIZE, height=GRID_H*CELL_SIZE)
canvas.pack()

canvas.bind("<Button-1>", place_cell)
canvas.bind("<Button-3>", delete_cell)
canvas.bind("<Button-2>", rotate_cell)
root.bind("<Key>", key)

Button(root, text="Save", command=save).pack(side=LEFT)
Button(root, text="Load", command=load).pack(side=LEFT)

draw()
root.mainloop()
