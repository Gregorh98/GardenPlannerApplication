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
		gardenMap = []
		for y in range(self.height):
			gardenMap.append([])
			for x in range(self.width):
				gardenMap[y].append({})
		
		print(gardenMap)
		self.drawGardenMap()
	
	def drawGardenMap(self):
		newWindow = Toplevel(self.root)
		
		tileWidth = 32 #The dimensions of the representation of one square foot of land
		
		c = Canvas(newWindow, background="#009A17", height=(self.height*tileWidth), width=(self.width*tileWidth))
		c.pack()
		
		for y in range(self.height):
			for x in range(self.width):
				c.create_rectangle(x*tileWidth, y*tileWidth, x*tileWidth+tileWidth, y*tileWidth+tileWidth, fill="brown")
		
	def getDimensions(self):
		self.width	= int(self.widthEntryBox.get())
		self.height = int(self.heightEntryBox.get())

A = Settings()
A.root.mainloop()

