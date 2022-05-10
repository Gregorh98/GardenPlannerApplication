import _tkinter
import json
from tkcalendar import DateEntry
from _resources import *
from _plant import Plant
from tkinter import *
import tkinter.messagebox


def getAvailableCrops():
    with open("plants.json", "r") as f:
        cropsList = json.loads(f.read())
        availableCrops = []
        for key in cropsList.keys():
            availableCrops.append(key.title())

    return availableCrops


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
        self.showEditPlotWindow()

    def eventRemoveCrop(self, args):
        self.plant = None

        self.canvas.delete(self.plotText)
        self.plotText = None

        self.canvas.itemconfig(self.canvasElement, fill=cLightMud, outline=cMidMud)

    def getNewPlotText(self):
        if self.plant.state == self.plant.growthStates["planned"] or self.plant.state == self.plant.growthStates["ready"]:
            return f"{self.plant.quantity}x\n{self.plant.displayName}\n({self.plant.state})"
        else:
            return f"{self.plant.quantity}x\n{self.plant.displayName}\n({self.plant.percentGrown}%)"

    def showEditPlotWindow(self):
        self.plotWindow = Toplevel(self.rootWindow)
        self.plotWindow.title("Edit Plot")

        availableCrops = getAvailableCrops()

        selected = StringVar(self.plotWindow)
        selected.set(availableCrops[0])

        # Listbox Section
        listFrame = LabelFrame(self.plotWindow, text="Select Plant")

        cropListbox = Listbox(listFrame, height=6)
        for x in availableCrops:
            cropListbox.insert(END, x)
        cropListbox.pack(side=LEFT, fill="y", padx=2, pady=(0,5))
        if self.plant is not None:
            cropListbox.select_set(self.plant.id)
        else:
            cropListbox.select_set(0)

        scrollbar = Scrollbar(listFrame, orient="vertical")
        scrollbar.config(command=cropListbox.yview)
        scrollbar.pack(side="right", fill="y", pady=(0,5))

        cropListbox.config(yscrollcommand=scrollbar.set)

        listFrame.pack(pady=5, padx=5, expand=TRUE, side=LEFT, fill="both")

        # Plant Settings Section
        plantSettingFrame = LabelFrame(self.plotWindow, text="Configure Plant")

        # Planting Date
        Label(plantSettingFrame, text="Planting Date").grid(column=0, row=0)
        plantingDateSelector = DateEntry(plantSettingFrame, width=12, borderwidth=2)
        if self.plant is not None:
            plantingDateSelector.set_date(self.plant.plantingDate)

        plantingDateSelector.grid(column=1, row=0, padx=2, pady=(2, 0))

        plantSettingFrame.pack(pady=(5,0), padx=(0,5), expand=TRUE, fill="both")

        selectCropButton = Button(self.plotWindow, text="Add Crop To Plot", command=lambda: self.cropSelected(cropListbox, plantingDateSelector.get_date()))
        selectCropButton.pack(pady=5, padx=(0,5), expand=TRUE, side=LEFT, fill="both")

    def cropSelected(self, cropListbox, plantingDate):
        try:
            self.plant = Plant(cropListbox.get(cropListbox.curselection()), cropListbox.curselection()[0], plantingDate)
        except _tkinter.TclError:
            tkinter.messagebox.showerror("Error", "Please select a crop to plant")
            return

        self.update()
        self.plotWindow.destroy()

    def update(self):
        # If we have a plant and its ready, light soil. Else dark soil
        if self.plant is not None and self.plant.state == self.plant.growthStates["ready"]:
            self.canvas.itemconfig(self.canvasElement, fill=cLightMud, outline=cMidMud)
        else:
            self.canvas.itemconfig(self.canvasElement, fill=cMidMud, outline=cDarkMud)

        if self.plotText is not None:
            self.canvas.itemconfigure(self.plotText, text=self.getNewPlotText())
        else:
            self.plotText = self.canvas.create_text(self.xCenterCell, self.yCenterCell, fill="white",
                                                    text=self.getNewPlotText(), justify=CENTER)
