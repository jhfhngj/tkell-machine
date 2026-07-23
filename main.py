from tkinter import *
from dataclasses import dataclass
root = Tk()
@dataclass
class Cell():
    type:str
    x:int
    y:int
cells = []
def loop():
    game.create_rectangle(0,0,400,200,fill="black")
    for cell in cells
game = Canvas(root, width=400,height=200)
game.pack()

root.mainloop()