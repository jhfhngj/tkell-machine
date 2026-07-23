from tkinter import *
from dataclasses import dataclass

root = Tk()
root.title("Tkell Machine")

@dataclass
class Cell:
    type: str
    x: int
    y: int
    facing: str

cells = [
    Cell("cwrotator", 10, 10, "down"),
    Cell("cwrotator", 0, 20, "down"),
    Cell("cwrotator", -10, 0, "down"),
    Cell("mover", 0, 0, "right"),
    Cell("generator", 20, 0, "right")
]

running = True

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

def dup(cell:Cell):
    return Cell(cell.type, cell.x, cell.y, cell.facing)

# ⭐ CHAIN PUSHING FIX
def push_chain(start_x, start_y, dx, dy):
    chain = []
    x, y = start_x, start_y

    # Find all cells in front in a straight line
    while True:
        blocker = None
        for c in cells:
            if c.x == x and c.y == y:
                blocker = c
                break

        if blocker is None:
            break

        chain.append(blocker)
        x += dx
        y += dy

    # Push entire chain forward
    for c in reversed(chain):
        c.x += dx
        c.y += dy


def loop():
    if running:
        game.delete("all")
        game.create_rectangle(0, 0, 400, 200, fill="gray")

        for cell in cells:
			# Push cell
            if cell.type=="push":
                game.create_rectangle(cell.x,cell.y,cell.x+10,cell.y+10,fill="yellow")
            # Generator
            if cell.type == "generator":
                game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="green")

                if cell.facing == "right":
                    for rcell in cells:
                        if rcell.x == cell.x - 10 and rcell.y == cell.y:
                            newcell = dup(rcell)
                            newcell.x = cell.x + 10
                            newcell.y = cell.y
                            cells.append(newcell)

                elif cell.facing == "left":
                    for rcell in cells:
                        if rcell.x == cell.x + 10 and rcell.y == cell.y:
                            newcell = dup(rcell)
                            newcell.x = cell.x - 10
                            newcell.y = cell.y
                            cells.append(newcell)

                elif cell.facing == "up":
                    for rcell in cells:
                        if rcell.y == cell.y + 10 and rcell.x == cell.x:
                            newcell = dup(rcell)
                            newcell.y = cell.y - 10
                            newcell.x = cell.x
                            cells.append(newcell)

                elif cell.facing == "down":
                    for rcell in cells:
                        if rcell.y == cell.y - 10 and rcell.x == cell.x:
                            newcell = dup(rcell)
                            newcell.y = cell.y + 10
                            newcell.x = cell.x
                            cells.append(newcell)

            # Rotators
            if cell.type == "cwrotator":
                game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="orange")

                for rcell in cells:
                    if rcell is cell:
                        continue

                    adjacent = (
                        (rcell.x == cell.x - 10 and rcell.y == cell.y) or
                        (rcell.x == cell.x + 10 and rcell.y == cell.y) or
                        (rcell.y == cell.y - 10 and rcell.x == cell.x) or
                        (rcell.y == cell.y + 10 and rcell.x == cell.x)
                    )

                    if adjacent and rcell.facing in ROTATE_CW:
                        rcell.facing = ROTATE_CW[rcell.facing]

            if cell.type == "ccwrotator":
                game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="teal")

                for rcell in cells:
                    if rcell is cell:
                        continue

                    adjacent = (
                        (rcell.x == cell.x - 10 and rcell.y == cell.y) or
                        (rcell.x == cell.x + 10 and rcell.y == cell.y) or
                        (rcell.y == cell.y - 10 and rcell.x == cell.x) or
                        (rcell.y == cell.y + 10 and rcell.x == cell.x)
                    )

                    if adjacent and rcell.facing in ROTATE_CCW:
                        rcell.facing = ROTATE_CCW[rcell.facing]

            # Mover
            if cell.type == "mover":
                game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="blue")

                if cell.facing == "right":
                    push_chain(cell.x + 10, cell.y, 10, 0)
                    cell.x += 10

                elif cell.facing == "left":
                    push_chain(cell.x - 10, cell.y, -10, 0)
                    cell.x -= 10

                elif cell.facing == "up":
                    push_chain(cell.x, cell.y - 10, 0, -10)
                    cell.y -= 10

                elif cell.facing == "down":
                    push_chain(cell.x, cell.y + 10, 0, 10)
                    cell.y += 10

    root.after(100, loop)

game = Canvas(root, width=400, height=200)
game.pack()

root.after(100, loop)
root.mainloop()
