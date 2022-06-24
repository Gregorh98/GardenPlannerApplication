"""
Notification Service

This will run in the background and provide updates via email in relation to your plants.

- Weekly summary of how plants are growing
- Watering reminders (after period of increased dryness)
- Fertiliser reminders
- Harvest alert (for ready crops)
- Planting alert (for planned crops)
"""
import datetime
import json
from os.path import exists

from _plant import Plant
from _resources import saveExportPath


class NotificationService:
    def __init__(self):
        if not exists("garden.json"):
            print("No save file located. Please save a garden before running the notification service")
        else:
            self.plants = self.getAllPlants()
            print(self.plants)
            print(self.writeWeeklySummary()["message"])

    # region Email Functions
    def initiateEmailService(self):
        return

    def sendEmail(self, message):
        return
    # endregion

    # region Email Writers
    def writeWeeklySummary(self):
        subject = "Square Foot Garden - Weekly Summary"
        message = "Weekly summary for week beginning 01/01/2022\n"
        for plant in self.getAllPlants():
            if plant.state == plant.growthStates["planned"]:
                message += f"\n(ID: {plant.id}) {plant.name} - {plant.daysTillPlanting} days till planting"
        message += "\n"
        for plant in self.getAllPlants():
            if plant.state == plant.growthStates["growing"]:
                message += f"\n(ID: {plant.id}) {plant.name} - {plant.daysTillHarvest} days till harvest ({plant.percentGrown}% grown)"
        message += "\n"
        for plant in self.getAllPlants():
            if plant.state == plant.growthStates["ready"]:
                message += f"\n(ID: {plant.id}) {plant.name} - ready to harvest!"


        return {"subject":subject, "message":message}


    # endregion

    def getAllPlants(self):
        plants = []
        with open(saveExportPath, "r") as f:
            jsonDump = json.loads(f.read())
            for key in jsonDump:
                if key != "general":   #Only select plots, not general information
                    plant = Plant(jsonDump[key]["plant"]["name"], jsonDump[key]["plant"]["id"], datetime.date.fromisoformat(jsonDump[key]["plant"]["plantingDate"]), 0)

                    plants.append(plant)

        return plants



NotificationService()