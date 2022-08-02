import math
import datetime
import json
from _resources import tileWidth

class Plant:
    def __init__(self, name, _id, plantingDate):
        self.growthStates    = {"planned":  "Planned",
                                "growing":  "Growing",
                                "ready":    "Ready"}
        self.name           = name
        self.id             = _id
        self.plantingDate   = plantingDate
        self.state          = self.growthStates["planned"]

        jsonInfo = self.getAdditionalInfo()
        self.quantity = jsonInfo["numberPerSquareFoot"]
        self.growTime = jsonInfo["growTime"]
        self.formattedDisplayName = jsonInfo["name"] if ("\n" in jsonInfo["name"] or len(jsonInfo["name"]) <= (tileWidth / 8)) else jsonInfo["name"][0:7] + "..."
        self.displayName = jsonInfo["name"]

        self.update()

    def getAdditionalInfo(self):
        with open("plants.json", "r") as f:
            allPlants = json.loads(f.read())
            myPlant = allPlants[self.name.lower()]
            return myPlant

    def update(self):
        self.harvestDate = self.plantingDate + datetime.timedelta(days=self.growTime)
        # noinspection PyTypeChecker
        self.daysTillHarvest = (self.harvestDate - datetime.date.today()).days
        self.daysSincePlanted = (datetime.date.today() - self.plantingDate).days

        # max percent grown is 100
        percentGrown = math.ceil((self.daysSincePlanted / self.growTime) * 100)
        self.percentGrown = percentGrown if percentGrown <= 100 else 100
        self.percentGrown = percentGrown if percentGrown >= 0 else 0

        if self.plantingDate <= datetime.date.today() < self.harvestDate:
            self.state = self.growthStates["growing"]

        if datetime.date.today() >= self.harvestDate:
            self.state = self.growthStates["ready"]
