import datetime
import json
import tkinter.messagebox
from tkinter import *
from PIL import ImageGrab

from os.path import exists
from _plot import Plot
from _plant import Plant
from _resources import *


#TODO - Split this all out into different files

class Main:
    def __init__(self):
        self.root = Tk()
        self.root.title("Square Foot Garden Planner")
        self.height = 2
        self.width = 3
        self.tileWidth = 64  # The dimensions of the representation of one square foot of land
        self.configurationWindow = None

        self.gardenMap = []
        self.drawGardenMap()

        loadGardenOnLaunch = True
        if exists("garden.json") and loadGardenOnLaunch:
            self.gardenMap = []
            self.loadGarden()
            return

    def configurePlotSize(self):
        self.configurationWindow = Toplevel(self.root)

        Label(self.configurationWindow, text="Width").grid(row=0, column=0, sticky=W)
        self.widthEntryBox = Entry(self.configurationWindow)
        self.widthEntryBox.grid(row=0, column=1)

        self.widthEntryBox.focus_set()

        Label(self.configurationWindow, text="Height").grid(row=1, column=0, sticky=W)
        self.heightEntryBox = Entry(self.configurationWindow)
        self.heightEntryBox.grid(row=1, column=1)

        Button(self.configurationWindow, text="Map My Garden", command=lambda :self.updateGarden(int(self.heightEntryBox.get()), int(self.widthEntryBox.get()))).grid(row=2, column=0, columnspan=2)

    def updateGarden(self, height, width):
        if self.gardenMap != []:
            overwriteConfirm = tkinter.messagebox.askyesno(title="Overwrite Warning",
                                                           message="This will overwrite the current plot. Do you wish to continue?")
            if overwriteConfirm == False:
                self.configurationWindow.destroy()
                tkinter.messagebox.showinfo(title="Overwrite Aborted", message="Configuration update cancelled")
                return

        self.height = height
        self.width = width

        self.gardenMap = []

        self.c.delete("all")

        self.c.create_rectangle(self.tileWidth - (self.tileWidth / 8), self.tileWidth - (self.tileWidth / 8),
                                (self.tileWidth * self.width) + self.tileWidth + (self.tileWidth / 8),
                                (self.tileWidth * self.height) + self.tileWidth + (self.tileWidth / 8), fill=cWood)

        for y in range(self.height):
            self.gardenMap.append([])
            for x in range(self.width):
                newPlot = Plot(x, y, self.root, self.tileWidth)
                newPlot.draw(self.c)
                self.gardenMap[y].append(newPlot)

        self.c.configure(height=((2 * self.tileWidth) + self.height * self.tileWidth),
                         width=((2 * self.tileWidth) + self.width * self.tileWidth))
        if self.configurationWindow is not None:
            self.configurationWindow.destroy()

    def saveImage(self):
        x = self.root.winfo_rootx() + self.c.winfo_x()
        y = self.root.winfo_rooty() + self.c.winfo_y()
        x1 = x + self.c.winfo_width()
        y1 = y + self.c.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(imageExportPath)

    def saveGarden(self):
        save = {}
        # General settings
        save["general"] = {
            "tileWidth":    self.tileWidth,
            "gardenWidth":  self.width,
            "gardenHeight": self.height
        }

        # Plot Settings
        for row in self.gardenMap:
            for plot in row:
                save[plot.id] = {}
                if plot.plant is not None:
                    # noinspection PyTypeChecker
                    save[plot.id]["plant"] = {
                        "name":         plot.plant.name,
                        "id":           plot.plant.id,
                        "plantingDate": plot.plant.plantingDate
                    }
                else:
                    # noinspection PyTypeChecker
                    save[plot.id]["plant"] = None

        jsonDump = json.dumps(save, default=str)
        with open(saveExportPath, "w") as f:
            f.write(jsonDump)

    def loadGarden(self):
        with open(saveExportPath, "r") as f:
            jsonDump = json.loads(f.read())
        # Update height and width
        height = jsonDump["general"]["gardenHeight"]
        width = jsonDump["general"]["gardenWidth"]
        self.updateGarden(height, width)
        for row in self.gardenMap:
            for plot in row:
                #Update plant in plot
                plotPlant = jsonDump[f"[{plot.x}, {plot.y}]"]["plant"]
                if plotPlant is not None:
                    self.gardenMap[plot.y][plot.x].plant = Plant(plotPlant["name"], plotPlant["id"], datetime.date.fromisoformat(plotPlant["plantingDate"]))
                    self.gardenMap[plot.y][plot.x].updateOnLoad()

    def drawGardenMap(self):
        self.c = Canvas(self.root, background=cGrass, height=((2 * self.tileWidth) + self.height * self.tileWidth),
                        width=((2 * self.tileWidth) + self.width * self.tileWidth))
        self.c.grid(row=0, column=0)

        buttonFrame = Frame(self.root)

        configButton = Button(buttonFrame, text="Configure\nPlot Size", command=self.configurePlotSize)
        configButton.grid(row=0, column=0, padx=2, pady=1, sticky=EW)

        saveImageButton = Button(buttonFrame, text="Save Image", command=self.saveImage)
        saveImageButton.grid(row=1, column=0, padx=2, pady=1, sticky=EW)

        saveButton = Button(buttonFrame, text="Save Garden", command=self.saveGarden)
        saveButton.grid(row=2, column=0, padx=2, pady=1, sticky=EW)

        loadButton = Button(buttonFrame, text="Load Garden", command=self.loadGarden)
        loadButton.grid(row=3, column=0, padx=2, pady=1, sticky=EW)

        buttonFrame.grid(row=0, column=1, sticky=N)

        self.c.create_rectangle(self.tileWidth-(self.tileWidth/8),
                                self.tileWidth-(self.tileWidth/8),
                                (self.tileWidth*self.width)+self.tileWidth+(self.tileWidth/8),
                                (self.tileWidth*self.height)+self.tileWidth+(self.tileWidth/8), fill=cWood)

        for y in range(self.height):
            self.gardenMap.append([])
            for x in range(self.width):
                newPlot = Plot(x, y, self.root, self.tileWidth)
                newPlot.draw(self.c)
                self.gardenMap[y].append(newPlot)

    def getDimensions(self):
        self.width = int(self.widthEntryBox.get())
        self.height = int(self.heightEntryBox.get())





A = Main()
A.root.mainloop()