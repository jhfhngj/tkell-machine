from tkinter import *
from sys import argv
from dataclasses import dataclass
import json
from PIL import Image, ImageTk
from time import process_time
from math import floor

root = Tk()
root.title("Tkell Machine")

celltypes = {"mover":[], "cwrotator":[], "ccwrotator":[], "generator":[], "push":[], "wall":[], "tkell":[], "convertigas":[]}
typers = ["mover","cwrotator","ccwrotator","generator","push","wall","tkell","convertigas"]
directions = ["down","right","up","left"]

# Load sprites
for wow in range(8):
	base = Image.open(f"sprite_{wow}.png")
	for i in range(4):
		img = base.rotate((90 * i)-(90 if wow != 3 else -270))
		celltypes[typers[wow]].append(ImageTk.PhotoImage(img))

@dataclass
class Cell:
	type: str
	x: int
	y: int
	facing: str

def load_level(path="level.tkell"):
	global cells
	try:
		with open(path, "r") as f:
			data = json.load(f)
		cells = [Cell(c["type"], c["x"], c["y"], c["facing"]) for c in data]
		print("Loaded:", path)
	except:
		print("Failed to load, loading default...")
		cells = [
			Cell("cwrotator", 10, 10, "down"),
			Cell("cwrotator", 0, 20, "down"),
			Cell("cwrotator", -10, 0, "down"),
			Cell("mover", 0, 0, "right"),
			Cell("generator", 20, 0, "right"),
			Cell("push",40,0,"right")
		]

load_level()

def clamp(n, smallest, largest):
	return max(smallest, min(n, largest))

if len(argv) < 2: argv.append("50")
if len(argv) < 3: argv.append("50")
if len(argv) < 4: argv.append("50")

argv[1] = int(argv[1])
argv[2] = int(argv[2])
argv[3] = int(argv[3])

running = True

ROTATE_CW = {"up":"right","right":"down","down":"left","left":"up"}
ROTATE_CCW = {"up":"left","left":"down","down":"right","right":"up"}

def dup(cell):
	return Cell(cell.type, cell.x, cell.y, cell.facing)

def is_wall(nx, ny):
	return any(c.x == nx and c.y == ny and c.type == "wall" for c in cells)

def push_chain(start_x, start_y, dx, dy):
    chain = []
    x, y = start_x, start_y

    # 1) Build the chain
    while True:
        # stop if outside grid
        if not (0 <= x <= argv[1]*10 and 0 <= y <= argv[2]*10):
            break

        blocker = None
        for c in cells:
            if c.x == x and c.y == y:
                blocker = c
                break

        # stop if no cell or hit a wall
        if blocker is None or blocker.type == "wall":
            break

        chain.append(blocker)
        x += dx
        y += dy

    # 2) Limits
    max_push = max(1, floor(len(cells) / 2))  # count-based cap
    start_time = process_time()
    time_limit = 0.05  # 50ms per push_chain call

    # 3) Push with both limits
    for i, c in enumerate(reversed(chain)):
        # stop if too many cells
        if i >= max_push:
            break

        # stop if too much CPU time
        if process_time() - start_time > time_limit:
            break

        nx = c.x + dx
        ny = c.y + dy

        # don't push into walls or out of bounds
        if not (0 <= nx <= argv[1]*10 and 0 <= ny <= argv[2]*10):
            continue
        if any(w.x == nx and w.y == ny and w.type == "wall" for w in cells):
            continue

        c.x = nx
        c.y = ny

def adjacent(cell,rcell):
	if rcell.x == cell.x and rcell.y == cell.y + 10:
		return True
	if rcell.y == cell.y and rcell.x == cell.x + 10:
		return True
	if rcell.x == cell.x and rcell.y == cell.y - 10:
		return True
	if rcell.y == cell.y and rcell.x == cell.x - 10:
		return True
	return False

