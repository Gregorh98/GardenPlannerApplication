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
		
		tileWidth = 64 #The dimensions of the representation of one square foot of land
		
		c = Canvas(newWindow, background="#2c3c1e", height=((2*tileWidth)+self.height*tileWidth), width=((2*tileWidth)+self.width*tileWidth))
		c.pack()
		
		for y in range(self.height):
			self.gardenMap.append([])
			for x in range(self.width):
				self.gardenMap[y].append(Plot(c, x, y, tileWidth))
				c.tag_bind(self.gardenMap[y][x].canvasElement, "<Button-1>", self.gardenMap[y][x].outputName)
						
		# id1=str([99,99])
		# print(id1)
		# c.create_rectangle(0, 0, 64, 64, fill="red", tags=id1)
		# c.tag_bind(id1, "<Button-1>", self.hello)
		
		# print(self.gardenMap)
		# for x in self.gardenMap[0]:
			# print(x.id)
		
	def getDimensions(self):
		self.width	= int(self.widthEntryBox.get())
		self.height = int(self.heightEntryBox.get())



class Plot():
	def __init__(self, canvas, x, y, tileWidth):
		self.x = x
		self.y = y
		self.id = str([x,y])
		self.canvasElement = canvas.create_rectangle(tileWidth+x*tileWidth, tileWidth+y*tileWidth, tileWidth+x*tileWidth+tileWidth, tileWidth+y*tileWidth+tileWidth, fill="#52402a", outline="#482f1f")
		
		
	def outputName(self, args):
		print(self.id)
		

A = Settings()
A.root.mainloop()

