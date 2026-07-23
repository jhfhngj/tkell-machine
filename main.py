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
    Cell("mover", 0, 0, "right")
]

running = True

ROTATE_CW = {
    "up": "right",
    "right": "down",
    "down": "left",
    "left": "up"
}

def loop():
    if running:
        # Clear canvas
        game.delete("all")
        game.create_rectangle(0, 0, 400, 200, fill="gray")

        for cell in cells:
            # Mover logic
            if cell.type == "mover":
                game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="blue")

                if cell.facing == "right":
                    for rcell in cells:
                                            if rcell is cell:
                                                continue
                                            if (rcell.x == cell.x + 10) and (rcell.y == cell.y):
                                                rcell.x += 10
                    cell.x += 10
                elif cell.facing == "left":
                    for rcell in cells:
                                            if rcell is cell:
                                                continue
                                            if (rcell.x == cell.x - 10) and (rcell.y == cell.y):
                                                rcell.x -= 10
                    cell.x -= 10
                elif cell.facing == "up":
                    for rcell in cells:
                        if rcell is cell:
                            continue
                        if (rcell.y == cell.y - 10) and (rcell.x == cell.x):
                            rcell.y -= 10
                    cell.y -= 10
                elif cell.facing == "down":
                    for rcell in cells:
                        if rcell is cell:
                            continue
                        if (rcell.y == cell.y + 10) and (rcell.x == cell.x):
                            rcell.y += 10
                    cell.y += 10

            # CW rotator logic
            if cell.type == "cwrotator":
                game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="orange")

                for rcell in cells:
                    if rcell is cell:
                        continue

                    # Adjacent check (exactly one cell away)
                    adjacent = (
                        (rcell.x == cell.x - 10 and rcell.y == cell.y) or  # left
                        (rcell.x == cell.x + 10 and rcell.y == cell.y) or  # right
                        (rcell.y == cell.y - 10 and rcell.x == cell.x) or  # up
                        (rcell.y == cell.y + 10 and rcell.x == cell.x)     # down
                    )

                    if adjacent and rcell.facing in ROTATE_CW:
                        rcell.facing = ROTATE_CW[rcell.facing]

    root.after(1000, loop)  # shorter tick for smoother motion

game = Canvas(root, width=400, height=200)
game.pack()

root.after(100, loop)
root.mainloop()
