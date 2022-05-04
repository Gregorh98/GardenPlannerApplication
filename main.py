import _tkinter
import datetime
import json
import math
import tkinter.messagebox
from tkinter import *
from PIL import ImageGrab
from tkcalendar import DateEntry

#Resources
cWood       = "#bca464"
cGrass      = "#2c3c1e"
cLightMud   = "#52402a"
cMidMud     = "#482f1f"
cDarkMud    = "#2e2018"

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
        ImageGrab.grab().crop((x, y, x1, y1)).save("garden.png")

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
                    save[plot.id]["plant"] = {
                        "name":         plot.plant.name,
                        "id":           plot.plant.id,
                        "plantingDate": plot.plant.plantingDate
                    }
                else:
                    save[plot.id]["plant"] = None

        jsonDump = json.dumps(save, default=str)
        with open("garden.json", "w") as f:
            f.write(jsonDump)

    def loadGarden(self):
        with open("garden.json", "r") as f:
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

class Plant():
    def __init__(self, name, id, plantingDate):
        self.growthStates    = {"planned":  "Planned",
                                "growing":  "Growing",
                                "ready":    "Ready"}
        self.name           = name
        self.id             = id
        self.plantingDate   = plantingDate
        self.state          = self.growthStates["planned"]

        jsonInfo = self.getInfo()
        self.quantity = jsonInfo["numberPerSquareFoot"]
        self.growTime = jsonInfo["growTime"]
        self.displayName = jsonInfo["name"]

        self.update()


    def getInfo(self):
        with open("plants.json", "r") as f:
            allPlants = json.loads(f.read())
            myPlant = allPlants[self.name.lower()]
            return myPlant


    def update(self):
        self.harvestDate = self.plantingDate + datetime.timedelta(days=self.growTime)
        self.daysTillHarvest = (self.harvestDate - datetime.date.today()).days
        self.daysSincePlanted = (datetime.date.today() - self.plantingDate).days

        #max percent grown is 100
        percentGrown = math.ceil((self.daysSincePlanted / self.growTime) * 100)
        self.percentGrown = percentGrown if percentGrown <= 100 else 100

        if datetime.date.today() >= self.plantingDate and datetime.date.today() < self.harvestDate:
            self.state = self.growthStates["growing"]

        if datetime.date.today() >= self.harvestDate:
            self.state = self.growthStates["ready"]

class Plot():
    def __init__(self, x, y, root, tileWidth):
        self.x = x
        self.y = y
        self.xOnGrid = tileWidth+(x*tileWidth)
        self.yOnGrid = tileWidth + (y * tileWidth)

        self.tileWidth = tileWidth

        self.xCenterCell = self.xOnGrid + (self.tileWidth/2)
        self.yCenterCell = self.yOnGrid + (self.tileWidth / 2)

        self.id = str([x, y])

        self.rootWindow = root
        self.plotText   = None

        self.plant       = None

    def draw(self, canvas):
        self.canvas = canvas
        self.canvasElement = canvas.create_rectangle(self.tileWidth + self.x * self.tileWidth, self.tileWidth + self.y * self.tileWidth,
                                                     self.tileWidth + self.x * self.tileWidth + self.tileWidth,
                                                     self.tileWidth + self.y * self.tileWidth + self.tileWidth, fill=cLightMud,
                                                     outline=cMidMud)
        self.canvas.tag_bind(self.canvasElement, "<Button-1>", self.eventAddEditCrop)
        self.canvas.tag_bind(self.canvasElement, "<Button-3>", self.eventRemoveCrop)


    def eventAddEditCrop(self, args):
        self.displayWindow()

    def eventRemoveCrop(self, args):
        self.plant = None

        self.canvas.delete(self.plotText)
        self.plotText = None

        self.canvas.itemconfig(self.canvasElement, fill=cLightMud, outline=cMidMud)



    def getAvailableCrops(self):
        with open("plants.json", "r") as f:
            cropsList = json.loads(f.read())
            availableCrops = []
            for key in cropsList.keys():
                availableCrops.append(key.title())

        return availableCrops

    def displayWindow(self):
        self.plotWindow = Toplevel(self.rootWindow)
        self.plotWindow.title("Edit Plot")

        availableCrops = self.getAvailableCrops()

        selected = StringVar(self.plotWindow)
        selected.set(availableCrops[0])

        # Listbox Section
        listFrame = Frame(self.plotWindow)

        cropListbox = Listbox(listFrame, height=6)
        for x in availableCrops:
            cropListbox.insert(END, x)
        cropListbox.pack(side=LEFT, fill="y")
        if self.plant is not None:
            cropListbox.select_set(self.plant.id)

        scrollbar = Scrollbar(listFrame, orient="vertical")
        scrollbar.config(command=cropListbox.yview)
        scrollbar.pack(side="right", fill="y")

        cropListbox.config(yscrollcommand=scrollbar.set)

        listFrame.pack()

        # Plant Settings Section
        plantSettingFrame = Frame(self.plotWindow)

        Label(plantSettingFrame, text="Planting Date").grid(column=0, row=0)
        plantingDateSelector = DateEntry(plantSettingFrame, width=12, borderwidth=2)
        if self.plant is not None:
            plantingDateSelector.set_date(self.plant.plantingDate)

        plantingDateSelector.grid(column=1, row=0)

        plantSettingFrame.pack(expand=True)

        selectCropButton = Button(self.plotWindow, text="Add Crop To Plot", command=lambda: self.cropSelected(cropListbox, plantingDateSelector.get_date()))
        selectCropButton.pack()

    def cropSelected(self, cropListbox, plantingDate):
        try:
            self.plant = Plant(cropListbox.get(cropListbox.curselection()), cropListbox.curselection()[0], plantingDate)
        except _tkinter.TclError:
            tkinter.messagebox.showerror("Error", "Please select a crop to plant")
            return

        # Add Crop Name to Plot, or update existing
        newPlotText =f"{self.plant.quantity}x\n{self.plant.displayName}\n({self.plant.state})"
        if self.plotText is not None:
            self.canvas.itemconfigure(self.plotText, text=newPlotText)
        else:
            self.plotText = self.canvas.create_text(self.xCenterCell, self.yCenterCell, fill="white", text=newPlotText, justify=CENTER)

        self.plotWindow.destroy()
        self.canvas.itemconfig(self.canvasElement, fill=cMidMud, outline=cDarkMud)

    def updateOnLoad(self):
        self.canvas.itemconfig(self.canvasElement, fill=cMidMud, outline=cDarkMud)

        newPlotText = f"{self.plant.quantity}x\n{self.plant.displayName}\n({self.plant.state})"
        self.plotText = self.canvas.create_text(self.xCenterCell, self.yCenterCell, fill="white", text=newPlotText, justify=CENTER)

A = Main()
A.root.mainloop()