def loop():
	global adjacent
	toime = process_time()
	if running:
		game.delete("all")
		game.create_rectangle(0, 0, argv[1]*10, argv[2]*10, fill="black")

		for cell in cells:
			cell.x = clamp(cell.x, 0, argv[1]*10)
			cell.y = clamp(cell.y, 0, argv[2]*10)

			img = celltypes[cell.type][directions.index(cell.facing)]
			game.create_image(cell.x, cell.y, image=img, anchor=NW)

			# Convertigas
			if cell.type == "convertigas":
				cell.y -= 10
				for rcell in cells:
					if rcell is cell:
						continue
					if adjacent(cell, rcell):
						rcell.type = "convertigas"
						rcell.facing = cell.facing
					if rcell.x == cell.x and cell.y == rcell.y:
						cell.y += 10
						rcell.type = "convertigas"
						rcell.facing = cell.facing

			# Tkell Cell
			if cell.type == "tkell":
				x = False
				y = False
				for rcell in cells:
					if rcell is cell:
						continue

					if rcell.x == cell.x:
						x = True
					if rcell.y == cell.y:
						y = True

				# after scanning, move Tkell once
				if x:
					cell.x += 10
				if y:
					cell.y -= 10

				# then apply effect to others
				for rcell in cells:
					if rcell is cell:
						continue

					if x and rcell.x == cell.x - 10:  # old axis
						rcell.x -= 10
					if y and rcell.y == cell.y + 10:  # old axis
						rcell.y += 10

				
			# WALLS
			if cell.type == "wall":
				continue

			# GENERATOR
			if cell.type == "generator":
				if cell.facing == "right":
					for rcell in cells:
						if rcell.x == cell.x - 10 and rcell.y == cell.y and rcell.type != "wall":
							newcell = dup(rcell)
							newcell.x = cell.x + 10
							newcell.y = cell.y
							if not is_wall(newcell.x, newcell.y):
								cells.append(newcell)
								push_chain(cell.x-10, cell.y, 10, 0)

				elif cell.facing == "left":
					for rcell in cells:
						if rcell.x == cell.x + 10 and rcell.y == cell.y and rcell.type != "wall":
							newcell = dup(rcell)
							newcell.x = cell.x - 10
							newcell.y = cell.y
							if not is_wall(newcell.x, newcell.y):
								cells.append(newcell)
								push_chain(cell.x+10, cell.y, -10, 0)

				elif cell.facing == "up":
					for rcell in cells:
						if rcell.y == cell.y + 10 and rcell.x == cell.x and rcell.type != "wall":
							newcell = dup(rcell)
							newcell.y = cell.y - 10
							newcell.x = cell.x
							if not is_wall(newcell.x, newcell.y):
								cells.append(newcell)
								push_chain(cell.x, cell.y-10, 0, -10)

				elif cell.facing == "down":
					for rcell in cells:
						if rcell.y == cell.y - 10 and rcell.x == cell.x and rcell.type != "wall":
							newcell = dup(rcell)
							newcell.y = cell.y + 10
							newcell.x = cell.x
							if not is_wall(newcell.x, newcell.y):
								cells.append(newcell)
								push_chain(cell.x, cell.y+10, 0, 10)

			# ROTATORS
			if cell.type == "cwrotator":
				for rcell in cells:
					if rcell is cell: continue
					adjacent = (
						(rcell.x == cell.x - 10 and rcell.y == cell.y) or
						(rcell.x == cell.x + 10 and rcell.y == cell.y) or
						(rcell.y == cell.y - 10 and rcell.x == cell.x) or
						(rcell.y == cell.y + 10 and rcell.x == cell.x)
					)
					if adjacent and rcell.facing in ROTATE_CW and rcell.type != "wall":
						rcell.facing = ROTATE_CW[rcell.facing]

			if cell.type == "ccwrotator":
				for rcell in cells:
					if rcell is cell: continue
					adjacent = (
						(rcell.x == cell.x - 10 and rcell.y == cell.y) or
						(rcell.x == cell.x + 10 and rcell.y == cell.y) or
						(rcell.y == cell.y - 10 and rcell.x == cell.x) or
						(rcell.y == cell.y + 10 and rcell.x == cell.x)
					)
					if adjacent and rcell.facing in ROTATE_CCW and rcell.type != "wall":
						rcell.facing = ROTATE_CCW[rcell.facing]

			# MOVER
			if cell.type == "mover":
				dx = dy = 0
				if cell.facing == "right": dx = 10
				if cell.facing == "left": dx = -10
				if cell.facing == "up": dy = -10
				if cell.facing == "down": dy = 10

				nx, ny = cell.x + dx, cell.y + dy

				if not is_wall(nx, ny):
					push_chain(nx, ny, dx, dy)
					cell.x = nx
					cell.y = ny

	toimetoo = process_time()
	#print(toime,toimetoo)
	if toimetoo - toime > 0.25 + argv[3]/1000:
		argv[3] += 0.1*1000
		print("Throttling...")
		argv[3] = int(round(argv[3]))

	root.after(argv[3], loop)

game = Canvas(root, width=argv[1]*10, height=argv[2]*10)
game.pack()

arka = root.destroy
def destro():
	arka()
	quit()
root.destroy = destro

root.after(argv[3], loop)
root.mainloop()