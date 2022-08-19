import unittest
from _plant import Plant
import datetime


class TestPlant(unittest.TestCase):
    def test_setupNewPlant_nameAppliesCorrectly(self):
        # Arrange
        plantName = "TestPlant"
        plantId = 0
        plantDate = datetime.date.fromisoformat("1998-12-02")

        # Act
        plant = Plant(plantName, plantId, plantDate)

        # Assert
        self.assertEqual(plant.name, plantName)
        self.assertEqual(plant.id, plantId)
        self.assertEqual(plant.plantingDate, plantDate)

    def test_plantInitialisation_plantInitialisesWithBasicAdditionalInfo(self):
        # Arrange
        plantName = "TestPlant"
        plantId = 0
        plantDate = datetime.date.fromisoformat("1998-12-02")

        expectedQuantity = 1
        expectedGrowTime = 100
        expectedDisplayName = "Test Plant"

        # Act
        plant = Plant(plantName, plantId, plantDate)

        # Assert
        self.assertEqual(plant.quantity, expectedQuantity)
        self.assertEqual(plant.growTime, expectedGrowTime)
        self.assertEqual(plant.displayName, expectedDisplayName)

    def test_plantPercentGrown_plantedInPast_percentGrownCalculatesCorrectly(self):
        #To test the bounds of the percent grown for a plant that is already planted and is growing/grown
        # Arrange
        plantName = "TestPlant"
        plantId = 0

        lowerOutBoundsDate      = datetime.date.today() + datetime.timedelta(days=300)  #before planting day
        lowerBoundsDate         = datetime.date.today() + datetime.timedelta(days=0)    #on planting day

        lowerInBoundsDate       = datetime.date.today() - datetime.timedelta(days=1)    #start of growing period
        midInBoundsDate         = datetime.date.today() - datetime.timedelta(days=50)   #mid way through growing period
        upperInBoundsDate       = datetime.date.today() - datetime.timedelta(days=99)   #end of growing period

        upperBoundsDate         = datetime.date.today() - datetime.timedelta(days=100)  #on harvest day
        upperOutBoundsDate      = datetime.date.today() - datetime.timedelta(days=300)  #after harvest day

        # Act
        lowerOutBoundsPlant = Plant(plantName, plantId, lowerOutBoundsDate)
        lowerBoundsPlant = Plant(plantName, plantId, lowerBoundsDate)

        lowerInBoundsPlant = Plant(plantName, plantId, lowerInBoundsDate)
        midInBoundsPlant = Plant(plantName, plantId, midInBoundsDate)
        upperInBoundsPlant = Plant(plantName, plantId, upperInBoundsDate)

        upperBoundsPlant = Plant(plantName, plantId, upperBoundsDate)
        upperOutBoundsPlant = Plant(plantName, plantId, upperOutBoundsDate)

        # Assert
        #lower out bounds
        self.assertEqual(lowerOutBoundsPlant.percentGrown, 0)
        self.assertEqual(lowerBoundsPlant.percentGrown, 0)

        #in bounds
        self.assertGreater(lowerInBoundsPlant.percentGrown, 0)
        self.assertLess(lowerInBoundsPlant.percentGrown, 100)
        self.assertGreater(midInBoundsPlant.percentGrown, 0)
        self.assertLess(lowerInBoundsPlant.percentGrown, 100)
        self.assertGreater(upperInBoundsPlant.percentGrown, 0)
        self.assertLess(upperInBoundsPlant.percentGrown, 100)

        #upper out bounds
        self.assertEqual(upperOutBoundsPlant.percentGrown, 100)
        self.assertEqual(upperBoundsPlant.percentGrown, 100)

    def test_plantPercentGrown_percentGrownCalculatesCorrectly(self):
        # Arrange
        plantName = "TestPlant"
        plantId = 0
        pastPlantDate       = datetime.date.today() - datetime.timedelta(days=7)
        futurePlantDate     = datetime.date.today() + datetime.timedelta(days=7)
        presentPlantDate    = datetime.date.today()

        # Act
        pastPlant = Plant(plantName, plantId, pastPlantDate)
        futurePlant = Plant(plantName, plantId, futurePlantDate)
        presentPlant = Plant(plantName, plantId, presentPlantDate)

        # Assert
        #Past
        self.assertGreater(pastPlant.percentGrown, 0)
        self.assertLessEqual(pastPlant.percentGrown, 100)

        #Present
        self.assertEqual(presentPlant.percentGrown, 0)

        #Future
        self.assertEqual(futurePlant.percentGrown, 0)










if __name__ == '__main__':
    unittest.main()
