import datetime
import json
import tkinter.messagebox
from tkinter import ttk
from tkinter import *
from PIL import ImageGrab
from os.path import exists
from _plot import Plot
from _plant import Plant
from _resources import *


class Main:
    def __init__(self):
        self.root = Tk()
        self.root.title(title)
        self.height = 2
        self.width = 3
        self.tileWidth = 64  # The dimensions of the representation of one square foot of land
        self.configurationWindow    = None
        self.scheduleWindow         = None

        self.gardenMap = []
        self.initialiseMainWindow()

        loadGardenOnLaunch = True
        if exists("garden.json") and loadGardenOnLaunch:
            self.gardenMap = []
            self.loadGarden()
            return

    # region Windows
    def initialiseMainWindow(self):
        self.c = Canvas(self.root, background=cGrass, height=((2 * self.tileWidth) + self.height * self.tileWidth),
                        width=((2 * self.tileWidth) + self.width * self.tileWidth))
        self.c.grid(row=0, column=0)

        sideFrame = Frame(self.root)

        row = 0

        Label(sideFrame, text=titleVersionNumber, wraplength=100).grid(row=row, column=0, padx=2, pady=1, sticky=EW)

        row += 1

        Label(sideFrame, text=str(datetime.date.today()), relief=SUNKEN).grid(row=row, column=0, padx=2, pady=1, sticky=EW)

        row += 1

        ttk.Separator(sideFrame, orient=HORIZONTAL).grid(row=row, column=0, padx=2, pady=4, sticky=EW)

        row += 1

        configButton = Button(sideFrame, text="Configure", command=self.showConfigureWindow)
        configButton.grid(row=row, column=0, padx=2, pady=1, sticky=EW)

        row += 1

        scheduleButton = Button(sideFrame, text="View Schedule", command=self.showScheduleWindow)
        scheduleButton.grid(row=row, column=0, padx=2, pady=1, sticky=EW)

        row += 1

        saveButton = Button(sideFrame, text="Save Garden", command=self.saveGarden)
        saveButton.grid(row=row, column=0, padx=2, pady=1, sticky=EW)

        row += 1

        loadButton = Button(sideFrame, text="Load Garden", command=self.loadGarden)
        loadButton.grid(row=row, column=0, padx=2, pady=1, sticky=EW)

        row += 1

        saveImageButton = Button(sideFrame, text="Save Image", command=self.saveImage)
        saveImageButton.grid(row=row, column=0, padx=2, pady=1, sticky=EW)

        sideFrame.grid(row=0, column=1, sticky=N)

        self.updateGarden(self.height, self.width)

    def showConfigureWindow(self):
        if self.configurationWindow is not None:
            return

        self.configurationWindow = Toplevel(self.root)
        self.configurationWindow.protocol("WM_DELETE_WINDOW", self.configClosed)

        Label(self.configurationWindow, text="Width").grid(row=0, column=0, sticky=W)
        self.widthEntryBox = Entry(self.configurationWindow)
        self.widthEntryBox.insert(0, str(self.width))
        self.widthEntryBox.grid(row=0, column=1)

        self.widthEntryBox.focus_set()

        Label(self.configurationWindow, text="Height").grid(row=1, column=0, sticky=W)
        self.heightEntryBox = Entry(self.configurationWindow)
        self.heightEntryBox.insert(0, str(self.height))
        self.heightEntryBox.grid(row=1, column=1)

        Button(self.configurationWindow, text="Map My Garden", command=lambda: self.updateGarden(int(self.heightEntryBox.get()), int(self.widthEntryBox.get()))).grid(row=2, column=0, columnspan=2)

    def showScheduleWindow(self):
        if self.scheduleWindow is not None:
            return

        allPlantedPlots = self.getAllPlantedPlots()
        # If no planted plots, don't show schedule
        if allPlantedPlots is None:
            tkinter.messagebox.showinfo("No Planted Plots", "There are no planted plots to display!")
            return

        allPlantedPlots.sort(key=lambda plantedPlot: plantedPlot.plant.daysTillHarvest)

        self.scheduleWindow = Toplevel(self.root)
        self.scheduleWindow.protocol("WM_DELETE_WINDOW", self.scheduleClosed)
        self.scheduleWindow.title("Schedule")

        scheduleTableFrame = Frame(self.scheduleWindow)
        scheduleTableFrame.pack()

        self.scheduleTable = ttk.Treeview(scheduleTableFrame)

        self.scheduleTable['columns'] = ('coords', 'cropName', 'plantDate', 'harvestDate', 'daysSincePlanted', 'daysTillGrown', 'percentGrown')

        self.scheduleTable.column("#0", width=0, stretch=NO)
        self.scheduleTable.column("coords", anchor=CENTER, width=80)
        self.scheduleTable.column("cropName", anchor=CENTER, width=80)
        self.scheduleTable.column("plantDate", anchor=CENTER, width=80)
        self.scheduleTable.column("harvestDate", anchor=CENTER, width=80)
        self.scheduleTable.column("daysSincePlanted", anchor=CENTER, width=80)
        self.scheduleTable.column("daysTillGrown", anchor=CENTER, width=80)
        self.scheduleTable.column("percentGrown", anchor=CENTER, width=100)

        self.scheduleTable.heading("#0", text="", anchor=CENTER)
        self.scheduleTable.heading("coords", text="Co-ords", anchor=CENTER)
        self.scheduleTable.heading("cropName", text="Crop", anchor=CENTER)
        self.scheduleTable.heading("plantDate", text="Planted Date", anchor=CENTER)
        self.scheduleTable.heading("harvestDate", text="Harvest Date", anchor=CENTER)
        self.scheduleTable.heading("daysSincePlanted", text="Since Planted", anchor=CENTER)
        self.scheduleTable.heading("daysTillGrown", text="Till Harvest", anchor=CENTER)
        self.scheduleTable.heading("percentGrown", text="Percent Grown", anchor=CENTER)

        for plot in allPlantedPlots:
            self.scheduleTable.insert(parent='', index='end', text='', values=(
                plot.id,                                # Co-ordinates of the plot [x, y]
                plot.plant.name,                        # Name
                plot.plant.plantingDate,                # Date planted on
                plot.plant.harvestDate,                 # Date to harvest on
                f"{plot.plant.daysSincePlanted} days",  # number of days since planted
                f"{plot.plant.daysTillHarvest} days",   # number of days till harvest
                f"{plot.plant.percentGrown}%"           # percent grown
            ))

        self.scheduleTable.bind('<<TreeviewSelect>>', self.eventScheduleSelectedItem)
        self.scheduleTable.pack()
    # endregion

    # region Save and Load
    def saveImage(self):
        x = self.root.winfo_rootx() + self.c.winfo_x()
        y = self.root.winfo_rooty() + self.c.winfo_y()
        x1 = x + self.c.winfo_width()
        y1 = y + self.c.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(imageExportPath)
        tkinter.messagebox.showinfo("Image Saved", f"Garden image saved successfully. Image located at '{imageExportPath}'")

    def saveGarden(self):
        overwriteWarning = True
        if exists(saveExportPath):
            overwriteWarning = tkinter.messagebox.askyesno("Overwrite Warning",
                                                           "There is an existing save. Are you sure you want to overwrite?")

        if overwriteWarning:
            save = {"general": {
                "tileWidth": self.tileWidth,
                "gardenWidth": self.width,
                "gardenHeight": self.height
            }}
            # General settings

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
                tkinter.messagebox.showinfo("Garden Saved", f"Garden saved successfully. Save file located at '{saveExportPath}'")
        else:
            tkinter.messagebox.showinfo("Save cancelled", "Save cancelled!")

    def loadGarden(self):
        try:
            with open(saveExportPath, "r") as f:
                jsonDump = json.loads(f.read())
        except FileNotFoundError:
            tkinter.messagebox.showerror("Error", "No Save Found")
            return
        # Update height and width
        height = jsonDump["general"]["gardenHeight"]
        width = jsonDump["general"]["gardenWidth"]
        if self.updateGarden(height, width) is not False:
            for row in self.gardenMap:
                for plot in row:
                    # Update plant in plot
                    plotPlant = jsonDump[f"[{plot.x}, {plot.y}]"]["plant"]
                    if plotPlant is not None:
                        self.gardenMap[plot.y][plot.x].plant = Plant(plotPlant["name"], plotPlant["id"], datetime.date.fromisoformat(plotPlant["plantingDate"]))
                        self.gardenMap[plot.y][plot.x].update()
    # endregion

    # region Functions
    def eventScheduleSelectedItem(self, args):
        for selectedItem in self.scheduleTable.selection():
            item = self.scheduleTable.item(selectedItem)

            for plot in self.getAllPlantedPlots():
                plot.update()
                if plot.id == item["values"][0]:
                    plot.canvas.itemconfig(plot.canvasElement, fill=cSelected, outline=cDarkMud)

    def scheduleClosed(self):
        for plot in self.getAllPlantedPlots():
            plot.update()
        self.scheduleWindow.destroy()
        self.scheduleWindow = None

    def configClosed(self):
        self.configurationWindow.destroy()
        self.configurationWindow = None

    def generateGardenMap(self):
        for y in range(self.height):
            self.gardenMap.append([])
            for x in range(self.width):
                newPlot = Plot(x, y, self.root, self.tileWidth)
                newPlot.draw(self.c)
                self.gardenMap[y].append(newPlot)

    def getAllPlantedPlots(self):
        allPlantedPlots = []
        for row in self.gardenMap:
            for plot in row:
                if plot.plant is not None:
                    allPlantedPlots.append(plot)
        return allPlantedPlots if allPlantedPlots != [] else None

    def updateGarden(self, height, width):
        if self.configurationWindow is not None:
            self.configClosed()

        if self.gardenMap != []:
            overwriteConfirm = tkinter.messagebox.askyesno(title="Overwrite Warning",
                                                           message="This will overwrite the current plot. Do you wish to continue?")
            if overwriteConfirm is False:
                if self.configurationWindow is not None:
                    self.configurationWindow.destroy()
                tkinter.messagebox.showinfo(title="Overwrite Aborted", message="Configuration update cancelled")
                return False

        self.height = height
        self.width = width

        self.gardenMap = []

        self.c.delete("all")

        self.c.create_rectangle(self.tileWidth - (self.tileWidth / 8), self.tileWidth - (self.tileWidth / 8),
                                (self.tileWidth * self.width) + self.tileWidth + (self.tileWidth / 8),
                                (self.tileWidth * self.height) + self.tileWidth + (self.tileWidth / 8), fill=cWood)

        self.generateGardenMap()

        self.c.configure(height=((2 * self.tileWidth) + self.height * self.tileWidth),
                         width=((2 * self.tileWidth) + self.width * self.tileWidth))
        if self.configurationWindow is not None:
            self.configurationWindow.destroy()
        return True
    # endregion


A = Main()
A.root.mainloop()
