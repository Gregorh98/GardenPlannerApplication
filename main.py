import tkinter.messagebox
from tkinter import *


class Main:
    def __init__(self):
        self.root = Tk()
        self.root.title("Garden Planner")
        self.height = 0
        self.width = 0
        self.tileWidth = 32  # The dimensions of the representation of one square foot of land
        self.gardenMap = []
        self.drawGardenMap()

    def configurePlotSize(self):
        self.configurationWindow = Toplevel(self.root)

        Label(self.configurationWindow, text="Width").grid(row=0, column=0, sticky=W)
        self.widthEntryBox = Entry(self.configurationWindow)
        self.widthEntryBox.grid(row=0, column=1)

        self.widthEntryBox.focus_set()

        Label(self.configurationWindow, text="Height").grid(row=1, column=0, sticky=W)
        self.heightEntryBox = Entry(self.configurationWindow)
        self.heightEntryBox.grid(row=1, column=1)

        Button(self.configurationWindow, text="Map My Garden", command=self.updateGarden).grid(row=2, column=0,
                                                                                               columnspan=2)

    def updateGarden(self):
        if self.gardenMap != []:
            overwriteConfirm = tkinter.messagebox.askyesno(title="Overwrite Warning",
                                                           message="This will overwrite the current plot. Do you wish to continue?")
            if overwriteConfirm == False:
                self.configurationWindow.destroy()
                tkinter.messagebox.showinfo(title="Overwrite Aborted", message="Configuration update cancelled")
                return

        self.height = int(self.heightEntryBox.get())
        self.width = int(self.widthEntryBox.get())

        self.gardenMap = []

        self.c.delete("all")

        for y in range(self.height):
            self.gardenMap.append([])
            for x in range(self.width):
                self.gardenMap[y].append(Plot(self.c, x, y, self.tileWidth, self.root))
                self.c.tag_bind(self.gardenMap[y][x].canvasElement, "<Button-1>", self.gardenMap[y][x].plotClicked)

        self.c.configure(height=((2 * self.tileWidth) + self.height * self.tileWidth),
                         width=((2 * self.tileWidth) + self.width * self.tileWidth))
        self.configurationWindow.destroy()

    def loadFile(self):
        pass

    def saveFile(self):
        pass

    def drawGardenMap(self):
        self.c = Canvas(self.root, background="#2c3c1e", height=((2 * self.tileWidth) + self.height * self.tileWidth),
                        width=((2 * self.tileWidth) + self.width * self.tileWidth))
        self.c.grid(row=0, column=0)

        buttonFrame = Frame(self.root)

        loadButton = Button(buttonFrame, text="Configure\nPlot Size", command=self.configurePlotSize)
        loadButton.grid(row=0, column=0, padx=2, pady=1, sticky=EW)

        saveButton = Button(buttonFrame, text="Load", command=self.loadFile)
        saveButton.grid(row=1, column=0, padx=2, pady=1, sticky=EW)

        configButton = Button(buttonFrame, text="Save", command=self.saveFile)
        configButton.grid(row=2, column=0, padx=2, pady=1, sticky=EW)

        buttonFrame.grid(row=0, column=1, sticky=N)

        for y in range(self.height):
            self.gardenMap.append([])
            for x in range(self.width):
                self.gardenMap[y].append(Plot(self.c, x, y, self.tileWidth, self.root))
                self.c.tag_bind(self.gardenMap[y][x].canvasElement, "<Button-1>", self.gardenMap[y][x].plotClicked)

    def getDimensions(self):
        self.width = int(self.widthEntryBox.get())
        self.height = int(self.heightEntryBox.get())


class Plot():
    def __init__(self, canvas, x, y, tileWidth, root):
        self.x = x
        self.y = y
        self.id = str([x, y])
        self.canvas = canvas
        self.canvasElement = canvas.create_rectangle(tileWidth + x * tileWidth, tileWidth + y * tileWidth,
                                                     tileWidth + x * tileWidth + tileWidth,
                                                     tileWidth + y * tileWidth + tileWidth, fill="#52402a",
                                                     outline="#482f1f")
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


A = Main()
A.root.mainloop()
