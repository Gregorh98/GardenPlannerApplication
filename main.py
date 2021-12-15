from tkinter import *

class Settings:
	def __init__(self):
		self.root = Tk()
		self.root.title("Garden Planner")
		self.drawWindow()
		
	def drawWindow(self):
		Label(self.root, text="Width").grid(row=0, column=0, sticky=W)
		self.widthEntryBox	= Entry(self.root)
		self.widthEntryBox.grid(row=0, column=1)
		
		self.widthEntryBox.focus_set()
		
		Label(self.root, text="Height").grid(row=1, column=0, sticky=W)
		self.heightEntryBox	= Entry(self.root)
		self.heightEntryBox.grid(row=1, column=1)
		
		Button(self.root, text="Map My Garden", command=self.mapGarden).grid(row=2, column=0, columnspan=2)

	def mapGarden(self):
		self.getDimensions()
		self.gardenMap = []
		self.drawGardenMap()
	
	def drawGardenMap(self):
		newWindow = Toplevel(self.root)
		
		tileWidth = 32 #The dimensions of the representation of one square foot of land
		
		c = Canvas(newWindow, background="#2c3c1e", height=((2*tileWidth)+self.height*tileWidth), width=((2*tileWidth)+self.width*tileWidth))
		c.pack()
		
		for y in range(self.height):
			self.gardenMap.append([])
			for x in range(self.width):
				self.gardenMap[y].append(Plot(c, x, y, tileWidth, newWindow))
				c.tag_bind(self.gardenMap[y][x].canvasElement, "<Button-1>", self.gardenMap[y][x].plotClicked)
								
	def getDimensions(self):
		self.width	= int(self.widthEntryBox.get())
		self.height = int(self.heightEntryBox.get())


class Plot():
	def __init__(self, canvas, x, y, tileWidth, root):
		self.x = x
		self.y = y
		self.id = str([x,y])
		self.canvas = canvas
		self.canvasElement = canvas.create_rectangle(tileWidth+x*tileWidth, tileWidth+y*tileWidth, tileWidth+x*tileWidth+tileWidth, tileWidth+y*tileWidth+tileWidth, fill="#52402a", outline="#482f1f")
		self.rootWindow = root
		self.plantedDate = None;
		
	def plotClicked(self, args):
		self.displayWindow()
		
	def displayWindow(self):
		self.plotWindow = Toplevel(self.rootWindow)
		self.plotWindow.title("Edit Plot")
		
		availableCrops = ["Corn", ["Peas"], ["Sprouts"]]
		
		selected = StringVar(self.plotWindow)
		selected.set(availableCrops[0])
		
		cropListbox = Listbox(self.plotWindow, height=3)
		for x in availableCrops:
			cropListbox.insert(END, x)
		cropListbox.pack()
		
		self.canvas.itemconfig(self.canvasElement, fill="#482f1f")
		
class Crop():
	def __init__():
		self.name = name

A = Settings()
A.root.mainloop()

