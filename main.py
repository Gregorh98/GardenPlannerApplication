import datetime
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
        self.canvasWidth = lambda:  (2 * tileWidth) + (tileWidth * self.width)
        self.canvasHeight = lambda: (2 * tileWidth) + (tileWidth * self.height)

        self.highlightSquare        = None
        self.configurationWindow    = None
        self.editPlantListWindow    = None
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
        self.c = Canvas(self.root, height=((2 * tileWidth) + self.height * tileWidth),
                        width=((2 * tileWidth) + self.width * tileWidth))

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

        #Dimensions
        dimensionsFrame = LabelFrame(self.configurationWindow, text="Garden Dimensions")

        Label(dimensionsFrame, text="Width").grid(row=0, column=0, sticky=W)
        self.widthEntryBox = Entry(dimensionsFrame, width=10)
        self.widthEntryBox.insert(0, str(self.width))
        self.widthEntryBox.grid(row=0, column=1, padx=2)

        self.widthEntryBox.focus_set()

        Label(dimensionsFrame, text="Height").grid(row=1, column=0, sticky=W)
        self.heightEntryBox = Entry(dimensionsFrame, width=10)
        self.heightEntryBox.insert(0, str(self.height))
        self.heightEntryBox.grid(row=1, column=1, padx=2)

        Button(dimensionsFrame, text="Apply", command=lambda: self.updateGarden(int(self.heightEntryBox.get()), int(self.widthEntryBox.get()))).grid(row=2, column=0, columnspan=2, pady=2, padx=2, sticky=EW)

        dimensionsFrame.grid(column=0, row=0, padx=2, pady=2)

        #Editing Plant List
        optionsFrame = LabelFrame(self.configurationWindow, text="Data")

        editPlantListButton = Button(optionsFrame, text="Edit Plant List", command=self.showEditPlantListWindow)
        editPlantListButton.grid(row=0, column=1, padx=2, pady=1, sticky=EW)

        optionsFrame.grid(row=0, column=2, padx=2, pady=2, sticky=NS)

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

        for id, plot in enumerate(allPlantedPlots):
            self.scheduleTable.insert(parent='', index='end', text='', iid=id, values=(
                plot.id,                                # Co-ordinates of the plot [x, y]
                plot.plant.displayName,                 # Name
                plot.plant.plantingDate,                # Date planted on
                plot.plant.harvestDate,                 # Date to harvest on
                f"{plot.plant.daysSincePlanted} days",  # number of days since planted
                f"{plot.plant.daysTillHarvest} days",   # number of days till harvest
                f"{plot.plant.percentGrown}%"           # percent grown
            ))

        self.scheduleTable.bind('<<TreeviewSelect>>', self.eventScheduleSelectedItem)
        self.scheduleTable.selection_set(0)
        self.scheduleTable.pack()

    def showEditPlantListWindow(self):
        self.configClosed()

        def refresh(args, regenBlankEntries=False):
            if not regenBlankEntries:
                try:
                    current = getAvailableCropDetail(cropListbox.get(cropListbox.curselection()))
                    id.set(str(cropListbox.get(cropListbox.curselection())))
                    name.set(str(current["name"]))
                    variety.set(str(current["variety"]))
                    noPerSquareFoot.set(str(current["numberPerSquareFoot"]))
                    growTime.set(str(current["growTime"]))
                except TclError:
                    return

            else:
                id.set("")
                name.set("")
                variety.set("")
                noPerSquareFoot.set("")
                growTime.set("")

        def regenListbox():
            availableCrops = getAvailableCrops()
            cropListbox.delete(0, END)
            for x in availableCrops:
                cropListbox.insert(END, x)

        if self.editPlantListWindow is not None:
            return

        self.editPlantListWindow = Toplevel(self.root)
        self.editPlantListWindow.protocol("WM_DELETE_WINDOW", self.editPlantListClosed)

        id = StringVar(self.editPlantListWindow)
        noPerSquareFoot = StringVar(self.editPlantListWindow)
        variety = StringVar(self.editPlantListWindow)
        name = StringVar(self.editPlantListWindow)
        growTime = StringVar(self.editPlantListWindow)

        availableCrops = getAvailableCrops()

        # Listbox Section
        listFrame = LabelFrame(self.editPlantListWindow, text="Select Plant")

        cropListbox = Listbox(listFrame, height=6)
        cropListbox.bind("<<ListboxSelect>>", refresh)

        for x in availableCrops:
            cropListbox.insert(END, x)
        cropListbox.pack(side=LEFT, fill="y", padx=2, pady=(0, 5))

        scrollbar = Scrollbar(listFrame, orient="vertical")
        scrollbar.config(command=cropListbox.yview)
        scrollbar.pack(side="right", fill="y", pady=(0, 5))

        cropListbox.config(yscrollcommand=scrollbar.set)

        listFrame.pack(pady=5, padx=5, expand=TRUE, side=LEFT, fill="both")

        # Plant Configuration Section
        plantConfigFrame = LabelFrame(self.editPlantListWindow, text="Plant Information")

        row=0
        # Id
        Label(plantConfigFrame, text="ID Name").grid(column=0, row=row, sticky=W, padx=2)
        plantIdEntry = Entry(plantConfigFrame, textvariable=id, state=DISABLED)
        plantIdEntry.grid(column=1, row=row, sticky=W, padx=2)
        row += 1
        # Name
        Label(plantConfigFrame, text="Display Name").grid(column=0, row=row, sticky=W, padx=2)
        Entry(plantConfigFrame, textvariable=name).grid(column=1, row=row, sticky=W, padx=2)
        row += 1
        # Number Per Square Foot
        Label(plantConfigFrame, text="Number Per Square Foot").grid(column=0, row=row, sticky=W, padx=2)
        Entry(plantConfigFrame, textvariable=noPerSquareFoot).grid(column=1, row=row, sticky=W, padx=2)
        row += 1
        # Variety
        Label(plantConfigFrame, text="Variety").grid(column=0, row=row, sticky=W, padx=2)
        Entry(plantConfigFrame, textvariable=variety).grid(column=1, row=row, sticky=W, padx=2)
        row += 1
        # Grow Time
        Label(plantConfigFrame, text="Grow Time").grid(column=0, row=row, sticky=W, padx=2)
        Entry(plantConfigFrame, textvariable=growTime).grid(column=1, row=row, sticky=W, padx=2)
        row += 1

        buttonFrame = Frame(plantConfigFrame)

        def getEntryData():
            if str(id.get()) != "":
                return {"id": str(id.get().lower()), "name": str(name.get()), "variety": str(variety.get()), "numberPerSquareFoot": float(noPerSquareFoot.get()), "growTime": int(growTime.get())}
            else:
                return None

        def add():
            self.addPlantToPlantsFile(getEntryData())
            regenListbox()
            refresh(None, True)

        def edit():
            self.editPlantInPlantsFile(getEntryData())
            regenListbox()
            refresh(None, True)

        def remove():
            self.removePlantInPlantsFile(getEntryData())
            regenListbox()
            refresh(None, True)

        Button(buttonFrame, text="Add", command=add, state=DISABLED).grid(column=0, row=0, sticky=W, padx=2)
        Button(buttonFrame, text="Apply Edit", command=edit).grid(column=1, row=0, sticky=W, padx=2)
        Button(buttonFrame, text="Remove", command=remove).grid(column=2, row=0, sticky=W, padx=2)

        buttonFrame.grid(row=row, column=0, columnspan=2, pady=2)

        plantConfigFrame.pack(pady=(5, 0), padx=(0, 5), expand=TRUE, fill="both")

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
                "tileWidth": tileWidth,
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
                    if self.highlightSquare is not None:
                        self.c.delete(self.highlightSquare)
                    outlineWidth = 4
                    self.highlightSquare = self.c.create_rectangle(
                        (tileWidth + (plot.x * tileWidth))+(outlineWidth/2),
                        (tileWidth + (plot.y * tileWidth))+(outlineWidth/2),
                        (tileWidth + (plot.x * tileWidth) + tileWidth)-(outlineWidth/2),
                        (tileWidth + (plot.y * tileWidth) + tileWidth)-(outlineWidth/2),
                        fill="",
                        outline=cSelected,
                        width=outlineWidth
                    )

    # region Closed Event Functions
    def scheduleClosed(self):
        for plot in self.getAllPlantedPlots():
            plot.update()
        self.c.delete(self.highlightSquare)
        self.scheduleWindow.destroy()
        self.scheduleWindow = None

    def configClosed(self):
        self.configurationWindow.destroy()
        self.configurationWindow = None

    def editPlantListClosed(self):
        self.editPlantListWindow.destroy()
        self.editPlantListWindow = None
    # endregion

    def generateGardenMap(self):
        for y in range(self.height):
            self.gardenMap.append([])
            for x in range(self.width):
                newPlot = Plot(x, y, self.root)
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

        if graphicalUI:
            self.root.grass = PhotoImage(file='sprites/grass.png')
            for y in range(0, self.canvasHeight(), 64):
                for x in range(0, self.canvasWidth(), 64):
                    self.c.create_image(x, y, image=self.root.grass, anchor=NW)
        else:
            self.c.configure(background=cGrass)

        self.c.create_rectangle(tileWidth - (tileWidth / 8), tileWidth - (tileWidth / 8),
                                (tileWidth * self.width) + tileWidth + (tileWidth / 8),
                                (tileWidth * self.height) + tileWidth + (tileWidth / 8), fill=cWood)

        self.generateGardenMap()

        self.c.configure(height=((2 * tileWidth) + self.height * tileWidth),
                         width=((2 * tileWidth) + self.width * tileWidth))

        if self.configurationWindow is not None:
            self.configurationWindow.destroy()

        return True

    def gameLoop(self):
        while True:
            self.root.update()
            self.root.update_idletasks()

    # region Change Plants File Functions
    def addPlantToPlantsFile(self, plantToAdd):
        with open(plantsJsonFile, "r") as f:
            jsonDump = json.loads(f.read())

        if plantToAdd is not None:
            if plantToAdd["id"] not in jsonDump:
                jsonDump[plantToAdd["id"]] = {"name": plantToAdd["name"], "variety": plantToAdd["variety"], "numberPerSquareFoot": plantToAdd["numberPerSquareFoot"], "growTime": plantToAdd["growTime"]}

                jsonDump = json.dumps(jsonDump, default=str)

                with open(plantsJsonFile, "w") as f:
                    f.write(jsonDump)
            else:
                tkinter.messagebox.showerror("Error", "Plant already exists! Please change the ID name")
        else:
            tkinter.messagebox.showerror("Error", "Please select a plant before attempting to add")

    def removePlantInPlantsFile(self, plantToRemove):
        with open(plantsJsonFile, "r") as f:
            jsonDump = json.loads(f.read())

        if plantToRemove["id"] in jsonDump:
            jsonDump.pop(plantToRemove["id"])

            jsonDump = json.dumps(jsonDump, default=str)

            with open(plantsJsonFile, "w") as f:
                f.write(str(jsonDump))
        else:
            tkinter.messagebox.showerror("Error", "Plant does not exist! Select another plant")

    def editPlantInPlantsFile(self, plantToEdit):
        with open(plantsJsonFile, "r") as f:
            jsonDump = json.loads(f.read())

        if plantToEdit["id"] in jsonDump:
            jsonDump[plantToEdit["id"]] = {"name": plantToEdit["name"], "variety": plantToEdit["variety"], "numberPerSquareFoot": plantToEdit["numberPerSquareFoot"], "growTime": plantToEdit["growTime"]}

            jsonDump = json.dumps(jsonDump, default=str)

            with open(plantsJsonFile, "w") as f:
                f.write(str(jsonDump))
        else:
            tkinter.messagebox.showerror("Error", "Plant does not exist! Select another plant")
    # endregion

    # endregion


A = Main()
A.gameLoop()

