# Variables
import os

versionNumber   = "1.2.0"
tileWidth       = 64            #Scale of view - min 64

# Resources
cWood       = "#bca464"
cGrass      = "#2c3c1e"
cLightMud   = "#52402a"
cMidMud     = "#482f1f"
cDarkMud    = "#2e2018"
cSelected   = "#3C3A7A"

# Paths
saveExportPath      = (os.getcwd()+"\\garden.json")
imageExportPath     = (os.getcwd()+"\\garden.png")
plantsJsonFile      = (os.getcwd()+"\\plants.json")

# Labels
title               = f"Square Foot Garden Planner"
titleVersionNumber  = f"{title} v{versionNumber}"

# Settings
graphicalUI = False

# Global static methods
import json

def getAvailableCrops():
    with open("plants.json", "r") as f:
        cropsList = json.loads(f.read())
        availableCrops = []
        for key in cropsList.keys():
            availableCrops.append(key.title())

    return availableCrops


def getAvailableCropDetail(crop):
    with open("plants.json", "r") as f:
        cropsList = json.loads(f.read())

    return cropsList[crop.lower()]

