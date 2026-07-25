from tkinter import *
from sys import argv
from dataclasses import dataclass
import json
from PIL import Image, ImageTk
from time import process_time

root = Tk()
root.title("Tkell Machine")
celltypes = {"mover":[],"cwrotator":[],"ccwrotator":[],"generator":[],"push":[],}
typers = ["mover","cwrotator","ccwrotator","generator","push"]
directions = ["down","right","up","left"]
o = 0
for wow in range(5):
	base = Image.open(f"sprite_{wow}.png")
	i = -90
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

		cells = []
		for c in data:
			cells.append(Cell(
				c["type"],
				c["x"],
				c["y"],
				c["facing"]
			))

		print("Loaded:", path)

	except Exception as e:
		print("Failed to load:", e)
		print("Loading default...")
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

if len(argv) < 2:
	argv.append("50")
if len(argv) < 3:
	argv.append("50")
if len(argv) < 4:
	argv.append("50")

argv[1] = int(argv[1])
argv[2] = int(argv[2])
argv[3] = int(argv[3])

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

def push_chain(start_x, start_y, dx, dy):
	chain = []
	x, y = start_x, start_y
	startime = process_time()
	while True:
		# stop if next position is outside grid
		if not (0 <= x <= argv[1]*10 and 0 <= y <= argv[2]*10):
			break

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

	for c in reversed(chain):
		if not (process_time() - startime > 100):
			c.x += dx
			c.y += dy
			startime = process_time()
		else:
			break

def loop():
	toime = process_time()
	if running:
		game.delete("all")
		game.create_rectangle(0, 0, argv[1]*10, argv[2]*10, fill="black")
		
		for cell in cells:
			cell.x = clamp(cell.x,0,argv[1]*10)
			cell.y = clamp(cell.y,0,argv[2]*10)

			sethc = celltypes[cell.type]
			# Push cell
			if cell.type=="push":
				#game.create_rectangle(cell.x,cell.y,cell.x+10,cell.y+10,fill="yellow")
				img = sethc[directions.index(cell.facing)]
				game.create_image(cell.x, cell.y, image = img, anchor = NW)
			# Generator
			if cell.type == "generator":
				#game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="green")
				img = sethc[directions.index(cell.facing)]
				game.create_image(cell.x, cell.y, image = img, anchor = NW)
				if cell.facing == "right":
					for rcell in cells:
						if rcell.x == cell.x - 10 and rcell.y == cell.y:
							newcell = dup(rcell)
							newcell.x = cell.x + 10
							newcell.y = cell.y
							cells.append(newcell)
							push_chain(cell.x-10,cell.y,10,0)

				elif cell.facing == "left":
					for rcell in cells:
						if rcell.x == cell.x + 10 and rcell.y == cell.y:
							newcell = dup(rcell)
							newcell.x = cell.x - 10
							newcell.y = cell.y
							cells.append(newcell)
							push_chain(cell.x+10,cell.y,-10,0)

				elif cell.facing == "up":
					for rcell in cells:
						if rcell.y == cell.y + 10 and rcell.x == cell.x:
							newcell = dup(rcell)
							newcell.y = cell.y - 10
							newcell.x = cell.x
							cells.append(newcell)
							push_chain(cell.x,cell.y-10,0,-10)

				elif cell.facing == "down":
					for rcell in cells:
						if rcell.y == cell.y - 10 and rcell.x == cell.x:
							newcell = dup(rcell)
							newcell.y = cell.y + 10
							newcell.x = cell.x
							cells.append(newcell)
							push_chain(cell.x,cell.y+10,0,10)

			# Rotators
			if cell.type == "cwrotator":
				#game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="orange")
				img = sethc[directions.index(cell.facing)]
				game.create_image(cell.x, cell.y, image = img, anchor = NW)
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
				#game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="teal")
				img = sethc[directions.index(cell.facing)]
				game.create_image(cell.x, cell.y, image = img, anchor = NW)
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
				#game.create_rectangle(cell.x, cell.y, cell.x+10, cell.y+10, fill="blue")
				img = sethc[directions.index(cell.facing)]
				game.create_image(cell.x, cell.y, image = img, anchor = NW)
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
	toimetoo = process_time()
	if toimetoo - toime > 100+argv[3]:
		argv[3] += 200

	root.after(argv[3], loop)

game = Canvas(root, width=argv[1]*10, height=argv[2]*10)
game.pack()

root.after(argv[3], loop)
root.mainloop()
