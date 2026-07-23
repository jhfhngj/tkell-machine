from tkinter import *
import json

root = Tk()
root.title("Tkell Machine")

CELL_SIZE = 10
GRID_W = 50
GRID_H = 50

selected_type = "mover"
facer = "right"
cells = []

def snap(v):
    return (v // CELL_SIZE) * CELL_SIZE

def place_cell(event):
    x = snap(event.x)
    y = snap(event.y)

    # overwrite existing cell
    for c in cells:
        if c["x"] == x and c["y"] == y:
            c["type"] = selected_type
            draw()
            return

    cells.append({"type": selected_type, "x": x, "y": y, "facing": facer})
    draw()

def delete_cell(event):
    x = snap(event.x)
    y = snap(event.y)

    cells[:] = [c for c in cells if not (c["x"] == x and c["y"] == y)]
    draw()

def rotate_cell(event):
    x = snap(event.x)
    y = snap(event.y)

    for c in cells:
        if c["x"] == x and c["y"] == y:
            dirs = ["up","right","down","left"]
            c["facing"] = dirs[(dirs.index(c["facing"]) + 1) % 4]
            break

    draw()

def draw():
    canvas.delete("all")
    canvas.create_rectangle(0,0,GRID_W*CELL_SIZE,GRID_H*CELL_SIZE,fill="black")
    canvas.create_text(60,20,text="Selected: "+selected_type+"\nRotation: "+facer,fill="white")

    for c in cells:
        color = {
            "mover":"blue",
            "generator":"green",
            "cwrotator":"orange",
            "ccwrotator":"teal",
            "push":"yellow"
        }.get(c["type"], "white")

        canvas.create_rectangle(c["x"], c["y"], c["x"]+CELL_SIZE, c["y"]+CELL_SIZE, fill=color)
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
        draw()
        print("Loaded level.tkell")
    except:
        print("No level file found")

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
